# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleItem(scrapy.Item):
    article_id = scrapy.Field() # ⽂章的id
    push = scrapy.Field() # ⽂章推⽂數量
    title = scrapy.Field() # ⽂章標題
    link = scrapy.Field() # ⽂章超連結
    author = scrapy.Field() # ⽂章作者
    published_date = scrapy.Field() # po⽂⽇期
    content = scrapy.Field() # 內⽂

class CommentItem(scrapy.Item):
    article_id = scrapy.Field() # ⽂章id
    push_tag = scrapy.Field() # 留⾔的推⽂數量
    push_user_id = scrapy.Field() # 留⾔者id
    push_content = scrapy.Field() # 留⾔內⽂
    push_ipdatetime = scrapy.Field() # 留⾔的ip時間⽇期