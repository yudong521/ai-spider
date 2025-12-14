"""定时任务调度服务"""

import asyncio
import logging
from datetime import datetime
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.database import async_session
from app.services.task_service import TaskService

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务调度服务"""
    
    _instance = None
    _scheduler: AsyncIOScheduler = None
    _running_tasks: set[str] = set()  # 正在执行的任务ID集合
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._scheduler is None:
            self._scheduler = AsyncIOScheduler()
    
    async def start(self):
        """启动调度器"""
        if not self._scheduler.running:
            # 添加主检查任务 - 每分钟检查一次待执行的定时任务
            self._scheduler.add_job(
                self._check_scheduled_tasks,
                IntervalTrigger(seconds=30),
                id="check_scheduled_tasks",
                name="检查定时任务",
                replace_existing=True
            )
            
            self._scheduler.start()
            logger.info("定时任务调度器已启动")
    
    async def shutdown(self):
        """关闭调度器"""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("定时任务调度器已关闭")
    
    async def _check_scheduled_tasks(self):
        """检查并执行到期的定时任务"""
        try:
            async with async_session() as db:
                service = TaskService(db)
                tasks = await service.get_scheduled_tasks()
                
                for task in tasks:
                    # 跳过正在执行的任务
                    if task.id in self._running_tasks:
                        logger.debug(f"任务 {task.id} 正在执行，跳过")
                        continue
                    
                    logger.info(f"定时任务触发: {task.name} (ID: {task.id})")
                    
                    # 在后台执行任务
                    asyncio.create_task(self._execute_scheduled_task(task.id))
                    
        except Exception as e:
            logger.error(f"检查定时任务时出错: {e}")
    
    async def _execute_scheduled_task(self, task_id: str):
        """执行定时任务"""
        self._running_tasks.add(task_id)
        
        try:
            async with async_session() as db:
                service = TaskService(db)
                
                # 创建执行记录
                execution = await service.create_scheduled_execution(task_id)
                logger.info(f"定时任务开始执行: task_id={task_id}, execution_id={execution.id}")
                
                # 执行任务
                await service.run_execution(execution.id)
                logger.info(f"定时任务执行完成: task_id={task_id}, execution_id={execution.id}")
                
        except Exception as e:
            logger.error(f"定时任务执行失败: task_id={task_id}, error={e}")
        finally:
            self._running_tasks.discard(task_id)
    
    def get_scheduler_status(self) -> dict:
        """获取调度器状态"""
        return {
            "running": self._scheduler.running if self._scheduler else False,
            "running_tasks": list(self._running_tasks),
            "jobs_count": len(self._scheduler.get_jobs()) if self._scheduler else 0
        }


# 全局调度器实例
scheduler_service = SchedulerService()

