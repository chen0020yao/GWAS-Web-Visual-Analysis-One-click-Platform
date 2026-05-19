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
            "id": str(p.id),
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
    project = ProjectDB(name=data.name or "", current_step="IDLE")
    db.add(project)
    db.commit()
    db.refresh(project)
    return {
        "id": str(project.id),
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
def get_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")
    return {
        "id": str(p.id),
        "name": p.name or f"项目_{p.id}",
        "current_step": p.current_step,
        "created_at": p.created_at.isoformat() if p.created_at else "",
        "updated_at": p.updated_at.isoformat() if p.updated_at else "",
        "sample_count": p.sample_count,
        "snp_count": p.snp_count,
        "phenotype_name": p.phenotype_name,
    }


@router.patch("/{project_id}")
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    p = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")
    if data.name is not None:
        p.name = data.name
    db.commit()
    return {"message": "更新成功", "id": str(p.id)}


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")
    db.delete(p)
    db.commit()
    return {"message": "项目已删除"}
