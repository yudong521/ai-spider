"""Token 统计中间件"""

import asyncio
from typing import Any
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class TokenCounterCallback(BaseCallbackHandler):
    """Token 统计回调 - 统计 LLM 调用的 token 消耗"""
    
    def __init__(self, execution_id: str, task_id: str, agent_type: str = "main_agent"):
        self.execution_id = execution_id
        self.task_id = task_id
        self.agent_type = agent_type
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_tokens = 0
        self.call_count = 0
        self.records: list[dict] = []  # 记录每次调用
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """在 LLM 调用结束时统计 token"""
        self.call_count += 1
        
        input_tokens = 0
        output_tokens = 0
        
        if response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            input_tokens = token_usage.get("prompt_tokens", 0)
            output_tokens = token_usage.get("completion_tokens", 0)
        
        total = input_tokens + output_tokens
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_tokens += total
        
        # 记录本次调用
        self.records.append({
            "execution_id": self.execution_id,
            "task_id": self.task_id,
            "agent_type": self.agent_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total,
        })
    
    def get_summary(self) -> dict:
        """获取统计摘要"""
        return {
            "execution_id": self.execution_id,
            "task_id": self.task_id,
            "agent_type": self.agent_type,
            "total_calls": self.call_count,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens,
        }
    
    def get_records(self) -> list[dict]:
        """获取所有调用记录"""
        return self.records
