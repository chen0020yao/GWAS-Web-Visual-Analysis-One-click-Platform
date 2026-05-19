import subprocess
import os
import shutil
import pandas as pd

def check_plink2_available():
    """前置校验PLINK2是否安装并可调用"""
    try:
        result = subprocess.run(["plink2", "--version"], check=True, capture_output=True, text=True)
        print(f"[INFO] PLINK2 版本: {result.stdout.splitlines()[0]}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise Exception("PLINK2 未安装或未加入系统环境变量，请先安装PLINK2")

def convert_to_plink(vcf_path, project_id):
    """VCF转PLINK二进制格式，全流程校验+错误捕获"""
    # 0. 前置环境校验
    check_plink2_available()

    # 1. 路径规范化处理
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(base_dir, "storage", project_id)
    vcf_path = os.path.abspath(vcf_path)

    # 2. 输入文件强校验
    if not os.path.exists(vcf_path):
        raise Exception(f"VCF文件不存在: {vcf_path}")
    if not os.access(vcf_path, os.R_OK):
        raise Exception(f"VCF文件无读取权限: {vcf_path}")

    # 3. 输出目录权限校验
    os.makedirs(output_dir, exist_ok=True)
    if not os.access(output_dir, os.W_OK):
        raise Exception(f"输出目录无写入权限: {output_dir}")

    # 4. 输出前缀定义（避免通用名冲突）
    output_prefix = os.path.join(output_dir, "genotype_final")
    print(f"[INFO] 输入VCF路径: {vcf_path}")
    print(f"[INFO] 输出文件前缀: {output_prefix}")

    # 5. 核心转换命令（全参数覆盖，解决exit 7高频场景）
    cmd = [
        "plink2",
        "--vcf", vcf_path,
        "--max-alleles", "2",        # 过滤多等位基因位点，核心修复
        "--make-bed",                 # 生成bed/bim/fam二进制文件
        "--out", output_prefix,
        "--allow-extra-chr",          # 兼容非标准染色体命名
        "--vcf-half-call", "m",       # 半合子位点处理规则
        "--vcf-idspace-to", "_",      # 处理ID中的空格，避免解析错误
        "--memory", "16384"           # 限制内存上限，避免大文件OOM
    ]

    print(f"[INFO] 执行PLINK2命令: {' '.join(cmd)}")

    try:
        # 执行命令，捕获全量输出+超时控制
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=3600  # 1小时超时，适配大文件转换
        )
        print(f"[INFO] PLINK2转换成功，标准输出:\n{result.stdout}")
        return output_prefix

    except subprocess.CalledProcessError as e:
        # 全量错误日志打印，精准定位问题
        print(f"[ERROR] ============== PLINK2转换失败 ==============")
        print(f"[ERROR] 退出码: {e.returncode}")
        print(f"[ERROR] 执行命令: {' '.join(e.cmd)}")
        print(f"[ERROR] 标准输出: {e.stdout}")
        print(f"[ERROR] 错误详情: {e.stderr}")
        print(f"[ERROR] ============================================")
        # 提取最核心的错误信息返回前端
        error_tip = e.stderr.splitlines()[-1] if e.stderr else "PLINK2执行失败，未知错误"
        raise Exception(f"PLINK2转换失败: {error_tip}")

    except subprocess.TimeoutExpired:
        raise Exception("PLINK2转换超时，文件过大或系统资源不足，请检查内存配置")


def qc_preview_analysis(prefix, maf, geno, mind, hwe):
    """质控预览统计，新增输入校验"""
    # 前置校验PLINK二进制文件完整性
    for suffix in [".bed", ".bim", ".fam"]:
        file_path = f"{prefix}{suffix}"
        if not os.path.exists(file_path):
            raise Exception(f"PLINK文件缺失: {file_path}")

    out_prefix = prefix + "_preview"
    maf_float, geno_float = float(maf), float(geno)
    mind_float, hwe_float = float(mind), float(hwe)

    try:
        # 执行统计命令
        subprocess.run([
            "plink2", "--bfile", prefix,
            "--freq", "--missing", "--hardy",
            "--out", out_prefix, "--allow-extra-chr", "--memory", "8192"
        ], check=True, capture_output=True, text=True, timeout=1800)

        # 读取PLINK2输出文件，处理列名
        freq = pd.read_csv(out_prefix + ".afreq", sep=r'\s+').rename(columns={'#ID': 'ID'})
        vmiss = pd.read_csv(out_prefix + ".vmiss", sep=r'\s+').rename(columns={'#ID': 'ID'})
        smiss = pd.read_csv(out_prefix + ".smiss", sep=r'\s+').rename(columns={'#IID': 'IID'})
        hwe_df = pd.read_csv(out_prefix + ".hardy", sep=r'\s+').rename(columns={'#ID': 'ID'})

        # 统计不合格位点/样本
        maf_fail = freq[freq["ALT_FREQS"] < maf_float]
        geno_fail = vmiss[vmiss["F_MISS"] > geno_float]
        mind_fail = smiss[smiss["F_MISS"] > mind_float]
        hwe_fail = hwe_df[hwe_df["P"] < hwe_float]
        removed_snp = set(maf_fail["ID"].tolist() + geno_fail["ID"].tolist() + hwe_fail["ID"].tolist())

        return {
            "total_snp": len(freq),
            "total_sample": len(smiss),
            "removed_snp": len(removed_snp),
            "removed_sample": len(mind_fail),
            "detail": {"maf": len(maf_fail), "geno": len(geno_fail), "hwe": len(hwe_fail), "mind": len(mind_fail)},
            "preview": maf_fail.head(50).to_dict(orient="records")
        }

    except subprocess.CalledProcessError as e:
        raise Exception(f"质控统计失败: {e.stderr.splitlines()[-1] if e.stderr else '未知错误'}")
    except Exception as e:
        raise Exception(f"读取质控数据失败: {str(e)}")


def run_plink_qc(prefix, maf=0.01, geno=0.1, mind=0.1, hwe=1e-6):
    """正式执行PLINK质控，全流程校验"""
    # 前置文件校验
    for suffix in [".bed", ".bim", ".fam"]:
        file_path = f"{prefix}{suffix}"
        if not os.path.exists(file_path):
            raise Exception(f"PLINK文件缺失: {file_path}")

    out_prefix = f"{prefix}_qc"
    cmd = [
        "plink2", "--bfile", prefix,
        "--maf", str(maf), "--geno", str(geno),
        "--mind", str(mind), "--hwe", str(hwe),
        "--make-bed", "--out", out_prefix,
        "--allow-extra-chr", "--memory", "16384"
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, timeout=3600
        )
        print(f"[INFO] PLINK质控完成，输出前缀: {out_prefix}")
        return out_prefix

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] PLINK质控失败: {e.stderr}")
        error_tip = e.stderr.splitlines()[-1] if e.stderr else "PLINK质控执行失败"
        raise Exception(f"PLINK质控错误: {error_tip}")