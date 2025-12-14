"""执行日志相关 schemas"""

from datetime import datetime
from pydantic import BaseModel


class LogResponse(BaseModel):
    """执行日志响应"""
    id: int
    execution_id: str
    task_id: str
    step_number: int
    step_type: str
    input_content: str | None
    output_content: str | None
    input_tokens: int
    output_tokens: int
    model_used: str | None
    duration_ms: int | None
    agent_type: str | None
    tool_name: str | None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class LogListResponse(BaseModel):
    """日志列表响应"""
    items: list[LogResponse]
    total: int

