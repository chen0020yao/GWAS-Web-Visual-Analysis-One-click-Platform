from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.project import ProjectDB
from app.services.file_service import get_project_prefix
from app.services.qc_service import qc_preview_analysis
import uuid
import threading
import time

router = APIRouter()

# 内存中的任务状态存储
_task_store: dict = {}


def _run_task_async(task_id: str, project_id: str, step: str):
    """模拟异步任务执行，实际可替换为 plink2 调用"""
    try:
        _task_store[task_id] = {"status": "RUNNING", "progress": 0, "message": f"启动 {step} 任务..."}

        for pct in range(10, 100, 15):
            time.sleep(0.5)  # 模拟耗时
            _task_store[task_id] = {
                "status": "RUNNING",
                "progress": pct,
                "message": f"执行 {step} 中... ({pct}%)"
            }

        _task_store[task_id] = {"status": "SUCCESS", "progress": 100, "message": f"{step} 执行完成"}
    except Exception as e:
        _task_store[task_id] = {"status": "FAILED", "progress": 0, "message": str(e), "error_reason": str(e)}


@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    task = _task_store.get(task_id)
    if not task:
        return {"status": "SUCCESS", "progress": 100, "message": "任务完成"}
    return task


@router.get("/logs/{task_id}")
def get_task_logs(task_id: str):
    return {
        "logs": [
            "[INFO] 任务初始化",
            "[INFO] 加载输入文件",
            "[INFO] 数据校验通过",
            "[INFO] 执行计算...",
            "[INFO] 完成"
        ]
    }


@router.post("/stop/{task_id}")
def stop_task(task_id: str):
    _task_store[task_id] = {
        "status": "FAILED",
        "progress": 0,
        "message": "用户手动终止",
        "error_reason": "用户取消"
    }
    return {"message": "任务已终止"}


@router.get("/progress/{project_id}")
def get_project_progress(project_id: str, db: Session = Depends(get_db)):
    try:
        project_id_int = int(project_id)
        p = db.query(ProjectDB).filter(ProjectDB.id == project_id_int).first()
    except ValueError:
        p = None

    if not p:
        # 返回模拟进度
        return {
            "steps": [
                {"name": "UPLOAD", "status": "completed"},
                {"name": "QC", "status": "completed"},
                {"name": "PCA", "status": "running"},
                {"name": "GWAS", "status": "pending"},
            ],
            "current": "PCA"
        }

    steps_map = {"IDLE": 0, "UPLOADED": 1, "QC_DONE": 2, "ANALYSIS_DONE": 3}
    current_weight = steps_map.get(p.current_step, 0)

    return {
        "steps": [
            {"name": "UPLOAD", "status": "completed" if current_weight >= 1 else "pending"},
            {"name": "QC", "status": "completed" if current_weight >= 2 else "pending"},
            {"name": "PCA", "status": "completed" if current_weight >= 2 else "pending"},
            {"name": "GWAS", "status": "completed" if current_weight >= 3 else "pending"},
        ],
        "current": p.current_step
    }


@router.post("/convert-vcf")
def trigger_vcf_conversion(data: dict):
    project_id = data.get("projectId")
    task_id = f"task_{project_id}_convert"
    _task_store[task_id] = {"status": "RUNNING", "progress": 20, "message": "VCF转换中..."}
    t = threading.Thread(target=_run_task_async, args=(task_id, project_id, "VCF转换"))
    t.start()
    return {"taskId": task_id, "message": "转换任务已启动"}


@router.get("/qc-report/{project_id}")
def get_qc_report(project_id: str):
    try:
        prefix = get_project_prefix(project_id)
        result = qc_preview_analysis(prefix, maf=0.01, geno=0.1, mind=0.1, hwe=1e-6)
        return {
            "total_initial_snps": result["total_snp"],
            "total_removed_snps": result["removed_snp"],
            "rejection_reasons": [
                {"reason": "MAF < 0.01", "count": result["detail"]["maf"]},
                {"reason": "Geno > 0.1", "count": result["detail"]["geno"]},
                {"reason": "HWE < 1e-6", "count": result["detail"]["hwe"]},
                {"reason": "Mind > 0.1", "count": result["detail"]["mind"]},
            ],
            "status": "COMPLETED"
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"项目文件不存在: {str(e)}")


@router.post("/history/batch-delete")
def batch_delete_history(data: dict, db: Session = Depends(get_db)):
    project_ids = data.get("projectIds", [])
    deleted = 0
    for pid in project_ids:
        try:
            p = db.query(ProjectDB).filter(ProjectDB.id == int(pid)).first()
            if p:
                db.delete(p)
                deleted += 1
        except (ValueError, TypeError):
            pass
    db.commit()
    return {"deleted": deleted, "message": f"已删除 {deleted} 个项目"}


@router.post("/confirm-next")
def confirm_next_step(data: dict):
    project_id = data.get("projectId")
    step = data.get("step", "QC")
    task_id = f"task_{project_id}_{step}"
    _task_store[task_id] = {"status": "RUNNING", "progress": 10, "message": f"开始执行 {step}..."}
    t = threading.Thread(target=_run_task_async, args=(task_id, project_id, step))
    t.start()
    return {"taskId": task_id, "status": "RUNNING"}
