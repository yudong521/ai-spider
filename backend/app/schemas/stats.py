"""Token 统计相关 schemas"""

from pydantic import BaseModel


class TokenStatsByAgent(BaseModel):
    """按 Agent 类型统计"""
    input_tokens: int
    output_tokens: int
    calls: int


class TokenStatsByStep(BaseModel):
    """按步骤统计"""
    step: int
    type: str
    tokens: int


class TokenStatsSummary(BaseModel):
    """Token 统计汇总"""
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    llm_calls: int
    estimated_cost_yuan: float | None = None


class TokenStats(BaseModel):
    """任务 Token 统计"""
    task_id: str
    execution_id: str | None = None
    summary: TokenStatsSummary
    by_agent: dict[str, TokenStatsByAgent]
    by_step: list[TokenStatsByStep]


class OverviewStats(BaseModel):
    """总体统计"""
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_tokens: int
    total_cost_yuan: float | None = None

