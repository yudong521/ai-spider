"""任务模型"""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Task(Base):
    """任务表"""
    __tablename__ = "tasks"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    entry_urls: Mapped[str] = mapped_column(Text, nullable=False)  # JSON 数组
    model: Mapped[str] = mapped_column(String(50), nullable=False, default="qwen3-max")
    extract_model: Mapped[str] = mapped_column(String(50), nullable=False, default="qwen3-max")
    config: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON 配置
    status: Mapped[str] = mapped_column(String(20), default="pending")  # 最新执行状态: pending/running/completed/failed/cancelled
    execution_count: Mapped[int] = mapped_column(Integer, default=0)  # 执行次数
    last_execution_id: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 最新执行ID
    
    # 定时执行相关字段
    schedule_enabled: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否启用定时执行
    schedule_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 定时类型: interval/cron/once
    schedule_config: Mapped[str | None] = mapped_column(Text, nullable=True)  # 定时配置 JSON
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # 下次执行时间
    last_scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # 上次定时执行时间
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

