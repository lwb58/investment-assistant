import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from util import DataSource

class TestGetStockFinancialData(unittest.TestCase):
    """测试get_stock_financial_data函数的单元测试"""
    
    @patch('util.get_stock_market')
    @patch('util.fetch_url')
    def test_valid_stock_code(self, mock_fetch_url, mock_get_stock_market):
        """测试有效股票代码的情况"""
        # 模拟市场获取函数返回结果
        mock_get_stock_market.return_value = 'sz'
        
        # 模拟API返回数据
        mock_response = {
            "result": {
                "status": {"code": 0},
                "data": {
                    "report_list": {
                        "20250930": {
                            "data": [
                                {"item_field": "BIZINCO", "item_title": "营业收入", "item_value": "1000000.00"},
                                {"item_field": "NETPROFIT", "item_title": "净利润", "item_value": "100000.00"},
                                {"item_field": "SGPMARGIN", "item_title": "销售毛利率", "item_value": "30.00"},
                                {"item_field": "SNPMARGINCONMS", "item_title": "销售净利率", "item_value": "10.00"},
                                {"item_field": "BASICEPS", "item_title": "基本每股收益", "item_value": "1.00"}
                            ]
                        },
                        "20250630": {
                            "data": [
                                {"item_field": "BIZINCO", "item_title": "营业收入", "item_value": "800000.00"},
                                {"item_field": "NETPROFIT", "item_title": "净利润", "item_value": "80000.00"},
                                {"item_field": "SGPMARGIN", "item_title": "销售毛利率", "item_value": "28.00"},
                                {"item_field": "SNPMARGINCONMS", "item_title": "销售净利率", "item_value": "10.00"},
                                {"item_field": "BASICEPS", "item_title": "基本每股收益", "item_value": "0.80"}
                            ]
                        }
                    }
                }
            }
        }
        
        mock_fetch_url.return_value = mock_response
        
        # 调用被测试函数
        result = DataSource.get_stock_financial_data('002920')
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['reportDate'], '20250930')
        self.assertEqual(result[0]['revenue'], '1000000.00')
        self.assertEqual(result[0]['netProfit'], '100000.00')
        self.assertEqual(result[0]['grossMargin'], '30.00')
        self.assertEqual(result[0]['netMargin'], '10.00')
        self.assertEqual(result[0]['eps'], '1.00')
        
        self.assertEqual(result[1]['reportDate'], '20250630')
        self.assertEqual(result[1]['revenue'], '800000.00')
        self.assertEqual(result[1]['netProfit'], '80000.00')
        
    @patch('util.get_stock_market')
    def test_unsupported_market(self, mock_get_stock_market):
        """测试不支持的股票市场"""
        # 模拟市场获取函数返回None
        mock_get_stock_market.return_value = None
        
        # 调用被测试函数
        result = DataSource.get_stock_financial_data('invalid_code')
        
        # 验证结果
        self.assertEqual(len(result), 0)
    
    @patch('util.get_stock_market')
    @patch('util.fetch_url')
    def test_api_error(self, mock_fetch_url, mock_get_stock_market):
        """测试API返回错误的情况"""
        # 模拟市场获取函数返回结果
        mock_get_stock_market.return_value = 'sz'
        
        # 模拟API返回错误
        mock_response = {
            "result": {
                "status": {"code": -1},
                "message": "API Error"
            }
        }
        
        mock_fetch_url.return_value = mock_response
        
        # 调用被测试函数
        result = DataSource.get_stock_financial_data('002920')
        
        # 验证结果
        self.assertEqual(len(result), 0)
    
    @patch('util.get_stock_market')
    @patch('util.fetch_url')
    def test_empty_report_list(self, mock_fetch_url, mock_get_stock_market):
        """测试report_list为空的情况"""
        # 模拟市场获取函数返回结果
        mock_get_stock_market.return_value = 'sz'
        
        # 模拟API返回空的report_list
        mock_response = {
            "result": {
                "status": {"code": 0},
                "data": {
                    "report_list": {}
                }
            }
        }
        
        mock_fetch_url.return_value = mock_response
        
        # 调用被测试函数
        result = DataSource.get_stock_financial_data('002920')
        
        # 验证结果
        self.assertEqual(len(result), 0)
    
    @patch('util.get_stock_market')
    @patch('util.fetch_url')
    def test_partial_data(self, mock_fetch_url, mock_get_stock_market):
        """测试部分数据缺失的情况"""
        # 模拟市场获取函数返回结果
        mock_get_stock_market.return_value = 'sz'
        
        # 模拟API返回部分数据
        mock_response = {
            "result": {
                "status": {"code": 0},
                "data": {
                    "report_list": {
                        "20250930": {
                            "data": [
                                {"item_field": "BIZINCO", "item_title": "营业收入", "item_value": "1000000.00"},
                                # 缺少净利润和利润率数据
                                {"item_field": "BASICEPS", "item_title": "基本每股收益", "item_value": "1.00"}
                            ]
                        }
                    }
                }
            }
        }
        
        mock_fetch_url.return_value = mock_response
        
        # 调用被测试函数
        result = DataSource.get_stock_financial_data('002920')
        
        # 验证结果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['reportDate'], '20250930')
        self.assertEqual(result[0]['revenue'], '1000000.00')
        # 验证缺失字段使用默认值
        self.assertEqual(result[0]['netProfit'], '0.00')
        self.assertEqual(result[0]['grossMargin'], '0.0')
        self.assertEqual(result[0]['netMargin'], '0.0')
    
    @patch('util.get_stock_market')
    @patch('util.fetch_url')
    def test_title_based_matching(self, mock_fetch_url, mock_get_stock_market):
        """测试基于标题的字段匹配"""
        # 模拟市场获取函数返回结果
        mock_get_stock_market.return_value = 'sz'
        
        # 模拟API返回数据，使用中文标题而不是英文字段
        mock_response = {
            "result": {
                "status": {"code": 0},
                "data": {
                    "report_list": {
                        "20250930": {
                            "data": [
                                {"item_field": "UNKNOWN_FIELD", "item_title": "营业收入", "item_value": "1000000.00"},
                                {"item_field": "UNKNOWN_FIELD2", "item_title": "净利润", "item_value": "100000.00"},
                                {"item_field": "UNKNOWN_FIELD3", "item_title": "毛利率", "item_value": "30.00"},
                                {"item_field": "UNKNOWN_FIELD4", "item_title": "销售净利率", "item_value": "10.00"},
                                {"item_field": "UNKNOWN_FIELD5", "item_title": "基本每股收益", "item_value": "1.00"}
                            ]
                        }
                    }
                }
            }
        }
        
        mock_fetch_url.return_value = mock_response
        
        # 调用被测试函数
        result = DataSource.get_stock_financial_data('002920')
        
        # 验证结果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['reportDate'], '20250930')
        self.assertEqual(result[0]['revenue'], '1000000.00')
        self.assertEqual(result[0]['netProfit'], '100000.00')
        self.assertEqual(result[0]['grossMargin'], '30.00')
        self.assertEqual(result[0]['netMargin'], '10.00')
        self.assertEqual(result[0]['eps'], '1.00')

if __name__ == '__main__':
    unittest.main()
