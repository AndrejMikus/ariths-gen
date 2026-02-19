from ariths_gen.wire_components import Bus, ConstantWireValue0
from ariths_gen.core.arithmetic_circuits import MultiplierCircuit
from ariths_gen.one_bit_circuits.one_bit_components import HalfAdder, FullAdder
from ariths_gen.multi_bit_circuits.approximative_compressors import GeneralApproxMtoNCompressor
from ariths_gen.multi_bit_circuits.adders.carry_lookahead_adder import UnsignedCarryLookaheadAdder
from ariths_gen.one_bit_circuits.logic_gates import AndGate
import math

class UnsignedApproxCompressorBasedMultiplier(MultiplierCircuit):
    def __init__(self, a: Bus, b: Bus, prefix: str = "", name: str = "u_apprx_cmpr", 
                 unsigned_adder_class_name=UnsignedCarryLookaheadAdder, type : str = "", **kwargs):

        self.N = max(a.N, b.N)
        self.type = type
        super().__init__(inputs=[a, b], prefix=prefix, name=name, out_N=self.N*2, **kwargs)

        self.a.bus_extend(N=self.N, prefix=a.prefix)
        self.b.bus_extend(N=self.N, prefix=b.prefix)


        self.h_max_next = (self.N + 1) // 2  # ceil(N/2)

        self.columns = self.init_column_heights()

        # Rearrange partial products (AND gates)
        # Each pp should appear in partial product matrix only once
        for col_idx in range(len(self.columns)):
            new_column = [self.get_column_height(col_idx)]

            for obj in self.columns[col_idx][1:]:
                if isinstance(obj, AndGate):
                    if obj.prefix not in self._prefixes:
                        self.add_component(obj)
                    new_column.append(obj.out)
                else:
                    new_column.append(obj)

            self.columns[col_idx] = new_column

        self.use_truncation = False
        self.approx_stages = None

        if self.type == "1StepFull":
            self.approx_stages = 1

        elif self.type == "2StepFull":
            self.approx_stages = 2
        
        elif self.type == "1StepTrunc":
            self.use_truncation = True
            self.approx_stages = 1

        elif self.type == "2StepTrunc":
            self.use_truncation = True
            self.approx_stages = 2

        elif self.type in ("", "General"):
            self.approx_stages = None
        


        stage = 0

        while not all(self.get_column_height(c) <= 2 for c in range(len(self.columns))): # defaultly goes to column height of two

            stage += 1
            current_max = max(self.get_column_height(c) for c in range(len(self.columns))) # maximum height of column in this stage

            self.h_max_next = math.ceil(current_max / 2)

            fa, ha, j = self.allocate_compressors()

            use_approx = ( # boolean value to decide if we use approx compressors in LSP
                self.approx_stages is None
                or stage <= self.approx_stages
            )


            for col_idx in range(len(self.columns)):
                self.connect_components(col_idx, fa[col_idx], ha[col_idx], j[col_idx], use_approx)
      

        # Final addition
        if self.N > 1:
            adder_a_wires = []
            adder_b_wires = []

            for col in range(1, len(self.columns)):
                h = self.get_column_height(col)
                adder_a_wires.append(self.add_column_wire(column=col, bit=0) if h > 0 else ConstantWireValue0())
                adder_b_wires.append(self.add_column_wire(column=col, bit=1) if h > 1 else ConstantWireValue0())

            adder_a = Bus(prefix=f"{self.prefix}_final_a", wires_list=adder_a_wires)
            adder_b = Bus(prefix=f"{self.prefix}_final_b", wires_list=adder_b_wires)

            final_adder = unsigned_adder_class_name(a=adder_a, b=adder_b, prefix=self.prefix, name=f"final_adder", inner_component=True, **kwargs)
            self.add_component(final_adder)

            [self.out.connect(i + 1, final_adder.out.get_wire(i)) for i in range(final_adder.out.N) if (i + 1) < self.out.N]
        else: 
            self.out.connect(1, ConstantWireValue0())

        # propagate the lowest bit of the partial product matrix to the output
        # we don't sum it with another bit as there is none
        self.out.connect(0, self.add_column_wire(column=0, bit=0))
        
        if self.use_truncation:
            for i in range(self.N - 1): # zero the n (half) least significant bits
                self.out.connect(i, ConstantWireValue0())


    def allocate_compressors(self):
        num_columns = len(self.columns)
        fa = [0] * num_columns
        ha = [0] * num_columns
        j = [0] * num_columns
        C = [0] * num_columns
        h_next = [0] * num_columns

        # Compute an array of column heights in the stage
        h = [self.get_column_height(col) for col in range(num_columns)]

        # Least significant part of matrix (LSP)
        for col in range(self.N):
            if h[col] <= 2:
                j[col] = 0
                h_next[col] = h[col]
            else:
                j[col] = h[col]
                h_next[col] = math.ceil(h[col]/2)

        
        # Most significant part (MSP)
        for col in range(self.N, 2*self.N - 2):
            C_prev = C[col-1] if col > 0 else 0
            c_star = math.ceil((h[col] - (self.h_max_next - C_prev)) / 2)

            if col + 2 < num_columns:
                c_max = self.h_max_next - math.ceil(h[col + 2] / 3)
            else:
                c_max = 0

            c_double_star = 2 * c_max - h[col + 1] + self.h_max_next

            if c_double_star < c_star:
                C[col] = c_double_star
                fa[col] = c_double_star
                j[col] = 2 * (h[col] - self.h_max_next - 2 * fa[col] + C_prev)

                if (j[col] == 2) and (h[col] - 3*fa[col] >= 3):
                    j[col] = 3
            
            else:
                C[col] = c_star
                if C[col] > 0:
                    fa[col] = math.ceil((h[col] - self.h_max_next + C_prev) / 2)
                    ha[col] = C[col] - fa[col]
            
            h_next[col] = h[col] - 2*fa[col] - ha[col] - math.ceil(j[col]/2) + C_prev
        return fa, ha, j
    

    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):

        # Connect full adders
        for _ in range(fa_count):
            if self.get_column_height(column_idx) < 3:
                break
            fa = FullAdder(self.add_column_wire(column=column_idx, bit=0),
                           self.add_column_wire(column=column_idx, bit=1),
                           self.add_column_wire(column=column_idx, bit=2),
                           prefix=f"{self.prefix}_fa_{column_idx}_{self.get_instance_num(cls=FullAdder)}")
            self.add_component(fa)
            self.update_column_heights(curr_column=column_idx, curr_height_change=-2, next_column=column_idx + 1, next_height_change=1)
            self.update_column_wires(curr_column=column_idx, next_column=column_idx + 1, adder=fa)


        # Connect half adders
        for _ in range(ha_count):
            if self.get_column_height(column_idx) < 2:
                break
            ha = HalfAdder(self.add_column_wire(column=column_idx, bit=0),
                           self.add_column_wire(column=column_idx, bit=1),
                           prefix=f"{self.prefix}_ha_{column_idx}_{self.get_instance_num(cls=HalfAdder)}")
            self.add_component(ha)
            self.update_column_heights(curr_column=column_idx, curr_height_change=-1, next_column=column_idx + 1, next_height_change=1)
            self.update_column_wires(curr_column=column_idx, next_column=column_idx + 1, adder=ha)

        current_height = self.get_column_height(column_idx)

        if use_approx: # use approximative compressors in this reduction stage
            j = min(j, current_height)
            
            
            # Connect approximative compressors
        
            wires_to_compress = [
                self.add_column_wire(column=column_idx, bit=i)
                for i in range(j)
            ]

            compressor_in_bus = Bus(prefix=f"{self.prefix}_compr_in_{column_idx}_{self.get_instance_num(cls=GeneralApproxMtoNCompressor)}", wires_list=wires_to_compress)
            
            compressor = GeneralApproxMtoNCompressor(a=compressor_in_bus, prefix=f"{self.prefix}_compr_{column_idx}_{self.get_instance_num(cls=GeneralApproxMtoNCompressor)}", inner_component=True)
            self.add_component(compressor)

            self.update_column_heights(curr_column=column_idx, curr_height_change=-(j - compressor.out.N))
            
            
            [self.columns[column_idx].pop(1) for _ in range(j)]
            [self.columns[column_idx].insert(len(self.columns[column_idx]), compressor.out.get_wire(i)) for i in range(compressor.out.N)]
        
        else:   # no use of approx. compressors in this stage
                # use of half and full adders instead
            while self.get_column_height(column_idx) > 2:
                if self.get_column_height(column_idx) >= 3:
                    fa = FullAdder(
                        self.add_column_wire(column=column_idx, bit=0),
                        self.add_column_wire(column=column_idx, bit=1),
                        self.add_column_wire(column=column_idx, bit=2),
                        prefix=f"{self.prefix}_fa_exact_{column_idx}_{self.get_instance_num(cls=FullAdder)}"
                    )
                    self.add_component(fa)
                    self.update_column_heights(
                        curr_column=column_idx,
                        curr_height_change=-2,
                        next_column=column_idx + 1,
                        next_height_change=1
                    )
                    self.update_column_wires(
                        curr_column=column_idx,
                        next_column=column_idx + 1,
                        adder=fa
                    )
                else:
                    break