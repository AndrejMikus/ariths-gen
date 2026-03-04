import os
import sys
import itertools
from math import ceil
from fractions import Fraction

# Add the parent directory to the system path
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DIR_PATH, '..'))


from ariths_gen.wire_components import Bus
from ariths_gen.multi_bit_circuits.approximative_compressors.general_approx_compressor import (
    LowerOrderApproxMtoNCompressor,
    GeneralApproxMtoNCompressor
)

P_ONE  = Fraction(1, 4)   # Probability that product of multiplication of 2 bits is ONE
P_ZERO = Fraction(3, 4)   # Probability that product is ZERO

# Setting colors for the final table
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET_COLOR = "\033[0m"



def compute_error_probability(bitvec):
    """
        Computes probability that there can be an input with `bitvec` bit sequence.
    """
    prob = Fraction(1, 1)
    for b in bitvec:
        if b == 1:
            prob *= P_ONE
        else:
            prob *= P_ZERO
    return prob


def test_lower_order_compressor(N):
    """
        Tests lower order compressor.
        Prints result table on stdout.
        TODO: Add some asserts (so there isno need to look up 
            correct values in the paper)
    """
    print(f"\n======================== {N} : {ceil(N/2)} compressor ========================")
    bits = tuple(f"p{i}" for i in reversed(range(N)))
    print(f"{'\t'.join(map(str, bits))} |\tS\tS_APP\tErr_i\tP(Err_i)")

    for bitvec in itertools.product([0, 1], repeat=N):

        bus = Bus(N=N, prefix="a")
        prefix = f"test_{N}_{''.join(map(str, bitvec))}"
        comp = LowerOrderApproxMtoNCompressor(a=bus, prefix=prefix)

        # Convert bit vector to integer input
        input_val = 0
        for bit in reversed(bitvec):
            input_val = (input_val << 1) | bit

        out_val = comp(input_val)

        # Sum of output bits (count 1s)
        S_APP = bin(out_val).count('1')
        S = sum(bitvec)

        Err_i = S - S_APP

        # Probability of error for the input vector
        p = compute_error_probability(bitvec)

        print(f"{'\t'.join(map(str, bitvec))}  |\t"
        f"{GREEN}{S}\t{RESET_COLOR}"
        f"{YELLOW}{S_APP}\t{RESET_COLOR}"
        f"{RED}{Err_i}\t{RESET_COLOR}"
        f"{CYAN}{p if Err_i != 0 else '-'}{RESET_COLOR}")

for N in range(2, 7):
    test_lower_order_compressor(N)
