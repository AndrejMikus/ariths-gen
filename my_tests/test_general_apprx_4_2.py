import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ariths_gen.wire_components import Bus, Wire
from ariths_gen.multi_bit_circuits.approximative_compressors import (
    LowerOrderApproxMtoNCompressor,
    GeneralApproxMtoNCompressor
    )

N = 8
a = Bus("a", N)

approx_4_2_cmprs = GeneralApproxMtoNCompressor(a, prefix="")

with open("my_tests/general_approx_4_2_cmprs_gen.c", "w") as f:
    approx_4_2_cmprs.get_c_code_hier(f)

print("OK")