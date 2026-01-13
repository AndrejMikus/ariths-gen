import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ariths_gen.one_bit_circuits.one_bit_components import MyFullAdder
from ariths_gen.wire_components import Wire

a = Wire(name="a")
b = Wire(name="b")
c = Wire(name="c")

fa = MyFullAdder(a, b, c, prefix="fa")

with open("my_tests/fa_gen.c", "w") as f:
    fa.get_c_code_flat(f)

print("OK")