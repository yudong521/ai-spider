"""执行记录相关 schemas"""

from datetime import datetime
from pydantic import BaseModel


class ExecutionResponse(BaseModel):
    """执行记录响应"""
    id: str
    task_id: str
    status: str
    result: str | None
    error_message: str | None
    execution_number: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    
    model_config = {"from_attributes": True}


class ExecutionListResponse(BaseModel):
    """执行记录列表响应"""
    items: list[ExecutionResponse]
    total: int


class ExecutionCreate(BaseModel):
    """创建执行记录请求（内部使用）"""
    task_id: str
    execution_number: int = 1

