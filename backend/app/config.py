"""应用配置管理"""

from pathlib import Path

# 项目路径
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)

# 数据库配置
DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR}/crawler_agent.db"

# Agent 默认配置
DEFAULT_MODEL = "qwen3-max"
DEFAULT_MAX_DEPTH = 3
DEFAULT_MAX_PAGES = 20
DEFAULT_MAIN_TEMPERATURE = 0.5
DEFAULT_EXTRACT_TEMPERATURE = 0.0
DEFAULT_TIMEOUT = 600

