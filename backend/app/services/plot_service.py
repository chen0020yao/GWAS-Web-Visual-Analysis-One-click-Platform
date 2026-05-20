import pandas as pd
import numpy as np
import glob
from app.services.utils import make_json_safe as _make_json_safe

SIGNIFICANCE = 5e-8


# =========================
# 读取GWAS结果
# =========================
def load_gwas_result(prefix):
    file = glob.glob(prefix + "*.glm*")[0]
    df = pd.read_csv(file, sep="\t")

    df = df.rename(columns={"#CHROM": "CHR", "POS": "BP", "P": "P"})
    df = df[df["P"].notna()]
    df = df[df["P"] > 0]

    df["-log10p"] = -np.log10(df["P"])
    return df


# =========================
# 曼哈顿图（含显著标注）
# =========================
def prepare_manhattan(df):
    df["CHR"] = df["CHR"].astype(int)
    df = df.sort_values(["CHR", "BP"])

    offset = 0
    ticks, labels = [], []
    chr_offset = {}

    for c in sorted(df["CHR"].unique()):
        sub = df[df["CHR"] == c]

        chr_offset[c] = offset

        mid = offset + (sub["BP"].max() - sub["BP"].min()) / 2
        ticks.append(mid)
        labels.append(str(c))

        offset += sub["BP"].max()

    df["x"] = df.apply(lambda r: r["BP"] + chr_offset[r["CHR"]], axis=1)

    return df, ticks, labels


# =========================
# 曼哈顿数据（含显著SNP）
# =========================
def manhattan_data(prefix):
    df = load_gwas_result(prefix)
    df, ticks, labels = prepare_manhattan(df)

    groups = []

    for c in sorted(df["CHR"].unique()):
        sub = df[df["CHR"] == c]

        data = []
        for x, y, rs, p in zip(sub["x"], sub["-log10p"], sub["ID"], sub["P"]):

            data.append({
                "value": [float(x), float(y)],
                "rsid": str(rs),
                "p": float(p),
                "significant": float(p) < SIGNIFICANCE
            })

        groups.append({
            "chr": int(c),
            "data": data
        })

    return _make_json_safe({
        "groups": groups,
        "ticks": ticks,
        "labels": labels,
        "threshold": -np.log10(SIGNIFICANCE)
    })


# =========================
# QQ图 + λGC
# =========================
def qq_data(prefix):
    df = load_gwas_result(prefix)

    p = np.sort(df["P"].values)

    expected = -np.log10(np.linspace(1/len(p), 1, len(p)))
    observed = -np.log10(p)

    chi2 = np.quantile(-2 * np.log(p), 0.5)
    lambda_gc = chi2 / 0.456

    return _make_json_safe({
        "expected": expected.tolist(),
        "observed": observed.tolist(),
        "lambda_gc": lambda_gc
    })


# =========================
# PCA数据
# =========================
def pca_data(eigenvec_file):
    df = pd.read_csv(eigenvec_file, sep=r'\s+', header=None)

    return _make_json_safe({
        "x": df[2].tolist(),
        "y": df[3].tolist()
    })
#===================
#gene提取
#==========
def extract_genes_from_snps(sig_df):
    """
    从显著SNP提取gene（这里简化：来自NCBI结果）
    """
    return list(set(sig_df["GENE"].dropna().tolist()))

# =========================
# 显著SNP列表
# =========================
def significant_snps(prefix):
    df = load_gwas_result(prefix)

    sig = df[df["P"] < SIGNIFICANCE].copy()
    sig = sig.sort_values("P")

    records = sig[["ID", "CHR", "BP", "P"]].to_dict("records")
    return _make_json_safe(records)