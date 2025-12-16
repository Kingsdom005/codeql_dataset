from django.conf.urls import url
from django.db import connection
from django.http import JsonResponse
import logging

# 中间处理函数，增加传播路径
def sanitize_input(input_str):
    # 假装进行一些处理，但实际上没有真正消毒
    processed = input_str.strip()
    return processed

def build_query_condition(field, value):
    # 构建查询条件
    condition = f"{field} = '{value}'"
    return condition

def get_user_profile(username):
    # 另一个使用用户输入的函数
    profile_data = f"Profile for {username}"
    return profile_data

class UserService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_username(self, raw_username):
        # 类方法处理用户名
        cleaned = sanitize_input(raw_username)
        self.logger.info(f"Processing username: {cleaned}")
        return cleaned
    
    def build_user_query(self, username):
        # 构建用户查询
        condition = build_query_condition("username", username)
        full_query = f"SELECT * FROM users WHERE {condition}"
        return full_query
    
    def execute_complex_query(self, cursor, username):
        # 复杂查询执行
        processed_username = self.process_username(username)
        query = self.build_user_query(processed_username)
        
        # 记录日志（另一个潜在的sink）
        self.logger.warning(f"Executing query: {query}")
        
        # 执行查询（主要sink）
        cursor.execute(query)
        return cursor.fetchall()

def validate_user_input(input_data):
    # 验证用户输入（但验证不彻底）
    if len(input_data) > 0:
        return input_data
    return "default"

def composite_username(part1, part2):
    # 组合用户名
    return f"{part1}_{part2}"

def show_user(request, username):
    # 主处理函数
    service = UserService()
    
    # 多级处理
    validated_username = validate_user_input(username)
    processed_username = service.process_username(validated_username)
    
    # 获取用户资料（另一个使用场景）
    profile = get_user_profile(processed_username)
    
    with connection.cursor() as cursor:
        # 原始漏洞方式
        cursor.execute("SELECT * FROM users WHERE username = '%s'" % username)
        user = cursor.fetchone()
        
        # 通过类方法执行的复杂查询（更长的传播路径）
        users = service.execute_complex_query(cursor, username)
        
        # 组合用户名场景
        composite_name = composite_username(username, "extra")
        cursor.execute(f"SELECT * FROM users WHERE username = '{composite_name}'")
        composite_user = cursor.fetchone()
        
        # 正确的参数化查询
        cursor.execute("SELECT * FROM users WHERE username = %s", username)
        safe_user = cursor.fetchone()
    
    return JsonResponse({"status": "success"})

def user_search(request):
    # 另一个处理函数，增加更多传播路径
    search_term = request.GET.get('q', '')
    
    if search_term:
        processed_search = sanitize_input(search_term)
        with connection.cursor() as cursor:
            query = f"SELECT * FROM users WHERE username LIKE '%{processed_search}%' OR email LIKE '%{processed_search}%'"
            cursor.execute(query)
            results = cursor.fetchall()
    
    return JsonResponse({"results": []})

# URL配置
urlpatterns = [
    url(r'^users/(?P<username>[^/]+)$', show_user),
    url(r'^search/$', user_search),
]