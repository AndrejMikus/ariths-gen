import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ariths_gen.wire_components import Bus

from ariths_gen.multi_bit_circuits.adders import (
    UnsignedKoggeStoneAdder,
    UnsignedRippleCarryAdder,
    UnsignedCarryLookaheadAdder,
    UnsignedBrentKungAdder,
)

from ariths_gen.multi_bit_circuits.multipliers import (
    UnsignedDaddaMultiplier,
    SignedDaddaMultiplier,
)

from ariths_gen.multi_bit_circuits.approximate_multipliers import (
    UnsignedApproxCompressorBasedMultiplier,
    SignedApproxCompressorBasedMultiplier,
    UnsignedQuarterApproxCompressorMultiplier,
    SignedQuarterApproxCompressorMultiplier,
    UnsignedThresholdApproxCompressorMultiplier,
    SignedThresholdApproxCompressorMultiplier,
    UnsignedApproxGreedyPredefinedCompressorBWMultiplier,
    SignedApproxGreedyPredefinedCompressorBWMultiplier,
    UnsignedThresholdGreedyPredefinedBWApproxCompressorMultiplier,
    SignedThresholdGreedyPredefinedBWApproxCompressorMultiplier,
    UnsignedApproxBalancedPredefinedBWCompressorMultiplier,
    SignedApproxBalancedPredefinedBWCompressorMultiplier,
    UnsignedThresholdBalancedPredefinedBWApproxCompressorMultiplier,
    SignedThresholdBalancedPredefinedBWApproxCompressorMultiplier,
)

bus_lengths = [4, 6, 8, 10, 12, 16, 20]

variants = ["1StepFull", "1StepTrunc", "2StepsFull", "2StepsTrunc"]
thresholds = [0.25, 0.40, 0.50, 0.60, 0.75]
compressor_bws = [3, 4, 5]

adder_classes = {
    "kogge_stone": UnsignedKoggeStoneAdder,
    "ripple_carry": UnsignedRippleCarryAdder,
    "carry_lookahead": UnsignedCarryLookaheadAdder,
    "brent_kung": UnsignedBrentKungAdder,
}

multiplier_groups = {
    "basic": {
        "unsigned": UnsignedApproxCompressorBasedMultiplier,
        "signed": SignedApproxCompressorBasedMultiplier,
    },
    "quarter": {
        "unsigned": UnsignedQuarterApproxCompressorMultiplier,
        "signed": SignedQuarterApproxCompressorMultiplier,
    },
    "threshold": {
        "unsigned": UnsignedThresholdApproxCompressorMultiplier,
        "signed": SignedThresholdApproxCompressorMultiplier,
    },
    "predefined_bw_greedy": {
        "unsigned": UnsignedApproxGreedyPredefinedCompressorBWMultiplier,
        "signed": SignedApproxGreedyPredefinedCompressorBWMultiplier,
    },
    "threshold_predefined_bw_greedy": {
        "unsigned": UnsignedThresholdGreedyPredefinedBWApproxCompressorMultiplier,
        "signed": SignedThresholdGreedyPredefinedBWApproxCompressorMultiplier,
    },
    "predefined_bw_balanced": {
        "unsigned": UnsignedApproxBalancedPredefinedBWCompressorMultiplier,
        "signed": SignedApproxBalancedPredefinedBWCompressorMultiplier,
    },
    "threshold_predefined_bw_balanced": {
        "unsigned": UnsignedThresholdBalancedPredefinedBWApproxCompressorMultiplier,
        "signed": SignedThresholdBalancedPredefinedBWApproxCompressorMultiplier,
    },
    "exact": {
        "unsigned": UnsignedDaddaMultiplier,
        "signed": SignedDaddaMultiplier,
    },
}


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def generate_and_store(multiplier_cls, a, b, adder_cls, out_file, **kwargs):
    circuit = multiplier_cls(
        a,
        b,
        prefix="",
        unsigned_adder_class_name=adder_cls,
        **kwargs,
    )
    with open(out_file, "w") as file_obj:
        circuit.get_v_code_flat(file_obj)


for signedness in ["unsigned", "signed"]:
    for n in bus_lengths:
        a = Bus("a", n)
        b = Bus("b", n)

        for group_name, group_classes in multiplier_groups.items():
            multiplier_cls = group_classes[signedness]

            for adder_name, adder_cls in adder_classes.items():
                out_dir = f"_verilog_circuit/{signedness}/{n}x{n}/{group_name}/{adder_name}"
                ensure_dir(out_dir)

                if group_name == "exact":
                    out_file = f"{out_dir}/exact.v"
                    generate_and_store(
                        multiplier_cls,
                        a,
                        b,
                        adder_cls,
                        out_file,
                    )

                elif group_name in ["basic", "quarter"]:
                    for variant in variants:
                        out_file = f"{out_dir}/{variant}.v"
                        generate_and_store(
                            multiplier_cls,
                            a,
                            b,
                            adder_cls,
                            out_file,
                            variant=variant,
                        )

                elif group_name == "threshold":
                    for threshold in thresholds:
                        threshold_tag = str(threshold).replace(".", "p")
                        for variant in variants:
                            out_file = f"{out_dir}/thr_{threshold_tag}_{variant}.v"
                            generate_and_store(
                                multiplier_cls,
                                a,
                                b,
                                adder_cls,
                                out_file,
                                variant=variant,
                                height_threshold=threshold,
                            )

                elif group_name in ["predefined_bw_greedy", "predefined_bw_balanced"]:
                    for bw in compressor_bws:
                        for variant in variants:
                            out_file = f"{out_dir}/bw_{bw}_{variant}.v"
                            generate_and_store(
                                multiplier_cls,
                                a,
                                b,
                                adder_cls,
                                out_file,
                                variant=variant,
                                max_compressor_bw=bw,
                            )

                elif group_name in ["threshold_predefined_bw_greedy", "threshold_predefined_bw_balanced"]:
                    for threshold in thresholds:
                        threshold_tag = str(threshold).replace(".", "p")
                        for bw in compressor_bws:
                            for variant in variants:
                                out_file = f"{out_dir}/thr_{threshold_tag}_bw_{bw}_{variant}.v"
                                generate_and_store(
                                    multiplier_cls,
                                    a,
                                    b,
                                    adder_cls,
                                    out_file,
                                    variant=variant,
                                    height_threshold=threshold,
                                    max_compressor_bw=bw,
                                )


print("OK")