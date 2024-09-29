# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 ns (100 MHz)
    clock = Clock(dut.clk, 10, units="ns")
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

    # Do SPI commands to write in frequency to demodulate with

    await ClockCycles(dut.clk, 10)

    freq = 0x995aa | (2 << 26)

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

    await ClockCycles(dut.clk, 500)

    fil = open("1bit_rf.txt")
    data = fil.readlines()


    #for data in data[0:1000000]:
    for data in data[0:100000]:
        bit = int(data)
        dut.ui_in.value = bit | 0xe 
        # Wait for one clock cycle to see the output values
        await ClockCycles(dut.clk, 1)

    # The following assersion is just an example of how to check the output values.
    # Change it to match the actual expected output of your module:
    #assert dut.uo_out.value == 50

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
