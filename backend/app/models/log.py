"""执行日志模型"""

from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ExecutionLog(Base):
    """执行日志表"""
    __tablename__ = "execution_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    execution_id: Mapped[str] = mapped_column(String(50), ForeignKey("executions.id"), index=True)
    task_id: Mapped[str] = mapped_column(String(50), ForeignKey("tasks.id"), index=True)  # 冗余字段，方便查询
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[str] = mapped_column(String(20), nullable=False)  # think/tool_call/tool_result/extract/final
    input_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    model_used: Mapped[str | None] = mapped_column(String(50), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    agent_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # main_agent / extract_agent
    tool_name: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 工具名称
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

