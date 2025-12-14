"""日志中间件"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Callable
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log import ExecutionLog
from app.database import async_session


# 专用线程池，用于同步执行异步数据库操作
_log_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="log_writer")


def _sync_save_log(log_data: dict, model_used: str) -> None:
    """在独立线程中同步写入日志到数据库"""
    import asyncio
    
    async def _commit():
        db_log = ExecutionLog(
            execution_id=log_data["execution_id"],
            task_id=log_data["task_id"],
            step_number=log_data["step_number"],
            step_type=log_data["step_type"],
            input_content=log_data.get("input_content"),
            output_content=log_data.get("output_content"),
            input_tokens=log_data.get("input_tokens", 0),
            output_tokens=log_data.get("output_tokens", 0),
            model_used=model_used,
            duration_ms=log_data.get("duration_ms"),
            agent_type=log_data.get("agent_type"),
            tool_name=log_data.get("tool_name"),
            created_at=log_data.get("created_at", datetime.utcnow())
        )
        async with async_session() as session:
            session.add(db_log)
            await session.commit()
    
    # 在新线程中创建新的事件循环执行异步操作
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_commit())
    except Exception as e:
        print(f"[LoggingCallback] 日志写入失败: {e}")
    finally:
        loop.close()


class LoggingCallback(BaseCallbackHandler):
    """日志记录回调 - 记录 Agent 执行过程，实时写入数据库"""
    
    def __init__(
        self, 
        execution_id: str,
        task_id: str,
        db: AsyncSession,
        model_used: str,
        agent_type: str = "main_agent",
        on_step: Callable[[dict], None] | None = None
    ):
        self.execution_id = execution_id
        self.task_id = task_id
        self.db = db
        self.model_used = model_used
        self.agent_type = agent_type  # main_agent / extract_agent
        self.step_number = 0
        self.on_step = on_step  # 实时回调函数
        self._start_time: datetime | None = None
        self._current_tool_name: str | None = None  # 当前工具名称
    
    def _save_log_to_db(self, log: dict) -> None:
        """实时保存日志到数据库（使用线程池立即提交，不阻塞主事件循环）"""
        # 提交到线程池立即执行，确保日志实时写入
        _log_executor.submit(_sync_save_log, log.copy(), self.model_used)
    
    def on_llm_start(self, serialized: dict, prompts: list[str], **kwargs: Any) -> None:
        """LLM 开始调用"""
        self._start_time = datetime.utcnow()
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """LLM 调用结束"""
        self.step_number += 1
        duration_ms = None
        if self._start_time:
            duration_ms = int((datetime.utcnow() - self._start_time).total_seconds() * 1000)
        
        # 获取输出内容
        output_content = ""
        if response.generations and response.generations[0]:
            output_content = response.generations[0][0].text
        
        # Token 统计
        input_tokens = 0
        output_tokens = 0
        if response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            input_tokens = token_usage.get("prompt_tokens", 0)
            output_tokens = token_usage.get("completion_tokens", 0)
        
        log = {
            "execution_id": self.execution_id,
            "task_id": self.task_id,
            "step_number": self.step_number,
            "step_type": "think",
            "output_content": output_content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "duration_ms": duration_ms,
            "agent_type": self.agent_type,
            "created_at": datetime.utcnow(),
        }
        
        # 实时写入数据库
        self._save_log_to_db(log)
        
        # 实时回调
        if self.on_step:
            self.on_step(log)
    
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs: Any) -> None:
        """工具调用开始"""
        self.step_number += 1
        self._start_time = datetime.utcnow()
        
        tool_name = serialized.get("name", "unknown")
        self._current_tool_name = tool_name  # 保存当前工具名称
        log = {
            "execution_id": self.execution_id,
            "task_id": self.task_id,
            "step_number": self.step_number,
            "step_type": "tool_call",
            "input_content": input_str,
            "agent_type": self.agent_type,
            "tool_name": tool_name,
            "created_at": datetime.utcnow(),
        }
        
        # 实时写入数据库
        self._save_log_to_db(log)
        
        if self.on_step:
            self.on_step(log)
    
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """工具调用结束"""
        self.step_number += 1
        duration_ms = None
        if self._start_time:
            duration_ms = int((datetime.utcnow() - self._start_time).total_seconds() * 1000)
        
        log = {
            "execution_id": self.execution_id,
            "task_id": self.task_id,
            "step_number": self.step_number,
            "step_type": "tool_result",
            "output_content": output[:5000] if output else "",  # 限制长度
            "duration_ms": duration_ms,
            "agent_type": self.agent_type,
            "tool_name": self._current_tool_name,  # 使用保存的工具名称
            "created_at": datetime.utcnow(),
        }
        
        # 实时写入数据库
        self._save_log_to_db(log)
        
        if self.on_step:
            self.on_step(log)
