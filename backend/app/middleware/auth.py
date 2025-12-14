"""认证中间件 - 验证系统密钥"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import async_session
from app.models.config import Config


class AuthMiddleware(BaseHTTPMiddleware):
    """系统密钥认证中间件"""
    
    # 白名单路径（不需要验证的路径）
    WHITELIST_PATHS = [
        "/health",
        "/api/configs/auth/status",
        "/api/configs/auth/verify",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        path = request.url.path
        
        # 白名单路径跳过验证
        if self._is_whitelisted(path):
            return await call_next(request)
        
        # 获取系统密钥配置
        system_key = await self._get_system_secret_key()
        
        # 如果系统密钥为空，跳过验证（未启用认证）
        if not system_key:
            return await call_next(request)
        
        # 验证请求头中的密钥（优先）或 URL query 参数中的密钥（用于 SSE 等不支持自定义头的场景）
        request_key = request.headers.get("X-Secret-Key", "") or request.query_params.get("key", "")
        
        if request_key != system_key:
            return JSONResponse(
                status_code=401,
                content={
                    "code": 40301,
                    "message": "未授权访问",
                    "data": None
                }
            )
        
        return await call_next(request)
    
    def _is_whitelisted(self, path: str) -> bool:
        """检查路径是否在白名单中"""
        for whitelist_path in self.WHITELIST_PATHS:
            if path.startswith(whitelist_path):
                return True
        return False
    
    async def _get_system_secret_key(self) -> str:
        """从数据库获取系统密钥"""
        async with async_session() as db:
            config = await db.get(Config, "system_secret_key")
            return config.value if config else ""

