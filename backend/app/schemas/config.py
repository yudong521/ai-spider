"""配置相关 schemas"""

from datetime import datetime
from pydantic import BaseModel


class ConfigResponse(BaseModel):
    """配置项响应"""
    key: str
    value: str
    description: str | None
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ConfigUpdate(BaseModel):
    """更新配置请求"""
    value: str


class ModelInfo(BaseModel):
    """模型信息"""
    key: str
    name: str
    provider: str
    description: str | None = None

