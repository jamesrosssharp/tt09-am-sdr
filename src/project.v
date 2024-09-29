/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_jamesrosssharp_1bitam (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // All output pins must be assigned. If not used, assign to 0.
  assign uio_out = 0;
  assign uio_oe  = 0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, ui_in[7:4], uio_in, 1'b0};

/*  ui[0]: "COMP_IN"
  ui[1]: "SPI_MOSI"
  ui[2]: "SPI_SCK"
  ui[3]: "SPI_CSb"
  ui[4]: ""
  ui[5]: ""
  ui[6]: ""
  ui[7]: ""

  # Outputs
  uo[0]: "COMP_OUT"
  uo[1]: "PWM"
  uo[2]: ""
  uo[3]: ""
  uo[4]: ""
  uo[5]: ""
  uo[6]: ""
  uo[7]: ""
*/

wire COMP_OUT;
wire PWM_OUT;
wire COMP_IN;
wire SCK;
wire MOSI;
wire CSb;

assign COMP_IN  = ui_in[0];
assign MOSI 	= ui_in[1];
assign SCK  	= ui_in[2];
assign CSb	= ui_in[3];

assign uo_out[0] 	= COMP_OUT;
assign uo_out[1] 	= PWM_OUT;
assign uo_out[7:2] 	= 6'd0;

top am_sdr0 (
	clk,
	rst_n,
	COMP_OUT,
	PWM_OUT,
	COMP_IN,

	SCK,
	MOSI,
	CSb

);

endmodule
