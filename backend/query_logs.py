"""临时脚本：查询 execution_logs 表"""
import sqlite3

conn = sqlite3.connect('data/crawler_agent.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("数据库中的表:")
for table in tables:
    print(f"  - {table[0]}")

print("\n" + "="*80)

# 查询 execution_logs 表
print("\nexecution_logs 表内容:")
try:
    cursor.execute("SELECT * FROM execution_logs")
    rows = cursor.fetchall()
    
    if not rows:
        print("  (表为空，没有数据)")
    else:
        # 获取列名
        columns = [desc[0] for desc in cursor.description]
        print(f"  列名: {columns}")
        print(f"  共 {len(rows)} 条记录:\n")
        
        for i, row in enumerate(rows, 1):
            print(f"  --- 记录 {i} ---")
            for col, val in zip(columns, row):
                # 截断过长的内容
                if isinstance(val, str) and len(val) > 200:
                    val = val[:200] + "..."
                print(f"    {col}: {val}")
            print()
except Exception as e:
    print(f"  查询失败: {e}")

conn.close()

