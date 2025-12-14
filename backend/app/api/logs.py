"""执行日志 API"""

import json
import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.response import ApiResponse
from app.schemas.log import LogResponse, LogListResponse
from app.services.task_service import TaskService

router = APIRouter()


@router.get("/{task_id}/logs", response_model=ApiResponse[LogListResponse])
async def get_task_logs(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取任务最新执行的日志"""
    service = TaskService(db)
    logs = await service.get_task_logs(task_id)
    
    return ApiResponse.success(LogListResponse(
        items=[LogResponse.model_validate(log) for log in logs],
        total=len(logs)
    ))


@router.get("/{task_id}/executions/{execution_id}/logs", response_model=ApiResponse[LogListResponse])
async def get_execution_logs(
    task_id: str,
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取指定执行记录的日志"""
    service = TaskService(db)
    logs = await service.get_execution_logs(execution_id)
    
    return ApiResponse.success(LogListResponse(
        items=[LogResponse.model_validate(log) for log in logs],
        total=len(logs)
    ))


@router.get("/{task_id}/executions/{execution_id}/logs/stream")
async def stream_execution_logs(
    task_id: str,
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    """SSE 实时日志流（基于执行记录）"""
    service = TaskService(db)
    execution = await service.get_execution(execution_id)
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """生成 SSE 事件"""
        # 先发送历史日志
        logs = await service.get_execution_logs(execution_id)
        for log in logs:
            data = {
                "step": log.step_number,
                "type": log.step_type,
                "content": log.output_content or log.input_content,
                "tokens": log.input_tokens + log.output_tokens,
                "agent_type": log.agent_type,
                "tool_name": log.tool_name
            }
            yield f"event: step\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
        
        # 如果执行已完成，发送完成事件
        if execution.status in ("completed", "failed", "cancelled"):
            data = {
                "status": execution.status,
                "result": execution.result,
                "error": execution.error_message
            }
            yield f"event: complete\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
            return
        
        # 等待新日志（轮询数据库）
        last_step = len(logs)
        timeout_count = 0
        max_timeout = 300  # 5分钟超时
        
        while timeout_count < max_timeout:
            await asyncio.sleep(1)
            timeout_count += 1
            
            # 查询新日志
            new_logs = await service.get_execution_logs(execution_id)
            if len(new_logs) > last_step:
                for log in new_logs[last_step:]:
                    data = {
                        "step": log.step_number,
                        "type": log.step_type,
                        "content": log.output_content or log.input_content,
                        "tokens": log.input_tokens + log.output_tokens,
                        "agent_type": log.agent_type,
                        "tool_name": log.tool_name
                    }
                    yield f"event: step\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
                last_step = len(new_logs)
            
            # 检查执行状态
            execution_updated = await service.get_execution(execution_id)
            if execution_updated.status in ("completed", "failed", "cancelled"):
                data = {
                    "status": execution_updated.status,
                    "result": execution_updated.result,
                    "error": execution_updated.error_message
                }
                yield f"event: complete\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
                return
        
        # 超时
        yield f"event: timeout\ndata: {json.dumps({'message': '连接超时'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
