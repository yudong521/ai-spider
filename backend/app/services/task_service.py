"""任务服务"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Callable
from uuid import uuid4

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.execution import Execution
from app.models.log import ExecutionLog
from app.models.token import TokenUsage
from app.schemas.task import TaskCreate, TaskConfig, TaskUpdate, ScheduleConfig
from app.agent.engine import AgentEngine
from app.exceptions import BizException, ErrorCode


def calculate_next_run(schedule_type: str, schedule_config: ScheduleConfig, from_time: datetime = None) -> datetime | None:
    """计算下次执行时间
    
    注意：用户设置的 cron_hour/cron_minute 是本地时间（北京时间 UTC+8），
    需要转换为 UTC 时间存储，以便与前端显示保持一致。
    """
    # 北京时间偏移量（小时）
    LOCAL_TZ_OFFSET = 8
    
    if from_time is None:
        from_time = datetime.utcnow()
    
    if schedule_type == "interval":
        # 间隔执行
        if schedule_config.interval_minutes:
            return from_time + timedelta(minutes=schedule_config.interval_minutes)
    
    elif schedule_type == "cron":
        # Cron 定时执行
        if schedule_config.cron_hour is not None and schedule_config.cron_minute is not None:
            # 用户设置的是本地时间，需要转换为 UTC
            # 例如：用户设置 10:00 (北京时间)，对应 UTC 02:00
            utc_hour = (schedule_config.cron_hour - LOCAL_TZ_OFFSET) % 24
            
            # 计算今天的目标时间（UTC）
            target = from_time.replace(
                hour=utc_hour,
                minute=schedule_config.cron_minute,
                second=0,
                microsecond=0
            )
            
            # 如果本地时间跨天（如设置凌晨1点，UTC是前一天17点），需要调整日期
            if schedule_config.cron_hour < LOCAL_TZ_OFFSET:
                # 本地时间的凌晨对应UTC的前一天晚上，不需要额外处理
                pass
            
            # 如果目标时间已过，设为明天
            if target <= from_time:
                target += timedelta(days=1)
            
            # 处理星期几的限制
            if schedule_config.cron_day_of_week and schedule_config.cron_day_of_week != "*":
                days_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
                allowed_days = [days_map[d.strip().lower()] for d in schedule_config.cron_day_of_week.split(",") if d.strip().lower() in days_map]
                
                if allowed_days:
                    # 找到下一个允许的日期
                    for _ in range(7):
                        if target.weekday() in allowed_days:
                            break
                        target += timedelta(days=1)
            
            return target
    
    elif schedule_type == "once":
        # 一次性执行
        if schedule_config.once_at and schedule_config.once_at > from_time:
            return schedule_config.once_at
    
    return None


class TaskService:
    """任务服务 - 任务 CRUD 和执行"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_task(self, data: TaskCreate) -> Task:
        """创建任务"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"
        
        # 验证定时配置完整性：启用定时必须有完整配置
        schedule_enabled = data.schedule_enabled
        if schedule_enabled and (not data.schedule_type or not data.schedule_config):
            # 配置不完整时强制禁用定时
            schedule_enabled = False
        
        # 计算下次执行时间
        next_run_at = None
        if schedule_enabled and data.schedule_type and data.schedule_config:
            next_run_at = calculate_next_run(data.schedule_type, data.schedule_config)
        
        task = Task(
            id=task_id,
            name=data.name,
            description=data.description,
            entry_urls=json.dumps(data.entry_urls),
            model=data.model,
            extract_model=data.extract_model,
            config=json.dumps(data.config.model_dump()) if data.config else None,
            status="pending",
            execution_count=0,
            schedule_enabled=schedule_enabled,
            schedule_type=data.schedule_type if schedule_enabled else None,
            schedule_config=json.dumps(data.schedule_config.model_dump()) if data.schedule_config and schedule_enabled else None,
            next_run_at=next_run_at
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task
    
    async def update_task(self, task_id: str, data: TaskUpdate) -> Task:
        """更新任务"""
        task = await self.get_task(task_id)
        
        if task.status == "running":
            raise BizException(40003, "任务正在执行，无法修改")
        
        if data.name is not None:
            task.name = data.name
        if data.description is not None:
            task.description = data.description
        if data.entry_urls is not None:
            task.entry_urls = json.dumps(data.entry_urls)
        if data.model is not None:
            task.model = data.model
        if data.extract_model is not None:
            task.extract_model = data.extract_model
        if data.config is not None:
            task.config = json.dumps(data.config.model_dump())
        
        # 更新定时配置
        if data.schedule_enabled is not None:
            if data.schedule_enabled:
                # 启用定时：更新提供的配置
                if data.schedule_type is not None:
                    task.schedule_type = data.schedule_type
                if data.schedule_config is not None:
                    task.schedule_config = json.dumps(data.schedule_config.model_dump())
                
                # 验证配置完整性：必须有 type 和 config 才能启用
                if task.schedule_type and task.schedule_config:
                    task.schedule_enabled = True
                    schedule_config = ScheduleConfig(**json.loads(task.schedule_config))
                    task.next_run_at = calculate_next_run(task.schedule_type, schedule_config)
                else:
                    # 配置不完整，强制禁用
                    task.schedule_enabled = False
                    task.next_run_at = None
            else:
                # 禁用定时时清空相关字段
                task.schedule_enabled = False
                task.schedule_type = None
                task.schedule_config = None
                task.next_run_at = None
        elif data.schedule_type is not None or data.schedule_config is not None:
            # 只更新部分定时配置
            if data.schedule_type is not None:
                task.schedule_type = data.schedule_type
            if data.schedule_config is not None:
                task.schedule_config = json.dumps(data.schedule_config.model_dump())
            
            # 重新计算下次执行时间
            if task.schedule_enabled and task.schedule_type and task.schedule_config:
                schedule_config = ScheduleConfig(**json.loads(task.schedule_config))
                task.next_run_at = calculate_next_run(task.schedule_type, schedule_config)
        
        await self.db.commit()
        await self.db.refresh(task)
        return task
    
    async def get_task(self, task_id: str) -> Task:
        """获取任务"""
        task = await self.db.get(Task, task_id)
        if not task:
            raise BizException(*ErrorCode.TASK_NOT_FOUND)
        return task
    
    async def list_tasks(self, skip: int = 0, limit: int = 20) -> tuple[list[Task], int]:
        """获取任务列表"""
        # 查询总数
        count_result = await self.db.execute(select(func.count(Task.id)))
        total = count_result.scalar()
        
        # 查询列表
        result = await self.db.execute(
            select(Task)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        tasks = list(result.scalars().all())
        
        return tasks, total
    
    async def delete_task(self, task_id: str) -> None:
        """删除任务及其所有执行记录"""
        task = await self.get_task(task_id)
        
        if task.status == "running":
            raise BizException(40003, "任务正在执行，无法删除")
        
        # 删除所有执行记录的日志和token记录
        # 注意：先删除TokenUsage（有log_id外键引用ExecutionLog），再删除ExecutionLog
        await self.db.execute(
            TokenUsage.__table__.delete().where(TokenUsage.task_id == task_id)
        )
        await self.db.execute(
            ExecutionLog.__table__.delete().where(ExecutionLog.task_id == task_id)
        )
        
        # 删除所有执行记录
        await self.db.execute(
            Execution.__table__.delete().where(Execution.task_id == task_id)
        )
        
        # 删除任务
        await self.db.delete(task)
        await self.db.commit()
    
    # ============ 执行记录相关方法 ============
    
    async def create_execution(self, task_id: str) -> Execution:
        """创建新的执行记录"""
        task = await self.get_task(task_id)
        
        # 计算执行序号
        execution_number = task.execution_count + 1
        
        # 生成执行ID
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"
        
        execution = Execution(
            id=execution_id,
            task_id=task_id,
            status="running",
            execution_number=execution_number,
            started_at=datetime.utcnow()
        )
        
        self.db.add(execution)
        
        # 更新任务状态
        task.status = "running"
        task.execution_count = execution_number
        task.last_execution_id = execution_id
        
        await self.db.commit()
        await self.db.refresh(execution)
        return execution
    
    async def get_execution(self, execution_id: str) -> Execution:
        """获取执行记录"""
        execution = await self.db.get(Execution, execution_id)
        if not execution:
            raise BizException(40401, "执行记录不存在")
        return execution
    
    async def run_execution(
        self, 
        execution_id: str,
        on_step: Callable[[dict], None] | None = None
    ) -> Execution:
        """执行任务（execution已创建且状态为running）"""
        execution = await self.get_execution(execution_id)
        task = await self.get_task(execution.task_id)
        
        try:
            # 解析配置
            config = None
            if task.config:
                config = TaskConfig(**json.loads(task.config))
            
            # 执行 Agent
            engine = AgentEngine(self.db)
            result = await engine.execute_task(task, execution, config, on_step)
            
            # 更新执行结果
            execution.status = "completed"
            execution.result = result
            execution.completed_at = datetime.utcnow()
            
            # 更新任务状态
            task.status = "completed"
            
            await self.db.commit()
            
        except Exception as e:
            # 记录错误
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            
            # 更新任务状态
            task.status = "failed"
            
            await self.db.commit()
            raise
        
        return execution
    
    async def cancel_execution(self, execution_id: str) -> Execution:
        """取消执行"""
        execution = await self.get_execution(execution_id)
        
        if execution.status not in ("pending", "running"):
            raise BizException(40004, "只能取消等待中或执行中的任务")
        
        execution.status = "cancelled"
        execution.completed_at = datetime.utcnow()
        
        # 更新任务状态
        task = await self.get_task(execution.task_id)
        task.status = "cancelled"
        
        await self.db.commit()
        
        return execution
    
    async def get_execution_logs(self, execution_id: str) -> list[ExecutionLog]:
        """获取执行记录的日志"""
        await self.get_execution(execution_id)  # 确保执行记录存在
        
        result = await self.db.execute(
            select(ExecutionLog)
            .where(ExecutionLog.execution_id == execution_id)
            .order_by(ExecutionLog.step_number)
        )
        return list(result.scalars().all())
    
    # ============ 旧方法保留兼容 ============
    
    async def get_task_logs(self, task_id: str) -> list[ExecutionLog]:
        """获取任务最新执行的日志"""
        task = await self.get_task(task_id)
        
        if not task.last_execution_id:
            return []
        
        return await self.get_execution_logs(task.last_execution_id)
    
    # ============ 定时任务相关方法 ============
    
    async def get_scheduled_tasks(self) -> list[Task]:
        """获取所有需要执行的定时任务"""
        now = datetime.utcnow()
        
        result = await self.db.execute(
            select(Task)
            .where(
                Task.schedule_enabled == True,
                Task.next_run_at <= now,
                Task.status != "running"  # 排除正在运行的任务
            )
        )
        return list(result.scalars().all())
    
    async def create_scheduled_execution(self, task_id: str) -> Execution:
        """创建定时执行记录（执行后更新下次运行时间）"""
        task = await self.get_task(task_id)
        
        # 创建执行记录
        execution = await self.create_execution(task_id)
        
        # 更新定时信息
        task.last_scheduled_at = datetime.utcnow()
        
        # 计算下次执行时间
        if task.schedule_type == "once":
            # 一次性任务执行后禁用定时
            task.schedule_enabled = False
            task.next_run_at = None
        elif task.schedule_config:
            schedule_config = ScheduleConfig(**json.loads(task.schedule_config))
            task.next_run_at = calculate_next_run(task.schedule_type, schedule_config)
        
        await self.db.commit()
        return execution
    
    async def get_all_scheduled_tasks(self) -> list[Task]:
        """获取所有启用了定时的任务（用于调度器启动时加载）"""
        result = await self.db.execute(
            select(Task)
            .where(Task.schedule_enabled == True)
        )
        return list(result.scalars().all())
