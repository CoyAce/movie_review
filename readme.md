# 影评分析程序

1、爬取豆瓣搜索结果

url为ur'https://movie.douban.com/subject_search?search_text=keyword'

2、使用搜索结果爬取指定影片的短评

url为ur'https://movie.douban.com/subject/subject_id/comments?status=P'

3、对爬取的短评进行情感分析

# todo：

检测splash是否启动
sudo docker run -p 8050:8050 scrapinghub/splash

菜单开发

情感分析

# 问题

scrapy和pickle、nltk冲突

