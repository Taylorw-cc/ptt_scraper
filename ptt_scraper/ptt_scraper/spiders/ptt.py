import scrapy
import re
from ..items import ArticleItem, CommentItem

class PttSpider(scrapy.Spider):
    name = "ptt"
    allowed_domains = ["www.ptt.cc"]
    borad = "Gossiping" #"Soft_Job"
    start_urls = f'https://www.ptt.cc/bbs/{borad}/index.html'
    ROOT_URL = 'https://www.ptt.cc'
    PAGE_LIMIT = 3
    current_page = 1    
    def start_requests(self):
            yield scrapy.Request(url=self.start_urls, callback=self.parse, cookies={"over18":"1"})
    
    def parse(self, response):
        print(f"Scraping the page {self.current_page}...")
        yield from self.__parse_article_list(response)

        if self.current_page < self.PAGE_LIMIT:
            yield from self.__parse_next_page(response)

    def __parse_next_page(self, response):
        next_page_url = response.css("a.btn.wide:nth-child(2)::attr('href')").get()
        if (next_page_url is not None) and response.css("a.btn.wide:nth-child(2)::text").get() == '‹ 上頁':
            next_page_url = self.ROOT_URL + next_page_url
            self.current_page += 1
            yield scrapy.Request(
                url = next_page_url,
                callback = self.parse
            )
    def __parse_article_list(self, response):
        for each in response.css('.r-ent'):
            link = each.css(".title > a::attr('href')").get()
            if link is None:
                continue
            regex_pattern = r"^\/bbs\/" + self.borad + r"\/([a-zA-Z]{1}\.[0-9]+\.[a-zA-Z]{1}\.[a-zA-Z0-9]+)\.html$"
            _res = re.match(regex_pattern, link)
            if _res is not None:
                article_id = _res[1]            
                push = each.css("div.nrec > span::text").get() 
                title = each.css(".title > a::text").get()
                link = self.ROOT_URL + link
                author = each.css("div.meta > div.author::text").get()
                published_date = each.css("div.meta > div.date::text").get()
            else:
                continue
            
            self.logger.debug("爬取文章中...")
            
            articleitem = ArticleItem()
            articleitem['article_id'] = article_id
            articleitem['push'] = push
            articleitem['title'] = title
            articleitem['link'] = link
            articleitem['author'] = author
            articleitem['published_date'] = published_date
            
            yield scrapy.Request(
                url=link,
                callback=self.__parse_each_article,
                cb_kwargs={'article_id': article_id, 'articleitem': articleitem}
                )

    def __parse_each_article(self, response, article_id, articleitem):
        content = "".join(response.css("#main-content::text").getall()).strip()

        self.logger.debug("爬取內文中...")
        articleitem['content'] = content
        yield articleitem
        
        for comment in response.css('div.push'):
            push_tag = comment.css("span:nth-child(1)::text").get()
            push_user_id = comment.css("span:nth-child(2)::text").get()
            push_content = comment.css("span:nth-child(3)::text").get()
            push_ipdatetime = comment.css("span:nth-child(4)::text").get()

            self.logger.debug("爬取留言中...")
            
            commentitem = CommentItem()
            commentitem['article_id'] = article_id
            commentitem['push_tag'] = push_tag
            commentitem['push_user_id'] = push_user_id
            commentitem['push_content'] = push_content
            commentitem['push_ipdatetime'] = push_ipdatetime
            yield commentitem
                        