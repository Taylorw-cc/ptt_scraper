# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.exporters import JsonItemExporter
from itemadapter import ItemAdapter
from .items import ArticleItem, CommentItem
import mysql.connector
from . import settings

class PttScraperPipeline:
    def process_item(self, item, spider):
        if isinstance(item, ArticleItem):
            if item['push'] is None:
                item['push'] = 0
            elif item['push'] == '爆':
                item['push'] = 100
            elif 'X' in item['push']:
                boo_cnt = item['push'].split('X')[-1]
                #XX
                if len(boo_cnt) == 3:
                    item['push'] = -100
                #X
                elif boo_cnt == '':
                    item['push'] = -10
                #X2 X3...
                else:
                    item['push'] = -10 * int(boo_cnt)
            else:
                item['push'] = int(item['push'])
        return item

#匯出成jason檔
class JsonWriterPipeline:
    def open_spider(self, spider):
        self.f = open("ptt-by-JsonWriterPipeline.json", "wb") # 必須是binary mode，寫⼊bytes
        self.exporter = JsonItemExporter(self.f, encoding="utf8") # 初始化exporter
        self.exporter.start_exporting() # 開始匯出
    def process_item(self, item, spider):
        self.exporter.export_item(item) # 匯出資料
        return item
    def close_spider(self, spider):
        self.exporter.finish_exporting() # 完成匯出

#存入mySQL
class DatabasePipeline:
    def open_spider(self, spider):
        # 建⽴connect物件，與mysql連線
        self.connect = mysql.connector.connect(
            host = settings.MYSQL_HOST,
            database = settings.MYSQL_DATABASE,
            username = settings.MYSQL_USERNAME,
            password = settings.MYSQL_PASSWORD
        )
        # 建⽴cursor物件，以便對資料庫做操作
        self.cursor = self.connect.cursor()

        self.__create_table_if_not_exist()

    def __create_table_if_not_exist(self):
        article_sql = """
            CREATE TABLE IF NOT EXISTS `article`(
                `id` SERIAL NOT NULL,
                `article_id` VARCHAR(30) PRIMARY KEY,
                `push` INT,
                `title` TEXT(50),
                `link` TEXT(50),
                `author` TEXT(20),
                `published_date` TEXT(20),
                `content` TEXT(1000)
                );
        """
        comment_sql = """
            CREATE TABLE IF NOT EXISTS `comment`(
                `id` SERIAL NOT NULL,
                `article_id` VARCHAR(30),
                `push_tag` TEXT(2),
                `push_user_id` TEXT(20),
                `push_content` TEXT(53),
                `push_ipdatetime` TEXT(20), /*ex: 05/26 08:57*/
                FOREIGN KEY(`article_id`)
                REFERENCES article(`article_id`)
                ON DELETE CASCADE /*當兩表都有該筆資料，主表刪除時⼀起刪掉*/
                );
        """
        self.cursor.execute(article_sql)
        self.cursor.execute(comment_sql)
        self.connect.commit()

    def process_item(self, item, spider):
        try:
            sql, data = None, None
            if isinstance(item, ArticleItem):
                sql, data = self.__process_article_item(item)
            elif isinstance(item, CommentItem):
                sql, data = self.__process_comment_item(item)

            if sql is not None and data is not None:
                self.cursor.execute(sql, data)
                self.connect.commit()
        except Exception as e:
            self.connect.rollback()
            print(e)
        return item

    def __process_article_item(self, item):
        sql = """
            INSERT INTO `article`(
                `article_id`,
                `push`,
                `title`,
                `link`,
                `author`,
                `published_date`,
                `content`
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        data = (
            item['article_id'], item['push'], item['title'], item['link'],
            item['author'], item['published_date'], item['content']
        )
        return sql, data
    
    def __process_comment_item(self, item):
        sql = """
            INSERT INTO `comment`(
                `article_id`,
                `push_tag`,
                `push_user_id`,
                `push_content`,
                `push_ipdatetime`
                )
            VALUES (%s, %s, %s, %s, %s);
        """
        data = (
            item['article_id'], item['push_tag'], item['push_user_id'], item['push_content'], item['push_ipdatetime']
        )
        return sql, data
    
    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()
