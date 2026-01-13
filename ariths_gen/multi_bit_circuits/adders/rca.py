from ariths_gen.one_bit_circuits.one_bit_components import FullAdder, HalfAdder
from ariths_gen.wire_components import Bus
from ariths_gen.core.arithmetic_circuits import GeneralCircuit

class UnsignedRca(GeneralCircuit):
    def __init__(self, a: Bus, b: Bus, name: str = "u_rca", prefix: str = "", **kwargs):
        self.N = max(a.N, b.N)
        super().__init__(inputs=[a, b], prefix=prefix, name=name, out_N=self.N+1, **kwargs)

        self.a.bus_extend(self.N, prefix=a.prefix)
        self.b.bus_extend(self.N, prefix=b.prefix)

        for index in range(self.N):
            if index == 0:
                adder = HalfAdder(self.a.get_wire(index), self.b.get_wire(index), prefix=self.prefix+"_ha")
            else:
                adder = FullAdder(self.a.get_wire(index), self.b.get_wire(index), self.get_previous_component().get_carry_wire(), prefix=self.prefix+"_fa"+str(index))

            self.add_component(adder)
            self.out.connect(index, adder.get_sum_wire())

            if index == (self.N-1):
                self.out.connect(self.N, adder.get_carry_wire())