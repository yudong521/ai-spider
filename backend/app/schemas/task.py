"""任务相关 schemas"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, field_validator


class TaskConfig(BaseModel):
    """任务高级配置"""
    max_pages: int = 20
    main_temperature: float = 0.5
    extract_temperature: float = 0.0
    timeout: int = 600


class ScheduleConfig(BaseModel):
    """定时配置"""
    # interval 类型: 间隔执行 (单位: 分钟)
    interval_minutes: int | None = None
    
    # cron 类型: cron 表达式各字段
    cron_hour: int | None = None      # 0-23
    cron_minute: int | None = None    # 0-59
    cron_day_of_week: str | None = None  # mon,tue,wed,thu,fri,sat,sun 或 * 表示每天
    
    # once 类型: 一次性执行时间
    once_at: datetime | None = None
    
    @field_validator('cron_hour')
    @classmethod
    def validate_hour(cls, v):
        if v is not None and (v < 0 or v > 23):
            raise ValueError('小时必须在 0-23 之间')
        return v
    
    @field_validator('cron_minute')
    @classmethod
    def validate_minute(cls, v):
        if v is not None and (v < 0 or v > 59):
            raise ValueError('分钟必须在 0-59 之间')
        return v


class TaskCreate(BaseModel):
    """创建任务请求"""
    name: str
    description: str
    entry_urls: list[str]
    model: str = "qwen3-max"
    extract_model: str = "qwen3-max"
    config: TaskConfig | None = None
    
    # 定时配置
    schedule_enabled: bool = False
    schedule_type: Literal["interval", "cron", "once"] | None = None
    schedule_config: ScheduleConfig | None = None


class TaskResponse(BaseModel):
    """任务响应"""
    id: str
    name: str
    description: str
    entry_urls: list[str]
    model: str
    extract_model: str
    config: TaskConfig | None
    status: str
    execution_count: int
    last_execution_id: str | None
    
    # 定时相关
    schedule_enabled: bool
    schedule_type: str | None
    schedule_config: ScheduleConfig | None
    next_run_at: datetime | None
    last_scheduled_at: datetime | None
    
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """任务列表响应"""
    items: list[TaskResponse]
    total: int


class TaskUpdate(BaseModel):
    """更新任务请求"""
    name: str | None = None
    description: str | None = None
    entry_urls: list[str] | None = None
    model: str | None = None
    extract_model: str | None = None
    config: TaskConfig | None = None
    
    # 定时配置
    schedule_enabled: bool | None = None
    schedule_type: Literal["interval", "cron", "once"] | None = None
    schedule_config: ScheduleConfig | None = None
