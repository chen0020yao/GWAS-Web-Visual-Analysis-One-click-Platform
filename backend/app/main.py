from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth_api, analysis_api, project_api, pipeline_api, report_api
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GWAS Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_api.router, prefix="/api/user", tags=["用户认证"])
app.include_router(analysis_api.router, prefix="/api/analysis", tags=["分析业务"])
app.include_router(project_api.router, prefix="/api/projects", tags=["项目管理"])
app.include_router(pipeline_api.router, prefix="/api/pipeline", tags=["管线任务"])
app.include_router(report_api.router, prefix="/api/report", tags=["报告导出"])


@app.get("/")
async def root():
    return {"message": "GWAS Backend API is running", "docs": "/docs"}
