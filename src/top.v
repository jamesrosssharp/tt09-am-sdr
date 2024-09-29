/*
 *	(C) 2022 J. R. Sharp
 *
 *	Top level for ulx3s board
 *
 *	See LICENSE.txt for software license
 */

module top (
	input	clk,
	input	RSTb,
	output  COMP_OUT,
	output 	reg PWM_OUT,
	input   COMP_IN,

	input 	SCK,
	input	MOSI,
	input	CS

);


wire [25:0] phase_inc;
wire [3:0]  gain_spi;

spi spi0
(
    clk,
    RSTb,
    MOSI,
    SCK,
    CS,

    phase_inc,
    gain_spi

);

// NCO

wire [7:0] sin;
wire [7:0] cos;

nco_sq nco0
(
	clk,
	RSTb,

	phase_inc,

	sin,
	cos
);

// Sample and RF Down convert

wire RF_out;
assign COMP_OUT =  RF_out;

wire [7:0] I_out;
wire [7:0] Q_out;

mixer_2b
mix0 
(
	clk,
	RSTb,

	COMP_IN,
	RF_out,

	sin,
	cos,

	I_out,
	Q_out	
);

// Instantiate CIC

wire [15:0] xI_out;
wire [15:0] xQ_out;
wire out_tickI;
wire out_tickQ;

wire [15:0] xI_out2;
wire [15:0] xQ_out2;
wire out_tickI_2;
wire out_tickQ_2;

cic_lite cic0
(
	clk,
	RSTb,
	1'b1,
	I_out,
	xI_out,
	out_tickI
);

cic_lite cic1
(
	clk,
	RSTb,
	1'b1,
	Q_out,
	xQ_out,
	out_tickQ
);

cic_lite cic2
(
	clk,
	RSTb,
	out_tickI,
	xI_out[15:8],
	xI_out2,
	out_tickI_2
);

cic_lite cic3
(
	clk,
	RSTb,
	out_tickQ,
	xQ_out[15:8],
	xQ_out2,
	out_tickQ_2
);

wire out_tick;
wire [15:0] demod_out;

am_demod_lite am0 
(
	clk,
	RSTb,

	xI_out2[15:8],
	xQ_out2[15:8],
	out_tickI_2,	/* tick should go high when new sample is ready */

	demod_out,
	out_tick	/* tick will go high when the new AM demodulated sample is ready */

);

reg [7:0] count; 

always @(posedge clk) begin
	if (RSTb == 1'b0) begin
		count <= 8'd0;
		PWM_OUT <= 1'b0;
	end else begin
		count <= count + 1;
		case (gain_spi[2:0])
			3'b000:
				PWM_OUT <= (count < demod_out[15:8]) ? 1'b1 : 1'b0;
			3'b001:
				PWM_OUT <= (count < demod_out[14:7]) ? 1'b1 : 1'b0;
			3'b010:
				PWM_OUT <= (count < demod_out[13:6]) ? 1'b1 : 1'b0;
			3'b011:
				PWM_OUT <= (count < demod_out[12:5]) ? 1'b1 : 1'b0;
			3'b100:	
				PWM_OUT <= (count < demod_out[11:4]) ? 1'b1 : 1'b0;
			default:	
				PWM_OUT <= (count < demod_out[10:3]) ? 1'b1 : 1'b0;
		endcase
	end	
end

//always @(posedge clk) PWM_OUT <= (count < phase_inc[7:0]) ? 1'b1 : 1'b0;


endmodule
