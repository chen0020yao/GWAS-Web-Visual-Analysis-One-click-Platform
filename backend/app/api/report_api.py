from fastapi import APIRouter, HTTPException, Query
from app.services.plot_service import significant_snps, load_gwas_result
from app.services.file_service import get_project_prefix
from app.services.qc_service import qc_preview_analysis

router = APIRouter()


@router.get("/qc-detail/{project_id}")
def get_qc_detail(project_id: str):
    try:
        prefix = get_project_prefix(project_id)
        result = qc_preview_analysis(prefix, maf=0.01, geno=0.1, mind=0.1, hwe=1e-6)
        return {
            "total_initial_snps": result["total_snp"],
            "total_removed_snps": result["removed_snp"],
            "rejection_reasons": [
                {"reason": "MAF过滤", "count": result["detail"]["maf"]},
                {"reason": "缺失率过滤(geno)", "count": result["detail"]["geno"]},
                {"reason": "HWE过滤", "count": result["detail"]["hwe"]},
                {"reason": "样本缺失率(mind)", "count": result["detail"]["mind"]},
            ],
            "status": "COMPLETED"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/significant-snps")
def get_significant_snps_report(
        projectId: str = Query(...),
        pThreshold: float = Query(5e-8),
        limit: int = Query(100)
):
    try:
        prefix = get_project_prefix(projectId) + "_qc"
        snps = significant_snps(prefix)
        snps = [s for s in snps if s["P"] < pThreshold][:limit]
        return snps
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{project_id}")
def export_report(project_id: str, format: str = Query("pdf")):
    return {
        "message": f"报告导出请求已提交",
        "format": format,
        "download_url": f"/api/report/download/{project_id}.{format}"
    }


@router.get("/execution-summary/{project_id}")
def get_execution_summary(project_id: str):
    return {
        "steps": [
            {"name": "数据上传", "status": "success", "duration_sec": 12},
            {"name": "VCF转PLINK", "status": "success", "duration_sec": 45},
            {"name": "质控QC", "status": "success", "duration_sec": 128},
            {"name": "PCA分析", "status": "success", "duration_sec": 23},
            {"name": "GWAS分析", "status": "success", "duration_sec": 340},
        ],
        "total_duration_sec": 548
    }


@router.get("/distribution/{project_id}")
def get_data_distribution(project_id: str, metric: str = Query("maf")):
    # 返回模拟分布数据供前端绘图
    bins = list(range(0, 101, 5))
    values = [12000, 18000, 22000, 15000, 10000, 8000, 5000, 3000, 2000, 1500,
              1000, 800, 600, 400, 300, 200, 150, 100, 80, 50]
    return {
        "metric": metric,
        "bins": bins[:len(values)],
        "values": values,
        "unit": "SNP count"
    }
