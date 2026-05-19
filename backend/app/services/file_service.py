import subprocess
import os
import shutil
from fastapi import HTTPException

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_upload_file(upload_file, project_id: str):
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)
    file_path = os.path.join(project_dir, upload_file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)
    return file_path

def vcf_to_plink(vcf_path: str, project_id: str):
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    output_prefix = os.path.join(project_dir, "plink")
    cmd = [
        "plink2",
        "--vcf", vcf_path,
        "--max-alleles", "2",
        "--make-bed",
        "--out", output_prefix,
        "--allow-extra-chr",
        "--vcf-half-call", "m"
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=3600)
        return output_prefix
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"VCF转换失败: {e.stderr[-100:]}")

def get_project_prefix(project_id: str):
    return os.path.join(UPLOAD_DIR, project_id, "plink")