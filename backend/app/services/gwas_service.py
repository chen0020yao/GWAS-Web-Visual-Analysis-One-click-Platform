import subprocess
import os


def run_gwas(prefix, model="GLM", covariates=None):
    """运行 GWAS 关联分析，输出与输入同目录"""
    out = prefix + "_gwas"
    cmd = ["plink2", "--bfile", prefix, "--glm", "--out", out, "--allow-extra-chr", "--memory", "16384"]

    if model == "MLM":
        cmd.extend(["--mlm"])
    elif model == "FarmCPU":
        cmd.extend(["--glm", "farmcpu"])

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=3600)
        return out
    except subprocess.CalledProcessError as e:
        error_tip = e.stderr.splitlines()[-1] if e.stderr else "GWAS执行失败"
        raise Exception(f"GWAS分析错误: {error_tip}")


def run_pca(prefix, npc=10):
    """运行 PCA 分析，输出与输入同目录"""
    out = prefix + "_pca"
    cmd = ["plink2", "--bfile", prefix, "--pca", str(npc), "--out", out, "--allow-extra-chr", "--memory", "8192"]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=1800)
        return out + ".eigenvec"
    except subprocess.CalledProcessError as e:
        error_tip = e.stderr.splitlines()[-1] if e.stderr else "PCA执行失败"
        raise Exception(f"PCA分析错误: {error_tip}")
