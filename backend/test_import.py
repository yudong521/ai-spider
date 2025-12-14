"""测试导入"""
import sys
print("Starting test...", flush=True)
sys.path.insert(0, '.')

try:
    print("Importing app.config...", flush=True)
    from app.config import DATABASE_URL
    print(f"DATABASE_URL: {DATABASE_URL}", flush=True)
    
    print("Importing app.database...", flush=True)
    from app.database import Base
    print("Database imported", flush=True)
    
    print("Importing app.models...", flush=True)
    from app.models import Task
    print("Models imported", flush=True)
    
    print("Importing app.main...", flush=True)
    from app.main import app
    print("Import successful!", flush=True)
except Exception as e:
    print(f"Import failed: {e}", flush=True)
    import traceback
    traceback.print_exc()

