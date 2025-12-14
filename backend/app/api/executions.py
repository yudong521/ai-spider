"""执行记录管理 API"""

import json
import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session
from app.schemas.response import ApiResponse
from app.schemas.execution import ExecutionResponse, ExecutionListResponse
from app.models.execution import Execution
from app.models.task import Task
from app.services.task_service import TaskService
from app.exceptions import BizException, ErrorCode

router = APIRouter()

# 存储后台任务引用，防止被垃圾回收
_background_tasks: set[asyncio.Task] = set()


def _execution_to_response(execution: Execution) -> ExecutionResponse:
    """转换 Execution 模型为响应"""
    return ExecutionResponse(
        id=execution.id,
        task_id=execution.task_id,
        status=execution.status,
        result=execution.result,
        error_message=execution.error_message,
        execution_number=execution.execution_number,
        created_at=execution.created_at,
        started_at=execution.started_at,
        completed_at=execution.completed_at
    )


@router.get("/{task_id}/executions", response_model=ApiResponse[ExecutionListResponse])
async def list_executions(
    task_id: str,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取任务的执行历史列表"""
    # 确保任务存在
    task = await db.get(Task, task_id)
    if not task:
        raise BizException(*ErrorCode.TASK_NOT_FOUND)
    
    # 查询总数
    count_result = await db.execute(
        select(func.count(Execution.id)).where(Execution.task_id == task_id)
    )
    total = count_result.scalar()
    
    # 查询列表（按创建时间倒序）
    result = await db.execute(
        select(Execution)
        .where(Execution.task_id == task_id)
        .order_by(Execution.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    executions = list(result.scalars().all())
    
    return ApiResponse.success(ExecutionListResponse(
        items=[_execution_to_response(e) for e in executions],
        total=total
    ))


@router.get("/{task_id}/executions/{execution_id}", response_model=ApiResponse[ExecutionResponse])
async def get_execution(
    task_id: str,
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取执行记录详情"""
    execution = await db.get(Execution, execution_id)
    if not execution or execution.task_id != task_id:
        raise BizException(40401, "执行记录不存在")
    
    return ApiResponse.success(_execution_to_response(execution))


@router.post("/{task_id}/executions", response_model=ApiResponse[ExecutionResponse])
async def create_execution(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """创建新的执行记录并启动执行"""
    service = TaskService(db)
    
    # 检查任务状态
    task = await service.get_task(task_id)
    if task.status == "running":
        raise BizException(*ErrorCode.TASK_ALREADY_RUNNING)
    
    # 创建执行记录
    execution = await service.create_execution(task_id)
    
    # 后台执行任务
    async def _run_in_background():
        async with async_session() as session:
            svc = TaskService(session)
            try:
                await svc.run_execution(execution.id)
            except Exception:
                pass  # 错误已在 run_execution 中处理并保存到数据库
    
    # 创建后台任务
    bg_task = asyncio.create_task(_run_in_background())
    _background_tasks.add(bg_task)
    bg_task.add_done_callback(_background_tasks.discard)
    
    # 立即返回，不等待任务完成
    return ApiResponse.success(_execution_to_response(execution))


@router.post("/{task_id}/executions/{execution_id}/cancel", response_model=ApiResponse[ExecutionResponse])
async def cancel_execution(
    task_id: str,
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    """取消执行"""
    service = TaskService(db)
    execution = await service.cancel_execution(execution_id)
    return ApiResponse.success(_execution_to_response(execution))

