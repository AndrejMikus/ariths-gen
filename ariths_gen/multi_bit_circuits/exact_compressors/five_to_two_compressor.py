from ariths_gen.one_bit_circuits.one_bit_components import (
    FullAdder
)

from ariths_gen.wire_components import (
    Bus
)

from ariths_gen.core.arithmetic_circuits import (
    GeneralCircuit
)

from ariths_gen.multi_bit_circuits.exact_compressors import (
    FourToTwoCompressor
)

"""
    ```
            X1 X2 X3                   
            │  │  │                    
            │  │  │                    
         ┌──▼──▼──▼──┐                 
         │           │                 
  ┌──────┤    FA     │                 
  │      │           │    X4 Cin1      
  │      └─────────┬─┘     │  │        
  │                │       │  │        
  ▼                │  ┌────┘  │        
Cout1              │  │   ┌───┘        
                   │  │   │            
                ┌──▼──▼───▼─┐          
                │           │          
        ┌───────┤    FA     │          
        │       │           │          
        │       └──────────┬┘  X5  Cin2
        │                  │    │   │  
        ▼                  │  ┌─┘   │  
      Cout2                │  │   ┌─┘  
                           │  │   │    
                         ┌─▼──▼───▼──┐ 
                         │           │ 
                         │    FA     │ 
                         │           │ 
                         └───┬────┬──┘ 
                             │    │    
                             ▼    ▼    
                           Carry  Sum  
    ```
"""

class FiveToTwoCompressor(GeneralCircuit):
    def __init__(self, a: Bus, prefix: str = "", name: str = "cmprss_5_2", **kwargs):
        assert a.N == 7 # X1, X2, X3, X4, X5, Cin1, Cin2
        self.N = a.N

        super().__init__(inputs=[a], name=name, prefix=prefix, out_N=4, **kwargs)

        # X1, X2, X3
        fa1_inputs = [self.a.get_wire(i) for i in [4, 3, 2]]
        fa1 = FullAdder(*fa1_inputs, prefix="fa1")
        self.add_component(fa1)

        # fa1_SUM, X4, Cin1
        fa2_inputs = [self.a.get_wire(5), fa1.get_sum_wire(), self.a.get_wire(1)]
        fa2 = FullAdder(*fa2_inputs, prefix="fa2")
        self.add_component(fa2)

        fa3_inputs = [self.a.get_wire(6), fa2.get_sum_wire(), self.a.get_wire(0)]
        fa3 = FullAdder(*fa3_inputs, prefix="fa3")
        self.add_component(fa3)


        self.out.connect(0, fa3.get_sum_wire()) #SUM
        self.out.connect(1, fa3.get_carry_wire()) #CARRY
        self.out.connect(2, fa1.get_carry_wire()) #COUT1
        self.out.connect(3, fa2.get_carry_wire()) #COUT2

