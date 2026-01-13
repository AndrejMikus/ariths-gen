import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ariths_gen.one_bit_circuits.one_bit_components import MyHalfAdder
from ariths_gen.wire_components import Wire

a = Wire(name="a")
b = Wire(name="b")

ha = MyHalfAdder(a, b, prefix="ha")

with open("my_tests/ha_gen.c", "w") as f:
    ha.get_c_code_flat(f)

print("OK")