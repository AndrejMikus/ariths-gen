import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ariths_gen.wire_components import Bus
from ariths_gen.multi_bit_circuits.approximate_multipliers.compressor_multiplier import (
    UnsignedApproxCompressorBasedMultiplier
)

M = 10
N = 10

a = Bus("a", M)
b = Bus("b", N)

compr_mult = UnsignedApproxCompressorBasedMultiplier(a, b, prefix="")

with open("my_tests/u_compr_mult_gen.c", "w") as f:
    compr_mult.get_c_code_flat(f)

print("OK")