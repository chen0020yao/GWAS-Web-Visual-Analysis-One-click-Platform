import pandas as pd
import numpy as np

SIGNIFICANCE_THRESHOLD = 5e-8


def extract_significant_snp(df):
    """
    提取显著SNP
    """
    sig = df[df["P"] < SIGNIFICANCE_THRESHOLD].copy()

    sig["-log10p"] = -np.log10(sig["P"])

    sig = sig.sort_values("P")

    return sig[["ID", "CHR", "BP", "P", "-log10p"]].to_dict("records")