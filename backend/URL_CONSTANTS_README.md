# URL常量与返回值关联文档

本文档列出了项目中所有的URL常量及其对应的返回值示例，方便查看和使用。

## 东方财富URL常量

| 常量名 | 描述 | URL模板 | 返回值示例 |
|-------|------|---------|-----------|
| EASTMONEY_HK_MAIN_INDICATOR_MAX_URL | 东方财富港股F10主要指标 | `http://emweb.securities.eastmoney.com/F10_JJGK.aspx?type=web&code=02367.HK` | [伯特利_603596_东方财富港股F10主要指标_result.md](test/url_test_results/伯特利_603596_东方财富港股F10主要指标_result.md) |
| EASTMONEY_HK_QUOTE_URL | 东方财富港股行情 | `http://quote.eastmoney.com/hk/02367.html` | [伯特利_603596_东方财富港股行情_result.md](test/url_test_results/伯特利_603596_东方财富港股行情_result.md) |
| EASTMONEY_QUOTE_URL | 东方财富行情接口 | `http://push2.eastmoney.com/api/qt/stock/get?fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f107,f104,f105,f116,f184,f168,f169,f170,f213,f152,f15,f19&secid=1.603596` | [伯特利_603596_东方财富行情_result.md](test/url_test_results/伯特利_603596_东方财富行情_result.md) |
| EASTMONEY_A_QUOTE_URL | 东方财富A股行情 | `http://push2.eastmoney.com/api/qt/stock/get?fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f107,f104,f105,f116,f184,f168,f169,f170,f213,f152,f15,f19&secid=1.603596` | [伯特利_603596_东方财富A股行情_result.md](test/url_test_results/伯特利_603596_东方财富A股行情_result.md) |

## 新浪URL常量

| 常量名 | 描述 | URL模板 | 返回值示例 |
|-------|------|---------|-----------|
| SINA_DUPONT_ANALYSIS_URL | 新浪杜邦分析（港股） | `https://stock.finance.sina.com.cn/hkstock/finance/02367/40.html` | [伯特利_603596_新浪杜邦分析_result.md](test/url_test_results/伯特利_603596_新浪杜邦分析_result.md) |
| SINA_A_DUPONT_ANALYSIS_URL | 新浪A股杜邦分析 | `https://finance.sina.com.cn/realstock/company/sh603596/finance_4_1.html` | [伯特利_603596_新浪A股杜邦分析_result.md](test/url_test_results/伯特利_603596_新浪A股杜邦分析_result.md) |
| SINA_SEARCH_URL | 新浪股票搜索 | `https://finance.sina.com.cn/search/?q=603596&range=stock` | [伯特利_603596_新浪股票搜索_result.md](test/url_test_results/伯特利_603596_新浪股票搜索_result.md) |
| SINA_FINANCE_SEARCH_URL | 新浪财经搜索 | `https://finance.sina.com.cn/search/?q=603596&range=finance` | [伯特利_603596_新浪财经搜索_result.md](test/url_test_results/伯特利_603596_新浪财经搜索_result.md) |
| SINA_FINANCE_API_URL | 新浪财务数据接口 | `https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022` | [通用测试_600000_新浪财务API_result.md](test/url_test_results/通用测试_600000_新浪财务API_result.md) |
| SINA_INDUSTRY_URL | 新浪行业数据 | `https://hq.sinajs.cn/ran=123456789&format=json&list=sinaindustry_up,sinaindustry_down` | [伯特利_603596_新浪行业数据_result.md](test/url_test_results/伯特利_603596_新浪行业数据_result.md) |
| SINA_CONCEPT_URL | 新浪概念数据 | `https://hq.sinajs.cn/ran=123456789&format=json&list=si_api4,si_api5,si_api6,si_api7` | [伯特利_603596_新浪概念数据_result.md](test/url_test_results/伯特利_603596_新浪概念数据_result.md) |
| SINA_HTTP_HQ_URL | 新浪HTTP行情 | `http://hq.sinajs.cn/list=sh603596` | - |
| SINA_SEARCH_SUGGEST_URL | 新浪搜索建议 | `https://suggest3.sinajs.cn/suggest/type=11&key=603596&name=suggestdata_0.123456789` | [伯特利_603596_新浪搜索建议_result.md](test/url_test_results/伯特利_603596_新浪搜索建议_result.md) |

## 腾讯URL常量

| 常量名 | 描述 | URL模板 | 返回值示例 |
|-------|------|---------|-----------|
| TENCENT_QUOTE_URL | 腾讯行情接口 | `http://qt.gtimg.cn/q=sh603596` | [伯特利_603596_腾讯行情_result.md](test/url_test_results/伯特利_603596_腾讯行情_result.md) |
| TENCENT_BKQT_RANK_SH_URL | 腾讯上海板块行情 | `https://qt.gtimg.cn/r=123456789&q=bkqtRank_A_sh` | [伯特利_603596_腾讯上海板块行情_result.md](test/url_test_results/伯特利_603596_腾讯上海板块行情_result.md) |
| TENCENT_BKQT_RANK_SZ_URL | 腾讯深圳板块行情 | `https://qt.gtimg.cn/r=123456789&q=bkqtRank_A_sz` | [伯特利_603596_腾讯深圳板块行情_result.md](test/url_test_results/伯特利_603596_腾讯深圳板块行情_result.md) |
| TENCENT_MINUTE_QUERY_URL | 腾讯创业板分钟数据 | `https://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_sz399006&code=sz399006&r=123456789` | [伯特利_603596_腾讯创业板分钟数据_result.md](test/url_test_results/伯特利_603596_腾讯创业板分钟数据_result.md) |

## 使用说明

1. 所有URL常量都定义在 `stock.py` 和 `util.py` 文件中
2. 测试文件 `test_all_urls.py` 可以测试所有URL并生成返回值示例
3. 测试结果保存在 `test/url_test_results/` 目录下
4. 可以通过本文档中的链接直接查看各个URL的返回值示例

## 更新记录

- 创建时间：2023年10月
- 最后更新：2023年10月
- 更新内容：初始版本，包含所有URL常量与返回值关联