from flask import Flask, render_template, request, redirect, url_for, abort
from flask_caching import Cache
import requests
import json
import time
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# 初始化缓存
cache = Cache(app)

# 飞书API相关函数
def get_tenant_access_token():
    """获取飞书tenant_access_token"""
    try:
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": app.config['FEISHU_APP_ID'],
            "app_secret": app.config['FEISHU_APP_SECRET']
        }
        
        app.logger.info(f"正在获取飞书tenant_access_token，APP_ID: {app.config['FEISHU_APP_ID']}")
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                app.logger.info("成功获取飞书tenant_access_token")
                return result.get("tenant_access_token")
            else:
                app.logger.error(f"飞书API返回错误码: {result.get('code')}, 错误信息: {result.get('msg')}")
                return None
        else:
            app.logger.error(f"获取tenant_access_token失败，状态码: {response.status_code}, 响应内容: {response.text}")
            return None
    except requests.exceptions.Timeout:
        app.logger.error("获取tenant_access_token超时")
        return None
    except requests.exceptions.RequestException as e:
        app.logger.error(f"请求tenant_access_token时发生异常: {str(e)}")
        return None
    except Exception as e:
        app.logger.error(f"获取tenant_access_token时发生未知异常: {str(e)}")
        return None

@cache.cached(timeout=3600, key_prefix='feishu_records')
def get_bitable_records():
    """获取飞书多维表格数据"""
    try:
        token = get_tenant_access_token()
        if not token:
            app.logger.error("无法获取飞书access_token，无法继续获取多维表格数据")
            return []
        
        app.logger.info(f"正在获取多维表格数据，BASE_ID: {app.config['BASE_ID']}, TABLE_ID: {app.config['TABLE_ID']}")
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app.config['BASE_ID']}/tables/{app.config['TABLE_ID']}/records"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                items = result.get("data", {}).get("items", [])
                app.logger.info(f"成功获取到{len(items)}条记录")
                return items
            else:
                app.logger.error(f"飞书API返回错误码: {result.get('code')}, 错误信息: {result.get('msg')}")
                return []
        else:
            app.logger.error(f"获取多维表格数据失败，状态码: {response.status_code}, 响应内容: {response.text}")
            return []
    except requests.exceptions.Timeout:
        app.logger.error("获取多维表格数据超时")
        return []
    except requests.exceptions.RequestException as e:
        app.logger.error(f"请求多维表格数据时发生异常: {str(e)}")
        return []
    except Exception as e:
        app.logger.error(f"获取多维表格数据时发生未知异常: {str(e)}")
        return []

# 路由
@app.route('/')
def index():
    """首页"""
    records = get_bitable_records()
    articles = []
    
    for record in records:
        fields = record.get("fields", {})
        article = {
            "id": record.get("record_id"),
            "title": fields.get("标题", ""),
            "quote": fields.get("金句输出", ""),
            "comment": fields.get("黄叔点评", ""),
            "content": fields.get("概要内容输出", "")
        }
        
        # 文章预览（前100字）
        if article["content"] and len(article["content"]) > 100:
            article["preview"] = article["content"][:100] + "..."
        else:
            article["preview"] = article["content"]
            
        articles.append(article)
    
    # Inside index function:
    return render_template('index.html', articles=articles, now=datetime.now())

@app.route('/article/<article_id>')
def article_detail(article_id):
    """文章详情页"""
    records = get_bitable_records()
    
    for record in records:
        if record.get("record_id") == article_id:
            fields = record.get("fields", {})
            article = {
                "id": record.get("record_id"),
                "title": fields.get("标题", ""),
                "quote": fields.get("金句输出", ""),
                "comment": fields.get("黄叔点评", ""),
                "content": fields.get("概要内容输出", "")
            }
            # 渲染详情页模板
            return render_template('detail.html', article=article, now=datetime.now())
    
    # 如果找不到文章，返回404
    abort(404)

@app.errorhandler(404)
def page_not_found(e):
    # Inside page_not_found function:
    return render_template('404.html', now=datetime.now()), 404

# 清除缓存的路由（可选，用于开发测试）
@app.route('/clear-cache')
def clear_cache():
    cache.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])