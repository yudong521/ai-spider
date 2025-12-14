"""Agent 工具定义"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from langchain_core.tools import tool
from crawl4ai import AsyncWebCrawler

from app.agent.prompts import EXTRACT_PROMPT_TEMPLATE


# 创建线程池用于执行 Playwright 操作（解决 Windows 子进程问题）
_crawler_executor = ThreadPoolExecutor(max_workers=4)


@tool
def current_time() -> str:
    """获取当前时间。
    
    Returns:
        当前时间的字符串，格式为 YYYY-MM-DD HH:MM:SS
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _run_crawl_in_new_loop(url: str) -> str:
    """
    在新的事件循环中执行爬取
    （解决 Windows 上 uvicorn + Playwright 子进程问题）
    """
    # 创建新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        async def _crawl():
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url)
                return str(result.markdown)
        return loop.run_until_complete(_crawl())
    finally:
        loop.close()


async def crawl_and_extract(
    url: str, 
    user_task: str, 
    extract_llm
) -> str:
    """
    爬取 URL 并使用 extract_agent 提取信息
    
    Args:
        url: 要爬取的 URL
        user_task: 用户任务描述
        extract_llm: 提取用的 LLM 实例
    
    Returns:
        提取后的内容
    """
    # 在线程池中执行爬取（新线程 + 新事件循环，避免 Windows asyncio 子进程问题）
    loop = asyncio.get_event_loop()
    content = await loop.run_in_executor(_crawler_executor, _run_crawl_in_new_loop, url)
    
    # 构建提取 prompt
    prompt = EXTRACT_PROMPT_TEMPLATE.format(
        content=content,
        user_task=user_task
    )
    
    # 调用 extract_llm 提取信息
    response = await extract_llm.ainvoke(prompt)
    return response.content


def create_crawl_tool(user_task: str, extract_llm):
    """创建带上下文的爬取工具"""
    
    @tool
    async def crawl_url(url: str) -> str:
        """爬取指定URL的网页内容并提取相关信息。
        
        Args:
            url: 要爬取的网页URL，必须是完整的HTTP/HTTPS地址
        
        Returns:
            与用户任务相关的提取信息和相关链接
        """
        return await crawl_and_extract(url, user_task, extract_llm)
    
    return crawl_url

