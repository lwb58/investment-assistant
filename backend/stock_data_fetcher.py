import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# 导入stock.py中的数据获取方法
from stock import (
    get_hk_stock_detail_from_eastmoney,
    get_stock_quotes_from_eastmoney,
    get_stock_quotes,
    get_stock_financial_data,
    dupont_analysis,
    get_stock_detail
)

class StockDataFetcher:
    """
    通用股票数据获取器，提供简化的接口获取股票各种数据，并使用缓存减少网络请求
    """
    
    def __init__(self, cache_dir: str = "data_cache"):
        """
        初始化股票数据获取器
        
        参数:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
    def _get_cache_file_path(self, stock_code: str, data_type: str) -> str:
        """
        获取缓存文件路径
        
        参数:
            stock_code: 股票代码
            data_type: 数据类型
            
        返回:
            缓存文件路径
        """
        return os.path.join(self.cache_dir, f"{stock_code}_{data_type}.json")
    
    def _is_cache_valid(self, cache_file: str, max_age_hours: int = 1) -> bool:
        """
        检查缓存是否有效
        
        参数:
            cache_file: 缓存文件路径
            max_age_hours: 缓存最大有效时间（小时）
            
        返回:
            缓存是否有效
        """
        if not os.path.exists(cache_file):
            return False
        
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        return datetime.now() - cache_time < timedelta(hours=max_age_hours)
    
    def _load_from_cache(self, stock_code: str, data_type: str) -> Optional[Dict[str, Any]]:
        """
        从缓存加载数据
        
        参数:
            stock_code: 股票代码
            data_type: 数据类型
            
        返回:
            缓存的数据，或None如果缓存无效
        """
        cache_file = self._get_cache_file_path(stock_code, data_type)
        if self._is_cache_valid(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"从缓存加载{stock_code}的{data_type}数据失败: {e}")
        return None
    
    def _save_to_cache(self, stock_code: str, data_type: str, data: Dict[str, Any]) -> None:
        """
        保存数据到缓存
        
        参数:
            stock_code: 股票代码
            data_type: 数据类型
            data: 要保存的数据
        """
        cache_file = self._get_cache_file_path(stock_code, data_type)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存{stock_code}的{data_type}数据到缓存失败: {e}")
    
    def get_basic_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息
        
        参数:
            stock_code: 股票代码
            
        返回:
            包含股票基本信息的字典
        """
        # 尝试从缓存加载
        cached_data = self._load_from_cache(stock_code, "basic")
        if cached_data:
            return cached_data
        
        # 根据股票代码判断是港股还是A股
        try:
            if len(stock_code) == 5 and stock_code.isdigit():
                # 港股
                data = get_hk_stock_detail_from_eastmoney(stock_code)
            else:
                # A股
                data = get_stock_detail(stock_code)
                
                # 对A股数据进行标准化处理，使其与港股格式一致
                if data:
                    standardized_data = {
                        "stock_name": data.get("stock_name", data.get("name", "未知")),
                        "total_market_cap": data.get("marketCap", "未知"),
                        "net_profit_ratio": data.get("net_profit_ratio", "未知"),
                        "roe_avg": data.get("roe", "未知"),
                        "operate_income": data.get("operateIncome", "未知")
                    }
                    data.update(standardized_data)
            
            if data:
                self._save_to_cache(stock_code, "basic", data)
                return data
        except Exception as e:
            print(f"获取{stock_code}的基本信息失败: {e}")
        
        return None
    
    def get_dupont_analysis(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取杜邦分析数据
        
        参数:
            stock_code: 股票代码
            
        返回:
            包含杜邦分析数据的字典
        """
        # 尝试从缓存加载
        cached_data = self._load_from_cache(stock_code, "dupont")
        if cached_data:
            return cached_data
        
        try:
            data = dupont_analysis(stock_code)
            if data and data.get("full_data"):
                # 对杜邦分析数据进行标准化处理，确保经营利润率等字段的一致性
                for item in data["full_data"]:
                    # 确保日期字段存在
                    if "date" not in item and "报告期" in item:
                        item["date"] = item["报告期"]
                    
                    # 确保经营利润率字段存在且格式正确
                    if "经营利润率(%)" not in item:
                        # 尝试从其他字段获取
                        if "经营利润率" in item:
                            # 如果经营利润率已经包含百分号，直接使用
                            if item["经营利润率"].endswith("%"):
                                item["经营利润率(%)"] = item["经营利润率"].rstrip("%")
                            else:
                                item["经营利润率(%)"] = item["经营利润率"]
                        elif "营业利润率" in item:
                            item["经营利润率(%)"] = item["营业利润率"]
                    
                    # 确保利息负担字段存在
                    if "利息负担(%)" not in item:
                        if "考虑利息负担" in item:
                            if item["考虑利息负担"].endswith("%"):
                                item["利息负担(%)"] = item["考虑利息负担"].rstrip("%")
                            else:
                                item["利息负担(%)"] = item["考虑利息负担"]
                    
                    # 确保净资产收益率字段存在
                    if "净资产收益率(%)" not in item and "净资产收益率" in item:
                        item["净资产收益率(%)"] = item["净资产收益率"]
                
                self._save_to_cache(stock_code, "dupont", data)
                return data
        except Exception as e:
            print(f"获取{stock_code}的杜邦分析数据失败: {e}")
        
        return None
    
    def get_financial_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取金融数据（利润等）
        
        参数:
            stock_code: 股票代码
            
        返回:
            包含金融数据的字典
        """
        # 尝试从缓存加载
        cached_data = self._load_from_cache(stock_code, "financial")
        if cached_data:
            return cached_data
        
        try:
            data = get_stock_financial_data(stock_code)
            if data:
                self._save_to_cache(stock_code, "financial", data)
                return data
        except Exception as e:
            print(f"获取{stock_code}的金融数据失败: {e}")
        
        return None
    
    def get_quote_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取行情数据
        
        参数:
            stock_code: 股票代码
            
        返回:
            包含行情数据的字典
        """
        # 行情数据更新频繁，缓存时间设为5分钟
        cache_file = self._get_cache_file_path(stock_code, "quote")
        if self._is_cache_valid(cache_file, max_age_hours=0.083):  # 5分钟
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"从缓存加载{stock_code}的行情数据失败: {e}")
        
        try:
            data = get_stock_quotes(stock_code)
            if data:
                self._save_to_cache(stock_code, "quote", data)
                return data
        except Exception as e:
            print(f"获取{stock_code}的行情数据失败: {e}")
        
        return None
    
    def clear_cache(self, stock_code: str) -> None:
        """
        清除指定股票代码的所有缓存文件
        
        参数:
            stock_code: 股票代码
        """
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.startswith(f"{stock_code}_")]
            for file in cache_files:
                file_path = os.path.join(self.cache_dir, file)
                os.remove(file_path)
                print(f"已清除缓存文件: {file}")
        except Exception as e:
            print(f"清除{stock_code}的缓存文件失败: {e}")

# 测试代码
if __name__ == "__main__":
    # 创建数据获取器实例
    fetcher = StockDataFetcher()
    
    # 测试巨子生物（港股，正确代码是02367）
    print("=== 测试巨子生物 (02367.HK) ===")
    
    # 清除缓存
    fetcher.clear_cache("02367")
    
    # 获取基本信息
    basic_info = fetcher.get_basic_info("02367")
    if basic_info:
        print(f"股票名称: {basic_info.get('stock_name', '未知')}")
        print(f"总市值: {basic_info.get('total_market_cap', '未知')}")
        print(f"净利润率: {basic_info.get('net_profit_ratio', '未知')}%")
        print(f"平均净资产收益率: {basic_info.get('roe_avg', '未知')}%")
    else:
        print("获取基本信息失败")
    
    # 获取杜邦分析数据
    dupont_data = fetcher.get_dupont_analysis("02367")
    if dupont_data and dupont_data.get('full_data'):
        latest_data = dupont_data['full_data'][0]
        print(f"\n杜邦分析（最新数据）:")
        print(f"日期: {latest_data.get('date', '未知')}")
        print(f"净资产收益率: {latest_data.get('净资产收益率(%)', '未知')}%")
        print(f"经营利润率: {latest_data.get('经营利润率(%)', '未知')}%")
        print(f"利息负担: {latest_data.get('利息负担(%)', '未知')}%")
    else:
        print("获取杜邦分析数据失败")
    
    # 获取金融数据
    financial_data = fetcher.get_financial_data("02367")
    if financial_data:
        latest_year = max([k for k in financial_data.keys() if k.isdigit()], default=None)
        if latest_year:
            print(f"\n金融数据（{latest_year}年）:")
            print(f"营业收入: {financial_data[latest_year].get('revenue', '未知')}亿元")
            print(f"净利润: {financial_data[latest_year].get('netProfit', '未知')}亿元")
            print(f"毛利率: {financial_data[latest_year].get('grossMargin', '未知')}%")
            print(f"净利率: {financial_data[latest_year].get('netMargin', '未知')}%")
    else:
        print("获取金融数据失败")
    
    # 获取行情数据
    quote_data = fetcher.get_quote_data("02367")
    if quote_data and quote_data.get('coreQuotes'):
        print(f"\n行情数据:")
        print(f"当前价格: {quote_data['coreQuotes'].get('currentPrice', '未知')}")
        print(f"涨跌幅: {quote_data['coreQuotes'].get('changePercent', '未知')}%")
    else:
        print("获取行情数据失败")
    
    # 测试A股（招商银行）
    print("\n\n=== 测试招商银行 (600036.SH) ===")
    
    # 清除缓存
    fetcher.clear_cache("600036")
    
    # 获取基本信息
    basic_info = fetcher.get_basic_info("600036")
    if basic_info:
        print(f"股票名称: {basic_info.get('stock_name', '未知')}")
        print(f"总市值: {basic_info.get('marketCap', '未知')}")
        print(f"最新总营收: {basic_info.get('operateIncome', '未知')}")
    else:
        print("获取基本信息失败")
    
    # 获取杜邦分析数据
    dupont_data = fetcher.get_dupont_analysis("600036")
    if dupont_data and dupont_data.get('full_data'):
        latest_data = dupont_data['full_data'][0]
        print(f"\n杜邦分析（最新数据）:")
        print(f"日期: {latest_data.get('date', '未知')}")
        print(f"净资产收益率: {latest_data.get('净资产收益率(%)', '未知')}%")
        print(f"经营利润率: {latest_data.get('经营利润率(%)', '未知')}%")
        print(f"利息负担: {latest_data.get('利息负担(%)', '未知')}%")
    else:
        print("获取杜邦分析数据失败")
    
    # 获取金融数据
    financial_data = fetcher.get_financial_data("600036")
    if financial_data:
        latest_year = max([k for k in financial_data.keys() if k.isdigit()], default=None)
        if latest_year:
            print(f"\n金融数据（{latest_year}年）:")
            print(f"营业收入: {financial_data[latest_year].get('revenue', '未知')}亿元")
            print(f"净利润: {financial_data[latest_year].get('netProfit', '未知')}亿元")
            print(f"毛利率: {financial_data[latest_year].get('grossMargin', '未知')}%")
            print(f"净利率: {financial_data[latest_year].get('netMargin', '未知')}%")
    else:
        print("获取金融数据失败")
    
    # 获取行情数据
    quote_data = fetcher.get_quote_data("600036")
    if quote_data and quote_data.get('coreQuotes'):
        print(f"\n行情数据:")
        print(f"当前价格: {quote_data['coreQuotes'].get('currentPrice', '未知')}")
        print(f"涨跌幅: {quote_data['coreQuotes'].get('changePercent', '未知')}%")
    else:
        print("获取行情数据失败")
