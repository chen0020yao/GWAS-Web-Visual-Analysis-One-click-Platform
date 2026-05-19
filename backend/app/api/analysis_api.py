from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body, Query
import os
from app.services.file_service import save_upload_file, vcf_to_plink, get_project_prefix
from app.services.qc_service import run_plink_qc, qc_preview_analysis
from app.services.pca_service import run_pca
from app.services.gwas_service import run_gwas
from app.services.plot_service import manhattan_data, qq_data, pca_data, load_gwas_result, significant_snps
from app.services.enrichment_service import go_enrichment, kegg_enrichment
from app.services.annotation_service import query_ncbi_snp

router = APIRouter()

# ====================
# 上传
# ====================
@router.post("/upload")
async def upload(
        project_id: str = Form(...),
        file: UploadFile = File(...),
        phenotype: UploadFile = File(...),
        covariate: UploadFile = File(None)
):
    try:
        g_path = save_upload_file(file, project_id)
        prefix = vcf_to_plink(g_path, project_id)
        pheno_path = save_upload_file(phenotype, project_id)
        _normalize_phenotype_fid(pheno_path)
        if covariate:
            save_upload_file(covariate, project_id)
        return {
            "code": 200,
            "msg": "数据接收并转换成功",
            "data": {"project_id": project_id, "prefix": prefix}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"后端报错: {str(e)}")


def _normalize_phenotype_fid(pheno_path: str):
    """将表型文件的 FID 列统一为 0，匹配 PLINK2 转换后的 .fam 格式"""
    import pandas as pd
    try:
        df = pd.read_csv(pheno_path, sep=r'\s+')
        if 'FID' in df.columns:
            df['FID'] = 0
            df.to_csv(pheno_path, sep='\t', index=False)
    except Exception:
        pass  # 非标准格式则跳过


# ====================
# QC 质控
# ====================
@router.post("/qc/preview")
async def qc_preview(
        projectId: str = Body(..., embed=True),
        maf: float = Body(0.01),
        geno: float = Body(0.1),
        mind: float = Body(0.1),
        hwe: float = Body(1e-6)
):
    try:
        prefix = get_project_prefix(projectId)
        result = qc_preview_analysis(prefix, maf=maf, geno=geno, mind=mind, hwe=hwe)
        return {"code": 200, "msg": "QC预览完成", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/qc/run")
async def qc_run(data: dict):
    try:
        project_id = data.get("projectId")
        filters = data.get("filters", {})
        prefix = get_project_prefix(project_id)
        qc_prefix = run_plink_qc(prefix, **filters)
        return {"msg": "QC执行完成", "data": {"qc_prefix": qc_prefix}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/qc/confirm")
def qc_confirm(data: dict):
    try:
        project_id = data.get("projectId")
        filters = data.get("filters", {})
        prefix = get_project_prefix(project_id)
        qc_prefix = run_plink_qc(prefix, **filters)
        return {"msg": "QC执行完成", "data": {"qc_prefix": qc_prefix}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/qc/report/{project_id}")
def get_qc_report(project_id: str):
    try:
        prefix = get_project_prefix(project_id)
        result = qc_preview_analysis(prefix, maf=0.01, geno=0.1, mind=0.1, hwe=1e-6)
        return {"code": 200, "msg": "QC报告", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# PCA
# ====================
@router.post("/pca")
def pca(data: dict):
    try:
        project_id = data.get("projectId")
        npc = data.get("npc", 10)
        qc_prefix = get_project_prefix(project_id) + "_qc"
        pca_file = run_pca(qc_prefix, npc=npc)
        return {"msg": "PCA完成", "data": {"pca_file": pca_file}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# GWAS
# ====================
@router.post("/run")
def run(data: dict):
    try:
        project_id = data.get("projectId")
        model = data.get("model", "GLM")
        covariates = data.get("covariates", [])

        prefix = get_project_prefix(project_id)
        qc_prefix = prefix + "_qc"

        # 优先用 QC 后的数据，没有则用原始数据
        if not os.path.exists(qc_prefix + ".bed"):
            qc_prefix = prefix

        # 查找并修正表型文件
        project_dir = os.path.dirname(prefix)
        pheno_file = None
        for f in os.listdir(project_dir):
            if f.endswith(".txt") and f != "plink.log" and "eigen" not in f:
                pheno_file = os.path.join(project_dir, f)
                _normalize_phenotype_fid(pheno_file)
                break

        gwas_prefix = run_gwas(qc_prefix, pheno_file=pheno_file, model=model, covariates=covariates)
        return {"msg": "GWAS完成", "data": {"gwas_prefix": gwas_prefix}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# 可视化数据
# ====================
@router.get("/plot-data/{project_id}")
def get_plot_data(project_id: str, type: str):
    try:
        prefix = get_project_prefix(project_id) + "_qc"
        if type == "manhattan":
            return manhattan_data(prefix)
        elif type == "qq":
            return qq_data(prefix)
        elif type == "pca":
            pca_file = prefix + "_pca.eigenvec"
            if not os.path.exists(pca_file):
                pca_file = run_pca(prefix, npc=10)
            return pca_data(pca_file)
        else:
            raise HTTPException(status_code=400, detail="不支持的图类型")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# 显著SNP
# ====================
@router.get("/snp/significant/{project_id}")
def get_significant_snps(project_id: str):
    try:
        prefix = get_project_prefix(project_id) + "_qc"
        snps = significant_snps(prefix)
        return snps
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# SNP注释
# ====================
@router.get("/annotation/{rsid}")
def get_annotation(rsid: str):
    try:
        result = query_ncbi_snp(rsid)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/snp/details")
def get_snp_details(rsid: str = Query(...)):
    try:
        result = query_ncbi_snp(rsid)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# 富集分析
# ====================
@router.get("/enrichment/{project_id}")
def enrichment(project_id: str):
    try:
        gwas_prefix = get_project_prefix(project_id) + "_qc"
        df = load_gwas_result(gwas_prefix)
        genes = df["ID"].astype(str).tolist()
        return {"go": go_enrichment(genes), "kegg": kegg_enrichment(genes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/enrichment/go/{project_id}")
def go_enrichment_only(project_id: str):
    try:
        gwas_prefix = get_project_prefix(project_id) + "_qc"
        df = load_gwas_result(gwas_prefix)
        genes = df["ID"].astype(str).tolist()
        return go_enrichment(genes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/enrichment/kegg/{project_id}")
def kegg_enrichment_only(project_id: str):
    try:
        gwas_prefix = get_project_prefix(project_id) + "_qc"
        df = load_gwas_result(gwas_prefix)
        genes = df["ID"].astype(str).tolist()
        return kegg_enrichment(genes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
