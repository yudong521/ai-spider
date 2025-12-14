"""执行记录模型"""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Execution(Base):
    """执行记录表 - 记录每次任务执行的详情"""
    __tablename__ = "executions"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # 格式: exec_YYYYMMDD_HHMMSS_xxx
    task_id: Mapped[str] = mapped_column(String(50), ForeignKey("tasks.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/running/completed/failed/cancelled
    result: Mapped[str | None] = mapped_column(Text, nullable=True)  # 执行结果(Markdown)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)  # 错误信息
    execution_number: Mapped[int] = mapped_column(Integer, default=1)  # 第几次执行
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

