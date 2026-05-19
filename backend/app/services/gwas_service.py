import subprocess
import os


def run_gwas(prefix, model="GLM", covariates=None):
    """运行 GWAS 关联分析"""
    out = prefix + "_gwas"
    cmd = [
        "plink2", "--bfile", prefix,
        "--glm", "hide-covar",
        "--out", out,
        "--allow-extra-chr",
        "--memory", "16384"
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=3600)
        print(f"[INFO] GWAS stdout: {result.stdout[-500:]}")
        return out
    except subprocess.CalledProcessError as e:
        error_tip = e.stderr.splitlines()[-1] if e.stderr else "GWAS执行失败"
        print(f"[ERROR] GWAS stderr: {e.stderr[-1000:]}")
        raise Exception(f"GWAS分析错误: {error_tip}")
