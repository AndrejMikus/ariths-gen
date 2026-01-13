from ariths_gen.core.one_bit_circuits import TwoInputOneBitCircuit
from ariths_gen.one_bit_circuits.logic_gates import XorGate, AndGate
from ariths_gen.wire_components import Wire, Bus

class MyHalfAdder(TwoInputOneBitCircuit):

    use_verilog_instance = False

    def __init__(self, a: Wire = Wire(name="a"), b: Wire = Wire(name="b"), prefix: str = "", name: str = ""):
        super().__init__(a, b, prefix=prefix, name=name)
        self.out = Bus(self.prefix+"_out", 2)

        xor1 = XorGate(a, b, prefix=self.prefix+"_xor")
        self.add_component(xor1)
        self.out.connect(0, xor1.out)

        and1 = AndGate(a, b, prefix=self.prefix+"_and")
        self.add_component(and1)
        self.out.connect(1, and1.out)


    def get_sum_wire(self):
        return self.out.get_wire(0)
    
    def get_carry_wire(self):
        return self.out.get_wire(1)
    
