"""统计 API"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.response import ApiResponse
from app.schemas.stats import TokenStats, OverviewStats
from app.services.stats_service import StatsService

router = APIRouter()


@router.get("/tasks/{task_id}/token-stats", response_model=ApiResponse[TokenStats])
async def get_task_token_stats(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取任务最新执行的 Token 统计"""
    service = StatsService(db)
    stats = await service.get_task_token_stats(task_id)
    return ApiResponse.success(stats)


@router.get("/executions/{execution_id}/token-stats", response_model=ApiResponse[TokenStats])
async def get_execution_token_stats(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取指定执行记录的 Token 统计"""
    service = StatsService(db)
    stats = await service.get_execution_token_stats(execution_id)
    return ApiResponse.success(stats)


@router.get("/overview", response_model=ApiResponse[OverviewStats])
async def get_overview_stats(
    db: AsyncSession = Depends(get_db)
):
    """获取总体统计"""
    service = StatsService(db)
    stats = await service.get_overview_stats()
    return ApiResponse.success(stats)
