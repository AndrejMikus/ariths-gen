from ariths_gen.one_bit_circuits.logic_gates import (
    NorGate,
    XnorGate,
    NotGate, 
    OrGate, 
    AndGate
)

from ariths_gen.wire_components import (
    Bus
)

from ariths_gen.core.arithmetic_circuits import (
    GeneralCircuit
)



"""
Uses design of ACC-3 from https://doi.org/10.1007/s10836-022-06019-6

```
┌─────┐                                              
│     │                                              
│ OR  ├─────┐                                        
│     │     │                                        
│     │     │                                        
└─────┘     │                                        
            │    ┌─────┐                             
            └────►     │                             
                 │ AND ├───┬──────────────────► Carry
                 │     │   │                         
            ┌────►     │   │                         
            │    └─────┘   │                         
┌─────┐     │              │                         
│     │     │              │        ┌─────┐          
│ OR  ├─────┘              │        │     │          
│     │                    └────────► NOT ├───► Sum  
│     │                             │     │          
└─────┘                             │     │          
                                    └─────┘          
```

"""
class ApproxFourTwoCompressor(GeneralCircuit):
    def __init__(self, a: Bus, prefix: str = "", name: str = "approx_4_2_cmprs", **kwargs):
        assert a.N == 4
        self.N = a.N

        super().__init__(inputs=[a], name=name, prefix=prefix, out_N=2, **kwargs)

        upper_bits = [self.a.get_wire(0), self.a.get_wire(1)] #X3, X4
        lower_bits = [self.a.get_wire(2), self.a.get_wire(3)] #X1, X2

        upper_or = OrGate(*upper_bits, prefix="upper_or")
        self.add_component(upper_or)

        lower_or = OrGate(*lower_bits, prefix="lower_or")
        self.add_component(lower_or)

        carry = AndGate(upper_or.out, lower_or.out, prefix="carry_and")
        self.add_component(carry)

        # sum output is negated carry output
        sum = NotGate(carry.out, prefix="sum_not")
        self.add_component(sum)

        self.out.connect(0, sum.out)
        self.out.connect(1, carry.out)

