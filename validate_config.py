#!/usr/bin/env python3
"""
配置验证脚本

此脚本用于验证项目配置的正确性，确保所有必要的配置项都已正确设置
"""

import os
import sys
import json
from config import settings


def check_environment_variables():
    """
    检查环境变量配置
    """
    print("=== 检查环境变量配置 ===")
    
    # 检查必需的环境变量
    required_vars = [
        "AI_API_KEY",
        "EMAIL_SENDER",
        "EMAIL_RECEIVER",
        "EMAIL_PASSWORD"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = getattr(settings, var, "")
        if not value:
            missing_vars.append(var)
        else:
            # 对于密码等敏感信息，只显示部分内容
            if "PASSWORD" in var:
                print(f"✓ {var}: ********")
            else:
                print(f"✓ {var}: {value}")
    
    if missing_vars:
        print("\n❌ 缺少以下必需的环境变量:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    # 检查可选的环境变量
    optional_vars = [
        "AI_MODEL",
        "AI_API_URL",
        "EMAIL_SMTP_SERVER",
        "EMAIL_SMTP_PORT",
        "TAVILY_API_KEY"
    ]
    
    print("\n=== 检查可选的环境变量 ===")
    for var in optional_vars:
        value = getattr(settings, var, "")
        if value:
            print(f"✓ {var}: {value}")
        else:
            print(f"⚠️ {var}: 未设置（可选）")
    
    return True


def check_dependencies():
    """
    检查依赖是否已安装
    """
    print("\n=== 检查依赖项 ===")
    
    required_packages = [
        ('feedparser', 'feedparser'),
        ('requests', 'requests'),
        ('bs4', 'beautifulsoup4'),
        ('dotenv', 'python-dotenv'),
        ('pydantic', 'pydantic'),
        ('pydantic_settings', 'pydantic-settings'),
        ('markdown2', 'markdown2'),
        ('openai', 'openai')
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"⚠️ {package_name}: 未安装（可选）")
    
    if missing_packages:
        print(f"\n⚠️ 缺少以下可选依赖: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
    else:
        print("\n✓ 所有必需的依赖都已安装")
    
    # 即使缺少一些可选依赖，也允许继续
    return True


def check_file_structure():
    """
    检查文件结构是否正确
    """
    print("\n=== 检查文件结构 ===")
    
    required_files = [
        "main.py",
        "config.py",
        "subscription_manager.py",
        "news_fetcher.py",
        "ai_analyzer.py",
        "push_manager.py",
        "requirements.txt",
        ".env.example",
        ".github/workflows/rss-tool.yml"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file}")
    
    if missing_files:
        print("\n❌ 缺少以下必需的文件:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    return True


def check_github_workflow():
    """
    检查GitHub Actions workflow配置
    """
    print("\n=== 检查GitHub Actions workflow ===")
    
    workflow_file = ".github/workflows/rss-tool.yml"
    if not os.path.exists(workflow_file):
        print("❌ GitHub Actions workflow文件不存在")
        return False
    
    try:
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键配置
        checks = [
            ("schedule:" in content, "定时任务配置"),
            ("workflow_dispatch" in content, "手动触发配置"),
            ("secrets.AI_API_KEY" in content, "AI API Key配置"),
            ("secrets.EMAIL_SENDER" in content, "邮箱发送者配置"),
            ("secrets.EMAIL_RECEIVER" in content, "邮箱接收者配置"),
            ("secrets.EMAIL_PASSWORD" in content, "邮箱密码配置")
        ]
        
        all_checks_passed = True
        for passed, description in checks:
            if passed:
                print(f"✓ {description}")
            else:
                print(f"❌ {description}")
                all_checks_passed = False
        
        return all_checks_passed
    except Exception as e:
        print(f"❌ 检查workflow文件失败: {e}")
        return False


def check_gitignore():
    """
    检查.gitignore文件
    """
    print("\n=== 检查.gitignore文件 ===")
    
    if not os.path.exists(".gitignore"):
        print("❌ .gitignore文件不存在")
        return False
    
    try:
        with open(".gitignore", 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_entries = [
            ".env",
            "data/",
            "__pycache__/",
            "*.py[cod]",
            ".vscode/",
            ".idea/",
            ".DS_Store"
        ]
        
        missing_entries = []
        for entry in required_entries:
            if entry in content:
                print(f"✓ {entry}")
            else:
                missing_entries.append(entry)
                print(f"⚠️ {entry}: 建议添加")
        
        if ".env" not in content:
            print("\n❌ .env文件未添加到.gitignore，存在安全风险")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 检查.gitignore文件失败: {e}")
        return False


def main():
    """
    主函数
    """
    print("📋 配置验证脚本")
    print("=" * 60)
    
    checks = [
        check_file_structure,
        check_dependencies,
        check_environment_variables,
        check_github_workflow,
        check_gitignore
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有检查都通过了！")
        print("\n部署准备就绪，可以推送代码到GitHub并配置Secrets。")
        print("\n下一步：")
        print("1. 将代码推送到GitHub仓库")
        print("2. 在GitHub仓库设置Secrets")
        print("3. 启用GitHub Actions")
        print("4. 手动触发工作流测试")
        return 0
    else:
        print("❌ 存在配置问题，请修复后再部署。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
