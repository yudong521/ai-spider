"""配置管理 API"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.response import ApiResponse
from app.schemas.config import ConfigResponse, ConfigUpdate, ModelInfo
from app.services.config_service import ConfigService
from app.agent.model_adapter import ModelAdapter

router = APIRouter()


class VerifyKeyRequest(BaseModel):
    """验证密钥请求"""
    key: str


class AuthStatusResponse(BaseModel):
    """认证状态响应"""
    required: bool  # 是否需要认证


class VerifyKeyResponse(BaseModel):
    """验证密钥响应"""
    valid: bool  # 密钥是否有效


@router.get("/auth/status", response_model=ApiResponse[AuthStatusResponse])
async def get_auth_status(
    db: AsyncSession = Depends(get_db)
):
    """获取系统认证状态（是否需要密钥）"""
    service = ConfigService(db)
    try:
        config = await service.get_config("system_secret_key")
        required = bool(config.value)
    except Exception:
        required = False
    return ApiResponse.success(AuthStatusResponse(required=required))


@router.post("/auth/verify", response_model=ApiResponse[VerifyKeyResponse])
async def verify_secret_key(
    data: VerifyKeyRequest,
    db: AsyncSession = Depends(get_db)
):
    """验证系统密钥"""
    service = ConfigService(db)
    try:
        config = await service.get_config("system_secret_key")
        # 如果系统密钥为空，任何密钥都有效
        if not config.value:
            valid = True
        else:
            valid = data.key == config.value
    except Exception:
        valid = False
    return ApiResponse.success(VerifyKeyResponse(valid=valid))


@router.get("", response_model=ApiResponse[list[ConfigResponse]])
async def get_all_configs(
    db: AsyncSession = Depends(get_db)
):
    """获取所有配置"""
    service = ConfigService(db)
    configs = await service.get_all_configs()
    return ApiResponse.success([ConfigResponse.model_validate(c) for c in configs])


@router.get("/{key}", response_model=ApiResponse[ConfigResponse])
async def get_config(
    key: str,
    db: AsyncSession = Depends(get_db)
):
    """获取配置项"""
    service = ConfigService(db)
    config = await service.get_config(key)
    return ApiResponse.success(ConfigResponse.model_validate(config))


@router.put("/{key}", response_model=ApiResponse[ConfigResponse])
async def update_config(
    key: str,
    data: ConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新配置项"""
    service = ConfigService(db)
    config = await service.update_config(key, data.value)
    return ApiResponse.success(ConfigResponse.model_validate(config))


@router.get("/api-key/{provider}/test", response_model=ApiResponse[dict])
async def test_api_key(
    provider: str,
    db: AsyncSession = Depends(get_db)
):
    """测试 API Key 连接"""
    service = ConfigService(db)
    is_valid = await service.test_api_key(provider)
    return ApiResponse.success({"provider": provider, "valid": is_valid})


@router.get("/models/list", response_model=ApiResponse[list[ModelInfo]])
async def list_models():
    """获取可用模型列表"""
    models = ModelAdapter.list_models()
    return ApiResponse.success([ModelInfo(**m) for m in models])

