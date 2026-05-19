import subprocess
import os


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
