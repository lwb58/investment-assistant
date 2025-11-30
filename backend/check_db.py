import sqlite3

# 连接数据库
conn = sqlite3.connect('stock_notes.db')
cursor = conn.cursor()

# 查询股票数量
cursor.execute('SELECT COUNT(*) FROM stocks')
count = cursor.fetchone()[0]
print('数据库中股票数量:', count)

# 查询前5条股票数据
print('\n前5条股票数据:')
cursor.execute('SELECT * FROM stocks LIMIT 5')
for row in cursor.fetchall():
    print(row)

# 关闭连接
conn.close()