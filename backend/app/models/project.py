from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base
from pydantic import BaseModel
from datetime import datetime


class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, default="")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    current_step = Column(String, default="IDLE")  # IDLE, UPLOADED, QC_DONE, ANALYSIS_DONE
    sample_count = Column(Integer, default=0)
    snp_count = Column(Integer, default=0)
    phenotype_name = Column(String, default="")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ProjectCreate(BaseModel):
    id: str = ""
    name: str = ""


class ProjectUpdate(BaseModel):
    name: str = None
    description: str = None
    current_step: str = None
    sample_count: int = None
    snp_count: int = None
    phenotype_name: str = None
