"""任务管理 API"""

import json
import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session
from app.schemas.response import ApiResponse
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, TaskConfig, ScheduleConfig
from app.services.task_service import TaskService

router = APIRouter()


def _task_to_response(task) -> TaskResponse:
    """转换 Task 模型为响应"""
    return TaskResponse(
        id=task.id,
        name=task.name,
        description=task.description,
        entry_urls=json.loads(task.entry_urls),
        model=task.model,
        extract_model=task.extract_model,
        config=TaskConfig(**json.loads(task.config)) if task.config else None,
        status=task.status,
        execution_count=task.execution_count,
        last_execution_id=task.last_execution_id,
        schedule_enabled=task.schedule_enabled,
        schedule_type=task.schedule_type,
        schedule_config=ScheduleConfig(**json.loads(task.schedule_config)) if task.schedule_config else None,
        next_run_at=task.next_run_at,
        last_scheduled_at=task.last_scheduled_at,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.post("", response_model=ApiResponse[TaskResponse])
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新任务（只创建，不执行）"""
    service = TaskService(db)
    task = await service.create_task(data)
    return ApiResponse.success(_task_to_response(task))


@router.get("", response_model=ApiResponse[TaskListResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取任务列表"""
    service = TaskService(db)
    tasks, total = await service.list_tasks(skip, limit)
    return ApiResponse.success(TaskListResponse(
        items=[_task_to_response(t) for t in tasks],
        total=total
    ))


@router.get("/{task_id}", response_model=ApiResponse[TaskResponse])
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取任务详情"""
    service = TaskService(db)
    task = await service.get_task(task_id)
    return ApiResponse.success(_task_to_response(task))


@router.put("/{task_id}", response_model=ApiResponse[TaskResponse])
async def update_task(
    task_id: str,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新任务"""
    service = TaskService(db)
    task = await service.update_task(task_id, data)
    return ApiResponse.success(_task_to_response(task))


@router.delete("/{task_id}", response_model=ApiResponse[None])
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除任务"""
    service = TaskService(db)
    await service.delete_task(task_id)
    return ApiResponse.success(message="删除成功")
