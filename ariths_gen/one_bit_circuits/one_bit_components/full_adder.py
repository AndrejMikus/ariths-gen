from ariths_gen.core.one_bit_circuits import ThreeInputOneBitCircuit
from ariths_gen.one_bit_circuits.logic_gates import AndGate, XorGate, OrGate
from ariths_gen.wire_components import Wire, Bus

class MyFullAdder(ThreeInputOneBitCircuit):

    use_verilog_instance = False

    def __init__(self, a: Wire = Wire(name="a"), b: Wire = Wire(name="b"), c: Wire = Wire(name="c"), prefix: str = "", name: str = ""):
        super().__init__(a, b, c, prefix=prefix, name=name)
        self.out = Bus(self.prefix+"_out", 2)

        xor1 = XorGate(a, b, prefix=self.prefix+"_xor1")
        self.add_component(xor1)
        

        and1 = AndGate(a, b, prefix=self.prefix+"_and1")
        self.add_component(and1)

        xor2 = XorGate(xor1.out, c, prefix=self.prefix+"_xor2")
        self.add_component(xor2)
        self.out.connect(0, xor2.out)

        and2 = AndGate(c, xor1.out, prefix=self.prefix+"_and2")
        self.add_component(and2)

        or1 = OrGate(and1.out, and2.out, prefix=self.prefix+"_or")
        self.add_component(or1)
        self.out.connect(1, or1.out)

