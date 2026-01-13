import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ariths_gen.wire_components import Bus
from ariths_gen.multi_bit_circuits.adders import UnsignedRca


N = 4
a = Bus("a", N)
b = Bus("b", N)

rca = UnsignedRca(a, b, prefix="")

with open("my_tests/u_rca_gen.c", "w") as f:
    rca.get_c_code_flat(f)

print("OK")