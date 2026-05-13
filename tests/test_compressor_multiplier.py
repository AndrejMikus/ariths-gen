# Filename: test_compressor_multiplier.py
# Description: This script creates dataframe with error metrics for each created multiplier with given parameters.
# Author: Andrej Mikus
# This file was created with help of Github Copilot tool

from ariths_gen.wire_components import Bus

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

import csv
import os
import sys

import numpy as np

# Add the parent directory to the system path
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DIR_PATH, '..'))

mul_set = [
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
    ]

bitwidths = [4,8]
variants = ["1StepFull", "1StepTrunc", "2StepsFull", "2StepsTrunc"]
thresholds = [0.20, 0.60]
max_bws = [3,4]


def compute_error_metrics(multiplier, N=8, variant="General", signed=False, **kwargs):
    """
    computes error metrics for given circuits
    """

    a = Bus(N=N, prefix="a")
    b = Bus(N=N, prefix="b")

    mul = multiplier(a=a, b=b, variant=variant, **kwargs)

    if signed:
        av = np.arange(-(2**(N-1)), 2**(N-1))
    else:
        av = np.arange(2**N)

    bv = av.reshape(-1, 1)

    exact = av * bv
    approx = mul(av, bv)

    E = exact - approx
    AE = np.abs(E)  # absolute error
    
    total_cases = E.size
    
    # worst case error
    WCE = np.amax(AE)
    
    # mean absolute error
    MAE = np.mean(AE)
    
    # mean error
    ME = np.mean(E)
    
    # root mean square error
    RMSE = np.sqrt(np.mean(E**2))
    
    # nonzero results out of total results
    ER = np.count_nonzero(E) / total_cases
    
    # number of effective bits
    NoEB = 2*N - np.log2(1 + RMSE) if RMSE > 0 else 2*N
    
    return {
        'WCE': WCE,
        'MAE': MAE,
        'ME': ME,
        'RMSE': RMSE,
        'ER': ER,
        'NoEB': NoEB,
    }


def create_database_with_results():
    """
    fills the database
    """
    rows = []

    for mul in mul_set:
        signedness = "signed" if mul.__name__.startswith("Signed") else "unsigned"
        mul_name = mul.__name__
        
        needs_threshold = "Threshold" in mul_name
        needs_max_bw = "BW" in mul_name

        for N in bitwidths:
            for variant in variants:
                threshold_values = thresholds if needs_threshold else [None]
                max_bw_values = max_bws if needs_max_bw else [None]
                
                for threshold in threshold_values:
                    for max_bw in max_bw_values:
                        kwargs = {
                            "N": N,
                            "variant": variant,
                            "signed": (signedness == "signed"),
                        }
                        
                        if needs_threshold:
                            kwargs["threshold"] = threshold
                        if needs_max_bw:
                            kwargs["max_bw"] = max_bw
                        
                        metrics = compute_error_metrics(mul, **kwargs)

                        row = {
                            "multiplier": mul_name,
                            "signedness": signedness,
                            "bitwidth": N,
                            "variant": variant,
                            **metrics,
                        }
                        
                        if needs_threshold:
                            row["threshold"] = threshold
                        if needs_max_bw:
                            row["max_bw"] = max_bw
                        
                        rows.append(row)

    all_fieldnames = set()
    for row in rows:
        all_fieldnames.update(row.keys())
    
    header_items = ["multiplier", "signedness", "bitwidth", "variant", "threshold", "max_bw"]
    metrics = ["WCE", "MAE", "ME", "RMSE", "ER", "NoEB"]
    
    fieldnames = [f for f in header_items if f in all_fieldnames] + [f for f in metrics if f in all_fieldnames]
    
    for row in rows:
        for fieldname in fieldnames:
            if fieldname not in row:
                row[fieldname] = ""

    output_path = os.path.join(DIR_PATH, "results.csv")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {len(rows)} results.")

if __name__ == "__main__":
    create_database_with_results()