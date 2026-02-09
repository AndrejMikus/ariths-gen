from ariths_gen.one_bit_circuits.logic_gates import (
    NorGate,
    XnorGate,
    NotGate,
    OrGate,
    AndGate,
)

from ariths_gen.wire_components import Bus

from ariths_gen.core.arithmetic_circuits import GeneralCircuit

from math import ceil


class ApproxMtoNCompressor(GeneralCircuit):
    def __init__(self, a: Bus, prefix="", name="approx_M_N_cmprs", **kwargs):
        self.N = a.N
        self.M = (self.N + 1) // 2 # ceil(N/2)

        super().__init__(
            inputs=[a],
            name=name,
            prefix=prefix,
            out_N=self.M,
            **kwargs
        )

        self.create_compressor()
        
        
    def pair_p_products(self):
        pairs = []
        for i in range(0, self.N, 2):
            wire0 = self.a.get_wire(i)
            wire1 = self.a.get_wire(i + 1) if (i + 1 < self.N) else None
            pairs.append((wire0, wire1))

        return pairs
    

    def create_and_or_pairs(self, pairs):
        and_outputs_list =  []
        or_outputs_list = []

        for i, (w0, w1) in enumerate(pairs):
            if w1 is None:
                # standalone partial product
                or_outputs_list.append(w0)
            else:
                and_gate = AndGate(w0, w1, prefix=f"and_{i}")
                or_gate = OrGate(w0, w1, prefix=f"or_{i}")

                self.add_component(and_gate)
                self.add_component(or_gate)

                and_outputs_list.append(and_gate.out)
                or_outputs_list.append(or_gate.out)

        return and_outputs_list, or_outputs_list
    
    def recode_and_or(self, and_list, or_list):
        outputs = []

        or_count = len(or_list)

        for i in range(or_count):
            a_i = and_list[i] if i < len(and_list) else None
            next_or_gate = or_list[(i + 1) % or_count]

            if a_i is None:
                # unpaired partial product
                outputs.append(next_or_gate)
            else:
                or_gate = OrGate(a_i, next_or_gate, prefix=f"out_{i}")
                self.add_component(or_gate)
                outputs.append(or_gate.out)

        return outputs
        
    def create_compressor(self):
        pairs = self.pair_p_products()
        and_list, or_list = self.create_and_or_pairs(pairs)
        outs = self.recode_and_or(and_list, or_list)

        for out_pin, wire_out in enumerate(outs):
            self.out.connect(out_pin, wire_out)