import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量（如果存在）
load_dotenv()

class Config:
    # 飞书应用配置
    FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', 'cli_a7567701b276100c')
    FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', 't3FoUoPAFmfNUHkplEEZXe6Wena5l3K6')
    
    # 多维表格配置
    BASE_ID = os.getenv('BASE_ID', 'R3jwbqxMraFRgZsId9FcGdxRn1c')
    TABLE_ID = os.getenv('TABLE_ID', 'tbl5FExHceWLJaBQ')
    
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # 缓存配置
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300  # 缓存过期时间（秒）