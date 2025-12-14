"""配置服务"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.config import Config
from app.exceptions import BizException, ErrorCode


class ConfigService:
    """配置服务 - 管理系统配置"""
    
    # 默认配置
    DEFAULT_CONFIGS = [
        ("dashscope_api_key", "", "阿里千问 API Key"),
        ("zhipu_api_key", "", "智谱 API Key"),
        ("default_model", "qwen3-max", "默认使用的模型"),
        ("system_secret_key", "", "系统访问密钥"),
    ]
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def init_configs(self) -> None:
        """初始化默认配置"""
        for key, value, description in self.DEFAULT_CONFIGS:
            existing = await self.db.get(Config, key)
            if not existing:
                config = Config(key=key, value=value, description=description)
                self.db.add(config)
        await self.db.commit()
    
    async def get_config(self, key: str) -> Config:
        """获取配置项"""
        config = await self.db.get(Config, key)
        if not config:
            raise BizException(*ErrorCode.CONFIG_NOT_FOUND)
        return config
    
    async def get_all_configs(self) -> list[Config]:
        """获取所有配置"""
        result = await self.db.execute(select(Config))
        return list(result.scalars().all())
    
    async def update_config(self, key: str, value: str) -> Config:
        """更新配置项"""
        config = await self.get_config(key)
        config.value = value
        config.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(config)
        return config
    
    async def test_api_key(self, provider: str) -> bool:
        """测试 API Key 是否有效"""
        key_map = {
            "dashscope": "dashscope_api_key",
            "zhipu": "zhipu_api_key"
        }
        
        config_key = key_map.get(provider)
        if not config_key:
            raise BizException(*ErrorCode.MODEL_NOT_SUPPORTED)
        
        config = await self.get_config(config_key)
        
        # 简单验证：非空即视为有效（实际可调用 API 测试）
        return bool(config.value)

