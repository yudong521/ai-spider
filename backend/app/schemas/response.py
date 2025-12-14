"""统一响应模型"""

from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    code: int = 0
    message: str = "success"
    data: T | None = None
    
    @classmethod
    def success(cls, data: T = None, message: str = "success") -> "ApiResponse[T]":
        """成功响应"""
        return cls(code=0, message=message, data=data)
    
    @classmethod
    def error(cls, code: int, message: str) -> "ApiResponse":
        """错误响应"""
        return cls(code=code, message=message, data=None)

