import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import warnings
import pandas as pd
warnings.filterwarnings('ignore')

def parse_sina_dupont_analysis(
    stock_id: str, 
    displaytype: str = "10",
    export_excel: bool = True  # 默认导出Excel（全量数据）
) -> Dict[str, Optional[List[Dict]]]:
    """
    全量解析新浪财经股票杜邦分析页面，提取所有指标（无遗漏）
    包含：核心指标 + 完整拆解指标（EBIT、利润总额、营业总收入等所有页面显示数据）
    """
    url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vFD_DupontAnalysis/stockid/{stock_id}/displaytype/{displaytype}.phtml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://finance.sina.com.cn/"
    }
    
    result = {
        "stock_id": stock_id,
        "full_data": None,  # 全量数据（核心+所有详细指标）
        "error": None
    }
    
    try:
        # 1. 发送请求并解析页面
        response = requests.get(url, headers=headers, timeout=20, verify=False)
        response.encoding = "gb2312"
        if response.status_code != 200:
            result["error"] = f"请求失败，状态码：{response.status_code}"
            return result
        
        soup = BeautifulSoup(response.text, "html.parser")
        full_data = []
        
        # 2. 提取所有有效报告期（严格匹配YYYY-MM-DD格式）
        report_dates = []
        for a in soup.find_all("a", attrs={"name": True}):
            date_str = a.get("name", "").strip()
            if len(date_str) == 10 and date_str.count("-") == 2:
                try:
                    year, month, day = map(int, date_str.split("-"))
                    if 2010 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                        report_dates.append(date_str)
                except:
                    continue
        
        if not report_dates:
            result["error"] = "未找到有效报告期（页面无数据或结构变更）"
            return result
        
        report_dates = list(set(report_dates))  # 去重
        report_dates.sort(reverse=True)  # 按时间倒序
        
        # 3. 全量提取每个报告期的所有指标（无遗漏）
        for date in report_dates:
            # 定位当前报告期的完整容器
            anchor = soup.find("a", attrs={"name": date})
            if not anchor:
                continue
            
            # 找到包含所有指标的.wrap容器（可能需要跨层级查找）
            wrap_div = anchor.find_next("div", class_="wrap")
            if not wrap_div:
                # 降级查找：如果找不到.wrap，查找包含.node的最近div
                wrap_div = anchor.find_next("div", string=lambda text: text and "净资产收益率" in text)
                if wrap_div:
                    wrap_div = wrap_div.find_parent("div", recursive=True)
            
            if not wrap_div:
                continue
            
            # 提取该容器下所有.node节点（所有层级的指标）
            node_divs = wrap_div.find_all("div", class_=lambda c: c and "node" in c)  # 匹配所有含node的class
            period_indicators = {"报告期": date}
            
            for node in node_divs:
                # 提取指标名称（支持多行拼接，如"归属母公司股东的\n销售净利率"）
                key_tags = node.find_all("p", class_=lambda c: c and "key" in c)
                value_tag = node.find("p", class_=lambda c: c and "value" in c)
                
                if not key_tags or not value_tag:
                    continue
                
                # 拼接指标名称（去除空格和换行）
                indicator_name = "".join([tag.get_text(strip=True) for tag in key_tags])
                indicator_value = value_tag.get_text(strip=True)
                
                # 避免重复指标（保留最后一个值）
                period_indicators[indicator_name] = indicator_value
            
            # 过滤无效数据（至少包含核心4个指标才保留）
            core_keys = {"净资产收益率", "归属母公司股东的销售净利率", "资产周转率(次)", "权益乘数"}
            if all(key in period_indicators for key in core_keys):
                full_data.append(period_indicators)
        
        if not full_data:
            result["error"] = "找到报告期，但未提取到有效指标（可能页面结构变更）"
            return result
        
        result["full_data"] = full_data
        
        # 4. 导出全量数据到Excel（包含所有指标）
        if export_excel:
            df = pd.DataFrame(full_data)
            # 重新排列列：报告期在前，核心指标次之，其他指标在后
            core_cols = ["报告期", "净资产收益率", "归属母公司股东的销售净利率", "资产周转率(次)", "权益乘数"]
            other_cols = [col for col in df.columns if col not in core_cols]
            df = df[core_cols + other_cols]
            # 保存Excel
            excel_filename = f"股票{stock_id}_杜邦分析全量数据.xlsx"
            df.to_excel(excel_filename, index=False, engine="openpyxl")
            print(f"\n✅ 全量数据已导出到：{excel_filename}")
        
    except requests.exceptions.Timeout:
        result["error"] = "请求超时（网络不稳定或页面响应慢）"
    except requests.exceptions.ConnectionError:
        result["error"] = "网络连接错误（请检查网络）"
    except Exception as e:
        result["error"] = f"解析失败：{str(e)}"
    
    return result


# ------------------- 测试示例（默认展示全量数据） -------------------
if __name__ == "__main__":
    stock_id = "300308"  # 可替换为任意股票代码（如601717、600036）
    print(f"\n{'='*60} 股票 {stock_id} 杜邦分析全量数据 {'='*60}")
    
    dupont_result = parse_sina_dupont_analysis(stock_id, export_excel=True)
    

    
    print(dupont_result)