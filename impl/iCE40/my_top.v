/*
 *	(C) 2022 J. R. Sharp
 *
 *	Top level for ulx3s board
 *
 *	See LICENSE.txt for software license
 */

//`define TEST_GENERATOR

module my_top (
	input	CLK12,
	output  COMP_NEG,
	output 	reg PWM_OUT,
	input   COMP0,

	input 	SCK,
	input	MOSI,
	input	CS

);

wire clk;

SB_PLL40_PAD #(
.FEEDBACK_PATH("SIMPLE"),
		.DIVR(4'b0000),		// DIVR =  0
		.DIVF(7'b1000010),	// DIVF = 66
		.DIVQ(3'b100),		// DIVQ =  4
		.FILTER_RANGE(3'b001)	// FILTER_RANGE = 1
 ) SB_PLL40_CORE_inst (
   .RESETB(1'b1),
   .BYPASS(1'b0),
   .PACKAGEPIN(CLK12),
   .PLLOUTCORE(clk),
);


reg [15:0] count = 16'd0;

reg RSTb = 1'b0;

always @(posedge clk)
begin
	if (count < 16'd10000) 
		count <= count + 1;
	else
		RSTb <= 1'b1;
end


top sdr0 (
	clk,
	RSTb,
	COMP_NEG,
	PWM_OUT,
	COMP0,
	SCK,
	MOSI,
	CS
);


endmodule
