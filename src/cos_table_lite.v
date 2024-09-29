module cosTable(input clk, input [3:0] addr, output reg [7:0] data);
reg [7:0] mem [0:15];
initial mem[0] = 8'h7f;
initial mem[1] = 8'h75;
initial mem[2] = 8'h59;
initial mem[3] = 8'h30;
initial mem[4] = 8'h0;
initial mem[5] = 8'hd0;
initial mem[6] = 8'ha7;
initial mem[7] = 8'h8b;
initial mem[8] = 8'h81;
initial mem[9] = 8'h8b;
initial mem[10] = 8'ha7;
initial mem[11] = 8'hd0;
initial mem[12] = 8'h0;
initial mem[13] = 8'h30;
initial mem[14] = 8'h59;
initial mem[15] = 8'h75;
always @(posedge clk) begin
	data <= mem[addr];
end
endmodule
