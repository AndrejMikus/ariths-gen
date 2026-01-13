from ariths_gen.one_bit_circuits.one_bit_components import (
    FullAdder
)

from ariths_gen.wire_components import (
    Bus
)

from ariths_gen.core.arithmetic_circuits import (
    GeneralCircuit
)

"""
    ```

          X1 X2 X3    X4
          │  │  │     │
        ┌─▼──▼──▼─┐   │
        │         │   │
   ┌────┤   FA    │   │
   │    │         │   │
   │    └─┬───────┘   │
   │      │  ┌────────┘
   ▼      │  │  ┌────────── Cin       
  Cout  ┌─▼──▼──▼─┐
        │         │
        │   FA    │
        │         │
        └──┬───┬──┘
           ▼   ▼
        Carry  Sum

    ```
"""

class FourToTwoCompressor(GeneralCircuit):
    def __init__(self, a: Bus, prefix: str = "", name: str = "cmprss_4_2", **kwargs):
        assert a.N == 5
        self.N = a.N

        # the commpressor has 3 outputs: sum, carry and cout
        super().__init__(inputs=[a], name=name, prefix=prefix, out_N=3, **kwargs)
        # input wires for first FA are X3, X2 and X1
        fa1_input = [self.a.get_wire(i) for i in [3, 2, 1]]

        fa1 = FullAdder(*fa1_input, prefix=prefix+"_fa1")
        self.add_component(fa1)
        
        fa2 = FullAdder(fa1.get_sum_wire(), self.a.get_wire(0), self.a.get_wire(4))
        self.add_component(fa2)

        # SUM is the sum output from the second FA
        self.out.connect(0, fa2.get_sum_wire())
        # CARRY is the carry output from the second FA
        self.out.connect(1, fa2.get_carry_wire())

        # COUT is the carry output from the first FA
        self.out.connect(2, fa1.get_carry_wire())

    def get_carry_wire(self):
        return self.out.get_wire(1)
    
    def get_cout_wire(self):
        return self.out.get_wire(2)