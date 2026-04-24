import sys
import os

from ariths_gen.multi_bit_circuits.adders.kogge_stone_adder import UnsignedKoggeStoneAdder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from ariths_gen.wire_components import Bus

from ariths_gen.multi_bit_circuits.multipliers.dadda_multiplier import (
    SignedDaddaMultiplier,
    UnsignedDaddaMultiplier
)

from ariths_gen.multi_bit_circuits.approximate_multipliers import (
    UnsignedApproxCompressorBasedMultiplier,
    SignedApproxCompressorBasedMultiplier
)

bus_lengths = [4, 6, 8, 10, 12, 16, 20]

signed_classes = [SignedDaddaMultiplier, SignedApproxCompressorBasedMultiplier]
unsigned_classes = [UnsignedDaddaMultiplier, UnsignedApproxCompressorBasedMultiplier]

variants = ["1StepFull", "1StepTrunc", "2StepsFull", "2StepsTrunc"]


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

adder = UnsignedKoggeStoneAdder

# SIGNED
for cls in signed_classes:
    for n in bus_lengths:

        a = Bus("a", n)
        b = Bus("b", n)

        if cls == SignedApproxCompressorBasedMultiplier:

            for var in variants:

                out_dir = f"_verilog_circuit/signed/{n}x{n}/approx"
                ensure_dir(out_dir)

                mult = cls(a, b, prefix="", variant=var, unsigned_adder_class_name=adder)

                with open(f"{out_dir}/{var}.v", "w") as f:
                    mult.get_v_code_flat(f)

        else:
            out_dir = f"_verilog_circuit/signed/{n}x{n}/exact"
            ensure_dir(out_dir)

            mult = cls(a, b, prefix="", unsigned_adder_class_name=adder)

            with open(f"{out_dir}/dadda.v", "w") as f:
                mult.get_v_code_flat(f)


# UNSIGNED
for cls in unsigned_classes:
    for n in bus_lengths:

        a = Bus("a", n)
        b = Bus("b", n)

        if cls == UnsignedApproxCompressorBasedMultiplier:

            for var in variants:

                out_dir = f"_verilog_circuit/unsigned/{n}x{n}/approx"
                ensure_dir(out_dir)

                mult = cls(a, b, prefix="", variant=var, unsigned_adder_class_name=adder)

                with open(f"{out_dir}/{var}.v", "w") as f:
                    mult.get_v_code_flat(f)

        else:
            out_dir = f"_verilog_circuit/unsigned/{n}x{n}/exact"
            ensure_dir(out_dir)

            mult = cls(a, b, prefix="", unsigned_adder_class_name=adder)

            with open(f"{out_dir}/dadda.v", "w") as f:
                mult.get_v_code_flat(f)


print("OK")