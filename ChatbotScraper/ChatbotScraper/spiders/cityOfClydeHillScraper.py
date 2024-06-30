import scrapy
import uuid
import os

class CityClydeHillSpider(scrapy.Spider):
    name = 'city_clyde_hill_spider'
    
    start_urls = ['https://www.clydehill.org/']
    allowed_domains = ['clydehill.org']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extracted_text = []

        
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        if "admin/api/connectedapps.cms.extensions" in response.url:
            # The scraper saves all the PDFs directly.
            pdf_filename = os.environ.get("CHATBOT_PATH") + "/Data/clyde_hill_extracted/pdfs/" + str(uuid.uuid4()) + '.pdf'
            
            with open(pdf_filename, 'wb') as pdf_file:
                pdf_file.write(response.body)
                pdf_file.close()

        else:
            f = open(os.environ.get("CHATBOT_PATH") + '/Data/clyde_hill_extracted/' + str(uuid.uuid4()) + '.txt', 'w')
            #  Format of Text Files
            #  Line 1: URL, 2: Title, 3: Date (if applicable), 4-: Website content
            
            f.write(response.url + '\n')
            
            title = response.css('title::text').get()
            f.write(title + '\n')
            
            #date = "".join(response.css('.date ::text').getall()).strip()

            #if not date:
            #    date = ""
            date = ""
            f.write(date + '\n')
            
            # All text on website are either in the .node__content class or the .content-wrapper class.
            text = " ".join([x.replace("\n", " ").replace("\t", "").strip() for x in response.css('#interior-content ::text').getall()])
            if not text:
                text = " ".join([x.replace("\n", " ").replace("\t", "").strip() for x in response.css('#interior ::text').getall()])
            
            f.write(text)
            f.close()

            for link in response.css('a::attr(href)').getall():
                # Check if next page is a non-english page.
                #if (link.startswith('https://bellevuewa.gov') and link[23:26] not in languages) or (link.startswith("/") and link[1:4] not in languages):
                if "mailto:" not in link and "calendar-of-events" not in link:
                    yield response.follow(link, callback=self.parse)

    

    def closed(self, reason):
        pass
