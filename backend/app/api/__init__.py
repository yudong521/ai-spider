"""API 路由"""

from fastapi import APIRouter

from app.api.tasks import router as tasks_router
from app.api.executions import router as executions_router
from app.api.logs import router as logs_router
from app.api.stats import router as stats_router
from app.api.configs import router as configs_router

api_router = APIRouter()

api_router.include_router(tasks_router, prefix="/tasks", tags=["任务管理"])
api_router.include_router(executions_router, prefix="/tasks", tags=["执行记录"])
api_router.include_router(logs_router, prefix="/tasks", tags=["执行日志"])
api_router.include_router(stats_router, prefix="/stats", tags=["统计"])
api_router.include_router(configs_router, prefix="/configs", tags=["配置管理"])

