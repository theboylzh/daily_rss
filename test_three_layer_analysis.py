#!/usr/bin/env python3
"""测试三层分析架构"""

from ai_analyzer import AIAnalyzer

# 测试三层分析
def test_three_layer_analysis():
    print("测试三层分析架构...")
    
    # 创建分析器实例
    analyzer = AIAnalyzer()
    
    # 创建模拟新闻数据
    mock_news = [
        {"title": "我国12月经济增长迅猛，GDP同比增长5.2%"},
        {"title": "科技巨头发布全新AI模型，性能提升30%"},
        {"title": "全球气候变化峰会达成重要协议，2030年前减排45%"},
        {"title": "央行宣布降准0.5个百分点，释放流动性1.2万亿元"},
        {"title": "教育部门推出新政策，减轻学生课业负担"},
        {"title": "新能源汽车销量持续增长，12月同比增长40%"},
        {"title": "医疗改革新举措，药品集中采购降价50%以上"},
        {"title": "体育盛会成功举办，我国代表团获得金牌第一"},
        {"title": "人工智能在医疗领域取得突破，辅助诊断准确率达95%"},
        {"title": "航天事业新进展，新一代运载火箭成功发射"}
    ]
    
    print(f"使用 {len(mock_news)} 条模拟新闻进行测试")
    
    # 测试数据预处理
    print("\n1. 测试数据预处理...")
    news_markdown = analyzer._preprocess_news(mock_news)
    print("预处理完成，生成的Markdown格式：")
    print(news_markdown)
    
    # 测试三层分析
    print("\n2. 测试三层分析...")
    analysis_results = analyzer._three_layer_analysis(mock_news)
    
    # 验证结果
    print("\n3. 验证分析结果...")
    print(f"第一层分析结果类型: {type(analysis_results.get('first_layer'))}")
    print(f"第二层分析结果数量: {len(analysis_results.get('second_layer', []))}")
    print(f"第三层分析结果类型: {type(analysis_results.get('third_layer'))}")
    
    # 保存测试结果
    print("\n4. 保存测试结果...")
    analyzer._save_analysis_results(analysis_results, "2026-02-15-test")
    
    print("\n测试完成！三层分析架构运行正常。")

if __name__ == "__main__":
    test_three_layer_analysis()
