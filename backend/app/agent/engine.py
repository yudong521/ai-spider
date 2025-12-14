"""Agent 引擎 - 核心执行逻辑"""

import asyncio
from typing import Callable

from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.model_adapter import ModelAdapter
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import current_time, create_crawl_tool
from app.agent.middleware import TokenCounterCallback, LoggingCallback
from app.models.task import Task
from app.models.execution import Execution
from app.models.token import TokenUsage
from app.schemas.task import TaskConfig


class AgentEngine:
    """Agent 引擎 - 管理任务执行"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model_adapter = ModelAdapter(db)
    
    async def execute_task(
        self,
        task: Task,
        execution: Execution,
        config: TaskConfig | None = None,
        on_step: Callable[[dict], None] | None = None
    ) -> str:
        """
        执行爬虫任务
        
        Args:
            task: 任务对象
            execution: 执行记录对象
            config: 任务配置
            on_step: 实时日志回调
        
        Returns:
            执行结果
        """
        config = config or TaskConfig()
        
        # 创建回调（传入execution_id和task_id）
        main_token_counter = TokenCounterCallback(execution.id, task.id, "main_agent")
        extract_token_counter = TokenCounterCallback(execution.id, task.id, "extract_agent")
        main_logging_callback = LoggingCallback(
            execution.id, task.id, self.db, task.model, 
            agent_type="main_agent", on_step=on_step
        )
        extract_logging_callback = LoggingCallback(
            execution.id, task.id, self.db, task.extract_model,
            agent_type="extract_agent"
        )
        
        # 获取 LLM 实例
        main_llm = await self.model_adapter.get_llm(
            task.model,
            temperature=config.main_temperature,
            callbacks=[main_token_counter, main_logging_callback]
        )
        
        extract_llm = await self.model_adapter.get_llm(
            task.extract_model,
            temperature=config.extract_temperature,
            callbacks=[extract_token_counter, extract_logging_callback]
        )
        
        # 构建用户任务描述
        import json
        entry_urls = json.loads(task.entry_urls)
        user_task = f"{task.description}\n入口URL: {', '.join(entry_urls)}"
        
        # 创建工具
        crawl_tool = create_crawl_tool(user_task, extract_llm)
        tools = [crawl_tool, current_time]

        # 创建中间件
        middleware = [
            ToolCallLimitMiddleware(
                tool_name="crawl_tool",
                run_limit=config.max_pages
            )
        ]

        # 创建 Agent
        agent = create_agent(
            main_llm,
            tools=tools,
            middleware=middleware
        )
        
        # 构建消息上下文
        messages = [
            SystemMessage(SYSTEM_PROMPT),
            HumanMessage(user_task)
        ]
        
        # 执行 Agent（callbacks 已在 LLM 创建时绑定，不需要在这里重复传递）
        # 注意：如果通过 config 传递 callbacks，会导致 callbacks 传播到内部所有 LLM 调用
        # 包括 extract_llm，从而导致重复日志记录
        result = await agent.ainvoke({"messages": messages})
        output = result["messages"][-1].content
        
        # 日志已在回调中实时写入数据库，这里确保最终提交
        await self.db.commit()
        
        # 保存 Token 统计到数据库
        await self._save_token_usage(main_token_counter, task.model)
        await self._save_token_usage(extract_token_counter, task.extract_model)
        
        return output
    
    async def _save_token_usage(self, counter: TokenCounterCallback, model_name: str):
        """保存 Token 使用记录到数据库"""
        for record in counter.get_records():
            usage = TokenUsage(
                execution_id=record["execution_id"],
                task_id=record["task_id"],
                agent_type=record["agent_type"],
                model_name=model_name,
                input_tokens=record["input_tokens"],
                output_tokens=record["output_tokens"],
                total_tokens=record["total_tokens"],
            )
            self.db.add(usage)
        await self.db.commit()
