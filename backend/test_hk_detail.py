import requests
import json

def test_hk_stock_detail(stock_id):
    """
    测试港股详情接口返回情况
    """
    try:
        # 先检查API路径是否正确，可能是/stock而不是/stocks
        url = f"http://localhost:8000/api/stock/{stock_id}"
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        
        data = response.json()
        print(f"港股 {stock_id} 详情接口测试结果：")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 检查关键字段是否存在
        print("\n=== 关键字段检查 ===")
        key_fields = ['total_market_cap', 'industry', 'common_shares', 'hk_common_shares', 'issued_common_shares']
        
        for field in key_fields:
            if field in data:
                print(f"✅ {field}: {data[field]}")
            else:
                print(f"❌ {field}: 缺失")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"解析响应失败: {e}")
        return None
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        return None

def test_eastmoney_api(stock_id):
    """
    测试东方财富API获取港股数据
    """
    try:
        # 使用正确的URL编码格式
        url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_CUSTOM_HKF10_FN_MAININDICATORMAX&columns=ORG_CODE%2CSECUCODE%2CSECURITY_CODE%2CSECURITY_NAME_ABBR%2CSECURITY_INNER_CODE%2CREPORT_DATE%2CBASIC_EPS%2CPER_NETCASH_OPERATE%2CBPS%2CBPS_NEDILUTED%2CCOMMON_ACS%2CPER_SHARES%2CISSUED_COMMON_SHARES%2CHK_COMMON_SHARES%2CTOTAL_MARKET_CAP%2CHKSK_MARKET_CAP%2COPERATE_INCOME%2COPERATE_INCOME_SQ%2COPERATE_INCOME_QOQ%2COPERATE_INCOME_QOQ_SQ%2CHOLDER_PROFIT%2CHOLDER_PROFIT_SQ%2CHOLDER_PROFIT_QOQ%2CHOLDER_PROFIT_QOQ_SQ%2CPE_TTM%2CPE_TTM_SQ%2CPB_TTM%2CPB_TTM_SQ%2CNET_PROFIT_RATIO%2CNET_PROFIT_RATIO_SQ%2CROE_AVG%2CROE_AVG_SQ%2CROA%2CROA_SQ%2CDIVIDEND_TTM%2CDIVIDEND_LFY%2CDIVI_RATIO%2CDIVIDEND_RATE%2CIS_CNY_CODE&filter=(SECUCODE%3D%22{stock_id}.HK%22)&pageNumber=1&pageSize=1&sortTypes=-1&sortColumns=REPORT_DATE&source=F10&client=PC&v=06695186382178545"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"\n东方财富API {stock_id} 测试结果：")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 检查关键字段是否存在
        if data.get('success') and data.get('result', {}).get('data'):
            eastmoney_data = data['result']['data'][0]
            print("\n=== 东方财富API关键字段 ===")
            key_fields_eastmoney = {
                'TOTAL_MARKET_CAP': '总市值',
                'HKSK_MARKET_CAP': '港股市值',
                'ISSUED_COMMON_SHARES': '已发行普通股',
                'HK_COMMON_SHARES': '港股普通股',
                'COMMON_ACS': '总权益',
                'PE_TTM': '市盈率TTM',
                'PB_TTM': '市净率TTM',
                'BASIC_EPS': '基本每股收益'
            }
            
            for field, description in key_fields_eastmoney.items():
                if field in eastmoney_data:
                    print(f"✅ {description} ({field}): {eastmoney_data[field]}")
                else:
                    print(f"❌ {description} ({field}): 缺失")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"东方财富API请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"解析东方财富API响应失败: {e}")
        return None
    except Exception as e:
        print(f"测试东方财富API过程中发生错误: {e}")
        return None

if __name__ == "__main__":
    # 测试巨子生物(02367)
    print("="*50)
    print("测试巨子生物(02367)")
    print("="*50)
    
    # 测试当前的detail接口
    detail_data = test_hk_stock_detail("02367")
    
    # 测试东方财富API
    eastmoney_data = test_eastmoney_api("02367")
    
    print("\n" + "="*50)
    print("测试完成")
    print("="*50)
