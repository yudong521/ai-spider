"""FastAPI 应用入口"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, async_session
from app.api import api_router
from app.exceptions import BizException
from app.services.config_service import ConfigService
from app.services.scheduler import scheduler_service
from app.middleware.auth import AuthMiddleware

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    
    # 初始化默认配置
    async with async_session() as db:
        config_service = ConfigService(db)
        await config_service.init_configs()
    
    # 启动定时任务调度器
    await scheduler_service.start()
    logger.info("定时任务调度器已启动")
    
    yield
    
    # 关闭定时任务调度器
    await scheduler_service.shutdown()
    logger.info("定时任务调度器已关闭")


app = FastAPI(
    title="智能爬虫 Agent API",
    description="基于 LLM 的智能爬虫 Agent 系统",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 认证中间件
app.add_middleware(AuthMiddleware)


# 全局异常处理器
@app.exception_handler(BizException)
async def biz_exception_handler(request: Request, exc: BizException):
    """业务异常处理"""
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "message": exc.message, "data": None}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={"code": 50000, "message": str(exc), "data": None}
    )


# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"code": 0, "message": "ok", "data": {"status": "ok"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

