#!/usr/bin/env python
import requests
import json
import sys
import logging
from urllib.parse import urljoin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_api")

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """测试健康检查端点"""
    logger.info("测试健康检查端点...")
    response = requests.get(urljoin(BASE_URL, "../health"))
    logger.info(f"状态码: {response.status_code}")
    logger.info(f"响应: {response.json()}")
    return response.status_code == 200

def test_api_status():
    """测试API状态端点"""
    logger.info("测试API状态端点...")
    response = requests.get(urljoin(BASE_URL, "../status"))
    logger.info(f"状态码: {response.status_code}")
    logger.info(f"响应: {response.json()}")
    return response.status_code == 200

def test_recommendation_system_status(token=None):
    """测试推荐系统状态端点"""
    logger.info("测试推荐系统状态端点...")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(
        urljoin(BASE_URL, "/recommendations/system-status"),
        headers=headers
    )
    logger.info(f"状态码: {response.status_code}")
    if response.status_code == 200:
        logger.info(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        logger.error(f"响应: {response.text}")
    return response.status_code == 200

def login(username, password):
    """登录并获取令牌"""
    logger.info(f"尝试登录用户: {username}...")
    response = requests.post(
        urljoin(BASE_URL, "/login/access-token"),
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        token = response.json().get("access_token")
        logger.info("登录成功，获取到令牌")
        return token
    logger.error(f"登录失败: {response.text}")
    return None

def test_job_recommendations(resume_id, token=None):
    """测试职位推荐API"""
    logger.info(f"测试职位推荐API，简历ID: {resume_id}...")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(
        urljoin(BASE_URL, "/recommendations/jobs"),
        params={"resume_id": resume_id, "limit": 5, "include_details": True},
        headers=headers
    )
    logger.info(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            recommendations = data.get("data", [])
            logger.info(f"获取到 {len(recommendations)} 个职位推荐")
            if recommendations:
                for i, rec in enumerate(recommendations[:3], 1):
                    logger.info(f"  {i}. {rec['title']} - 匹配度: {rec['match_score']:.2f}")
            return True
        else:
            logger.error(f"API返回错误: {data.get('message')}")
    else:
        logger.error(f"响应: {response.text}")
    return False

def test_resume_recommendations(job_id, token=None):
    """测试简历推荐API"""
    logger.info(f"测试简历推荐API，职位ID: {job_id}...")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(
        urljoin(BASE_URL, "/recommendations/resumes"),
        params={"job_id": job_id, "limit": 5, "include_details": True},
        headers=headers
    )
    logger.info(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            recommendations = data.get("data", [])
            logger.info(f"获取到 {len(recommendations)} 个简历推荐")
            if recommendations:
                for i, rec in enumerate(recommendations[:3], 1):
                    logger.info(f"  {i}. {rec['title']} - 匹配度: {rec['match_score']:.2f}")
            return True
        else:
            logger.error(f"API返回错误: {data.get('message')}")
    else:
        logger.error(f"响应: {response.text}")
    return False

def main():
    """主函数"""
    logger.info("=== 开始测试API ===")
    
    # 测试健康检查和状态端点
    test_health()
    test_api_status()
    
    # 登录获取令牌
    print("\n请输入测试用户信息:")
    username = input("用户名: ")
    password = input("密码: ")
    token = login(username, password)
    
    if not token:
        logger.error("未能获取令牌，无法进行需要认证的测试")
        return False
    
    # 测试推荐系统状态
    test_recommendation_system_status(token)
    
    # 测试推荐API
    print("\n请输入测试ID:")
    resume_id = input("简历ID: ")
    job_id = input("职位ID: ")
    
    if resume_id:
        test_job_recommendations(resume_id, token)
    
    if job_id:
        test_resume_recommendations(job_id, token)
    
    logger.info("=== API测试完成 ===")
    return True

if __name__ == "__main__":
    main() 