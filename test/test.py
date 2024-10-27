# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

import numpy as np


from scipy.signal import butter, lfilter
from scipy.signal import freqs
from scipy import fft

def butter_bandpass(cutOffLow, cutOff, fs, order=5):
    b, a = butter(order, (cutOffLow, cutOff), fs = fs, btype='band', analog = False)
    return b, a

def butter_bandpass_filter(data, cutOffLow, cutOff, fs, order=4):
    b, a = butter_bandpass(cutOffLow, cutOff, fs, order=order)
    y = lfilter(b, a, data)
    return y



async def test_am_freq(dut, gen_freq, mod_freq, clock_freq):

    # Do SPI commands to write in frequency to demodulate with

    await ClockCycles(dut.clk, 10)

    freq = int((1<<26) * mod_freq / clock_freq) | (2 << 26)

    # Deassert chip select
    dut.ui_in.value = 0xe

    await ClockCycles(dut.clk, 10)

    # Asset chip select
    dut.ui_in.value = 0x6

    await ClockCycles(dut.clk, 10)

    for i in range(0, 32):
        bit = 0
        if freq & (1 << (31 - i)) != 0:
            bit |= 2
        dut.ui_in.value = bit
        await ClockCycles(dut.clk, 10)
        dut.ui_in.value = bit | 4
        await ClockCycles(dut.clk, 10)

    await ClockCycles(dut.clk, 10)

    # Deassert chip select
    dut.ui_in.value = 0xe

    await ClockCycles(dut.clk, 200)

    # Create modulated data
    t = np.linspace(0, 0.01, 500)
    data = 32768.0 * np.sin(2*np.pi*gen_freq*t)
    audioSampleRate = 50000

    sampleRate = int(clock_freq)
    carrier = int(mod_freq)

    #print(audioSampleRate)
    #print(sampleRate // audioSampleRate)

    interp = int(sampleRate // audioSampleRate)

    _data = []

    phase = 0
    for l in data:
        #print (l)
        phase_arr = np.zeros(interp)
        for i in range(0, interp):
            phase_arr[i] = phase
            phase += carrier / sampleRate
        mod = (0.7 + 0.3*(l / 32768.0)) * np.cos(2*np.pi*phase_arr)
        mod += np.random.normal(0,0.5,interp)
        #plt.plot(mod)
        #plt.show()
        one_bit = np.sign(mod)
        for bit in one_bit:
            if bit < 0:
                _data.append(0)
            else:
                _data.append(1)


    #for data in data[0:1000000]:
    prev_bit = [0, 0, 0, 0]
    nu_bit = 0

    i = 0

    pwm_dat = []

    for data in _data[0:300000]:
        i += 1
        bit = int(data)
        dut.ui_in.value = bit | 0xe 
        # Wait for one clock cycle to see the output values
        await ClockCycles(dut.clk, 1)
        
        for j in reversed(range(0, 3)):
            prev_bit[j+1] = prev_bit[j]
        prev_bit[0] = bit
        nu_bit = dut.uo_out.value & 1

        pwm_dat.append(dut.uo_out.value & 2) 

        if (i > 100):
            assert prev_bit[3] == nu_bit  # Check that the output to comparator filter is delayed version of input

    # The following assersion is just an example of how to check the output values.
    # Change it to match the actual expected output of your module:
    #assert dut.uo_out.value == 50

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.

    # Test generated frequency

    # Lowpass filter the pwm_dat

    #from matplotlib import pyplot as plt

    y = butter_bandpass_filter(pwm_dat, 500, 5000, clock_freq, 2)
    #plt.plot(y)
    #plt.show()

    # Decimate to 100kHz sampling rate

    decim = int(clock_freq // 100000)

    #print("Decim = {}".format(decim))

    # Skip the first 100k samples as this is the decimation filters (CICs) warming up
    yy = y[100000::decim]

    #plt.plot(yy)
    #plt.show()

    f = fft.fft(yy)

    #plt.plot(np.absolute(f))
    #plt.show()

    # Find argmax
    freq_i = np.argmax(np.abs(f[:len(f)//2]))
    freq = (freq_i / len(f)) * 1e5

    dut._log.info("RX tone: {} Hz".format(freq))

    assert freq < gen_freq * 1.2
    assert freq > gen_freq * 0.8

    


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    
    clock_per = 20
    clock_freq = 1.0 / (clock_per * 1.e-9)

    clock = Clock(dut.clk, 20, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test project behavior")

    # Set the input values you want to test
    #dut.ui_in.value = 20
    #dut.uio_in.value = 30

    dut._log.info("Test 1kHz AM, 936kHz carrier")
    await test_am_freq(dut, 1000, 936000, clock_freq) 

    dut._log.info("Test 2kHz AM, 747kHz carrier")
    await test_am_freq(dut, 2000, 747000, clock_freq) 

    dut._log.info("Test 3kHz AM, 585kHz carrier")
    await test_am_freq(dut, 3000, 585000, clock_freq) 

    dut._log.info("Test 1.5kHz AM, 7MHz carrier")
    await test_am_freq(dut, 1500, 7000000, clock_freq) 




