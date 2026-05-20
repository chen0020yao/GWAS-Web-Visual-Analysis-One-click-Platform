from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.project import ProjectDB, ProjectCreate, ProjectUpdate

router = APIRouter()


@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(ProjectDB).order_by(ProjectDB.updated_at.desc()).all()
    return [
        {
            "id": p.id,
            "name": p.name or f"项目_{p.id}",
            "created_at": p.created_at.isoformat() if p.created_at else "",
            "updated_at": p.updated_at.isoformat() if p.updated_at else "",
            "current_step": p.current_step,
            "sample_count": p.sample_count,
            "snp_count": p.snp_count,
            "status": "COMPLETED" if p.current_step == "ANALYSIS_DONE" else "IN_PROGRESS",
            "step": p.current_step,
        }
        for p in projects
    ]


@router.post("/")
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    # 如果已存在同 ID 项目则跳过创建
    existing = db.query(ProjectDB).filter(ProjectDB.id == data.id).first()
    if existing:
        return {
            "id": existing.id,
            "name": existing.name or f"项目_{existing.id}",
            "current_step": existing.current_step,
            "created_at": existing.created_at.isoformat() if existing.created_at else ""
        }
    project = ProjectDB(id=data.id, name=data.name or "", current_step="IDLE")
    db.add(project)
    db.commit()
    db.refresh(project)
    return {
        "id": project.id,
        "name": project.name or f"项目_{project.id}",
        "current_step": project.current_step,
        "created_at": project.created_at.isoformat() if project.created_at else ""
    }


@router.get("/summary")
def project_summary(db: Session = Depends(get_db)):
    total = db.query(ProjectDB).count()
    completed = db.query(ProjectDB).filter(ProjectDB.current_step == "ANALYSIS_DONE").count()
    return {
        "total_projects": total,
        "completed": completed,
        "in_progress": total - completed,
        "total_storage_gb": 1.2
    }


@router.get("/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    p = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")
    return {
        "id": p.id,
        "name": p.name or f"项目_{p.id}",
        "current_step": p.current_step,
        "created_at": p.created_at.isoformat() if p.created_at else "",
        "updated_at": p.updated_at.isoformat() if p.updated_at else "",
        "sample_count": p.sample_count,
        "snp_count": p.snp_count,
        "phenotype_name": p.phenotype_name,
    }


@router.patch("/{project_id}")
def update_project(project_id: str, data: ProjectUpdate, db: Session = Depends(get_db)):
    p = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")
    if data.name is not None:
        p.name = data.name
    if data.current_step is not None:
        p.current_step = data.current_step
    if data.sample_count is not None:
        p.sample_count = data.sample_count
    if data.snp_count is not None:
        p.snp_count = data.snp_count
    if data.phenotype_name is not None:
        p.phenotype_name = data.phenotype_name
    db.commit()
    return {"message": "更新成功", "id": p.id, "current_step": p.current_step}


@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    p = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")
    db.delete(p)
    db.commit()
    return {"message": "项目已删除"}
