from backend.util import fetch_url
import re, json

# 测试新浪财经API
url = 'https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022?paperCode=sz300300&source=lrb&type=0&page=1&num=10'

print('请求URL:', url)
raw_data = fetch_url(url, timeout=20, is_sina_var=True)

if raw_data:
    print('\n原始数据:', raw_data[:500], '...')  # 只打印前500个字符
    
    # 处理JSONP格式
    json_str = re.sub(r'^hqccall\d+\(', '', raw_data).rstrip(')')
    print('\nJSON字符串:', json_str[:500], '...')  # 只打印前500个字符
    
    try:
        data = json.loads(json_str)
        print('\n解析成功！')
        
        # 查看数据结构
        print('\n数据结构:')
        print('- 顶级键:', list(data.keys()))
        
        # 查看result部分
        if 'result' in data:
            print('\nresult:', data['result'])
        
        # 查看data部分
        if 'data' in data:
            data_section = data['data']
            print('\ndata键:', list(data_section.keys()))
            
            # 查看report_list
            if 'report_list' in data_section:
                report_list = data_section['report_list']
                print('\nreport_list类型:', type(report_list))
                print('report_list长度:', len(report_list))
                
                if report_list:
                    first_report = report_list[0]
                    print('\n第一个report键:', list(first_report.keys()))
                    print('report_date:', first_report.get('report_date'))
                    print('report_type:', first_report.get('report_type'))
                    
                    # 查看财务数据
                    if 'data' in first_report:
                        report_data = first_report['data']
                        print('\nreport_data长度:', len(report_data))
                        print('\n前5个财务项:')
                        for item in report_data[:5]:
                            print(f"  - field: {item.get('item_field')}, title: {item.get('item_title')}, value: {item.get('item_value')}")
    except Exception as e:
        print('\n解析失败:', str(e))
        import traceback
        traceback.print_exc()
else:
    print('\n获取数据失败')