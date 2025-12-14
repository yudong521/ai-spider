"""自定义异常和错误码定义"""


class BizException(Exception):
    """业务异常基类 - 直接抛出，由全局处理器捕获"""
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class ErrorCode:
    """错误码定义"""
    # 任务相关 400xx
    TASK_NOT_FOUND = (40001, "任务不存在")
    TASK_ALREADY_RUNNING = (40002, "任务正在执行中")
    TASK_CANNOT_CANCEL = (40003, "任务无法取消")
    
    # 模型相关 401xx
    MODEL_NOT_SUPPORTED = (40101, "不支持的模型")
    API_KEY_NOT_CONFIGURED = (40102, "API Key 未配置")
    
    # 配置相关 402xx
    CONFIG_NOT_FOUND = (40201, "配置项不存在")
    
    # 认证相关 403xx
    UNAUTHORIZED = (40301, "未授权访问")
    INVALID_SECRET_KEY = (40302, "密钥无效")
    
    # 系统错误 500xx
    INTERNAL_ERROR = (50000, "服务器内部错误")
    AGENT_EXECUTION_ERROR = (50001, "Agent 执行错误")

