"""模型适配器 - 统一千问和智谱模型接口"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_openai import ChatOpenAI

from app.models.config import Config
from app.exceptions import BizException, ErrorCode


class ModelAdapter:
    """模型适配器"""
    
    # 支持的模型配置
    MODELS = {
        # 千问系列
        "qwen3-max": {
            "provider": "dashscope",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model_name": "qwen3-max",
            "description": "千问3-Max (推荐)"
        },
        # 智谱系列
        "glm-4.6": {
            "provider": "zhipu",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model_name": "glm-4.6",
            "description": "智谱 GLM-4.6"
        }
    }
    
    # 提供商对应的 API Key 配置键名
    API_KEY_CONFIG = {
        "dashscope": "dashscope_api_key",
        "zhipu": "zhipu_api_key"
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_api_key(self, provider: str) -> str:
        """从数据库获取 API Key"""
        config_key = self.API_KEY_CONFIG.get(provider)
        if not config_key:
            raise BizException(*ErrorCode.MODEL_NOT_SUPPORTED)
        
        result = await self.db.execute(
            select(Config).where(Config.key == config_key)
        )
        config = result.scalar_one_or_none()
        
        if not config or not config.value:
            raise BizException(*ErrorCode.API_KEY_NOT_CONFIGURED)
        
        return config.value
    
    async def get_llm(
        self, 
        model_key: str, 
        temperature: float = 0.5,
        callbacks: list = None
    ) -> ChatOpenAI:
        """获取 LLM 实例"""
        if model_key not in self.MODELS:
            raise BizException(*ErrorCode.MODEL_NOT_SUPPORTED)
        
        model_config = self.MODELS[model_key]
        api_key = await self.get_api_key(model_config["provider"])
        
        return ChatOpenAI(
            api_key=api_key,
            base_url=model_config["base_url"],
            model=model_config["model_name"],
            temperature=temperature,
            timeout=600,
            callbacks=callbacks or []
        )
    
    @classmethod
    def list_models(cls) -> list[dict]:
        """列出所有支持的模型"""
        return [
            {
                "key": key,
                "name": config["model_name"],
                "provider": config["provider"],
                "description": config.get("description")
            }
            for key, config in cls.MODELS.items()
        ]

