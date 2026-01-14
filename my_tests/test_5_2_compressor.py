import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ariths_gen.wire_components import Bus, Wire
from ariths_gen.multi_bit_circuits.exact_compressors import FiveToTwoCompressor

N = 7
a = Bus("a", N)

five_two_cmprs = FiveToTwoCompressor(a, prefix="")

with open("my_tests/five_two_cmprs_gen.c", "w") as f:
    five_two_cmprs.get_c_code_flat(f)

print("OK")