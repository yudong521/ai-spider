"""统计服务"""

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.execution import Execution
from app.models.token import TokenUsage
from app.models.log import ExecutionLog
from app.schemas.stats import (
    TokenStats, 
    TokenStatsSummary, 
    TokenStatsByAgent,
    TokenStatsByStep,
    OverviewStats
)
from app.exceptions import BizException, ErrorCode


class StatsService:
    """统计服务 - Token 统计和汇总"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_task_token_stats(self, task_id: str) -> TokenStats:
        """获取任务最新执行的 Token 统计"""
        # 获取任务的最新执行ID
        task = await self.db.get(Task, task_id)
        if not task:
            raise BizException(*ErrorCode.TASK_NOT_FOUND)
        
        if not task.last_execution_id:
            # 没有执行记录，返回空统计
            return TokenStats(
                task_id=task_id,
                execution_id=None,
                summary=TokenStatsSummary(
                    total_input_tokens=0,
                    total_output_tokens=0,
                    total_tokens=0,
                    llm_calls=0,
                    estimated_cost_yuan=None
                ),
                by_agent={},
                by_step=[]
            )
        
        return await self.get_execution_token_stats(task.last_execution_id)
    
    async def get_execution_token_stats(self, execution_id: str) -> TokenStats:
        """获取指定执行记录的 Token 统计"""
        # 验证执行记录存在
        execution = await self.db.get(Execution, execution_id)
        if not execution:
            raise BizException(40401, "执行记录不存在")
        
        # 查询总计
        result = await self.db.execute(
            select(
                func.sum(TokenUsage.input_tokens).label("total_input"),
                func.sum(TokenUsage.output_tokens).label("total_output"),
                func.sum(TokenUsage.total_tokens).label("total"),
                func.count(TokenUsage.id).label("calls")
            )
            .where(TokenUsage.execution_id == execution_id)
        )
        row = result.first()
        
        summary = TokenStatsSummary(
            total_input_tokens=row.total_input or 0,
            total_output_tokens=row.total_output or 0,
            total_tokens=row.total or 0,
            llm_calls=row.calls or 0,
            estimated_cost_yuan=self._estimate_cost(row.total or 0)
        )
        
        # 按 Agent 类型统计
        by_agent_result = await self.db.execute(
            select(
                TokenUsage.agent_type,
                func.sum(TokenUsage.input_tokens).label("input"),
                func.sum(TokenUsage.output_tokens).label("output"),
                func.count(TokenUsage.id).label("calls")
            )
            .where(TokenUsage.execution_id == execution_id)
            .group_by(TokenUsage.agent_type)
        )
        
        by_agent = {}
        for row in by_agent_result:
            by_agent[row.agent_type] = TokenStatsByAgent(
                input_tokens=row.input or 0,
                output_tokens=row.output or 0,
                calls=row.calls or 0
            )
        
        # 按步骤统计
        logs_result = await self.db.execute(
            select(ExecutionLog)
            .where(ExecutionLog.execution_id == execution_id)
            .order_by(ExecutionLog.step_number)
        )
        
        by_step = []
        for log in logs_result.scalars():
            by_step.append(TokenStatsByStep(
                step=log.step_number,
                type=log.step_type,
                tokens=log.input_tokens + log.output_tokens
            ))
        
        return TokenStats(
            task_id=execution.task_id,
            execution_id=execution_id,
            summary=summary,
            by_agent=by_agent,
            by_step=by_step
        )
    
    async def get_overview_stats(self) -> OverviewStats:
        """获取总体统计"""
        # 任务统计
        task_result = await self.db.execute(
            select(
                func.count(Task.id).label("total"),
                func.sum(case((Task.status == "completed", 1), else_=0)).label("completed"),
                func.sum(case((Task.status == "failed", 1), else_=0)).label("failed")
            )
        )
        task_row = task_result.first()
        
        # Token 统计
        token_result = await self.db.execute(
            select(func.sum(TokenUsage.total_tokens))
        )
        total_tokens = token_result.scalar() or 0
        
        return OverviewStats(
            total_tasks=task_row.total or 0,
            completed_tasks=task_row.completed or 0,
            failed_tasks=task_row.failed or 0,
            total_tokens=total_tokens,
            total_cost_yuan=self._estimate_cost(total_tokens)
        )
    
    def _estimate_cost(self, tokens: int) -> float | None:
        """估算成本（简单估算，实际应根据不同模型计算）"""
        if tokens <= 0:
            return None
        # 假设平均 0.015 元/千 token
        return round(tokens * 0.015 / 1000, 4)
