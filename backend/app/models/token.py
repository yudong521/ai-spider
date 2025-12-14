"""Token 使用记录模型"""

from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TokenUsage(Base):
    """Token 使用记录表"""
    __tablename__ = "token_usage"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    execution_id: Mapped[str] = mapped_column(String(50), ForeignKey("executions.id"), index=True)
    task_id: Mapped[str] = mapped_column(String(50), ForeignKey("tasks.id"), index=True)  # 冗余字段，方便查询
    log_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("execution_logs.id"), nullable=True)
    agent_type: Mapped[str] = mapped_column(String(20), nullable=False)  # main_agent/extract_agent
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

