from ariths_gen.one_bit_circuits.logic_gates import (
    XorGate
)

from ariths_gen.one_bit_circuits.one_bit_components import (
    FullAdder,
    HalfAdder
)

from ariths_gen.wire_components import (
    Bus
)

from ariths_gen.core.arithmetic_circuits import (
    GeneralCircuit
)

"""
    Uses design M-4 from https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10690038

"""

class ApproxFiveTwoCompressor(GeneralCircuit):
    def __init__(self, a: Bus, prefix: str = "", name: str = "approx_5_2_cmprs", **kwargs):
        assert a.N == 5
        self.N = a.N

        super().__init__(inputs=[a], name=name, prefix=prefix, out_N=3, **kwargs)

        fa_inputs = [self.a.get_wire(i) for i in [4, 3, 2]]
        ha1_inputs = [self.a.get_wire(i) for i in [1, 0]]

        fa = FullAdder(*fa_inputs, prefix="fa")
        self.add_component(fa)

        ha1 = HalfAdder(*ha1_inputs, prefix="ha1")
        self.add_component(ha1)

        ha2 = HalfAdder(fa.get_carry_wire(), ha1.get_carry_wire(), prefix="ha2")
        self.add_component(ha2)

        xor_sum = XorGate(fa.get_sum_wire(), ha1.get_sum_wire(), prefix="xor_sum")
        self.add_component(xor_sum)


        self.out.connect(0, xor_sum.out) # Sum
        self.out.connect(1, ha2.get_sum_wire()) # C1
        self.out.connect(2, ha2.get_carry_wire()) #C2