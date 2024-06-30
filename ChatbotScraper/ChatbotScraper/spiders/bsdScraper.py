import scrapy
import uuid
import os

class CityClydeHillSpider(scrapy.Spider):
    name = 'bsd_spider'
    
    start_urls = ['https://www.bsd405.org/']
    allowed_domains = ['bsd405.org', 'resources.finalsite.net/']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extracted_text = []

        
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        if "https://resources.finalsite.net/" in response.url:
            # The scraper saves all the PDFs directly.
            pdf_filename = os.environ.get("CHATBOT_PATH") + "/Data/bsd_extracted/pdfs/" + str(uuid.uuid4()) + '.pdf'
            
            with open(pdf_filename, 'wb') as pdf_file:
                pdf_file.write(response.body)
                pdf_file.close()

        else:
            f = open(os.environ.get("CHATBOT_PATH") + '/Data/bsd_extracted/' + str(uuid.uuid4()) + '.txt', 'w')
            #  Format of Text Files
            #  Line 1: URL, 2: Title, 3: Date (if applicable), 4-: Website content
            
            f.write(response.url + '\n')
            
            title = response.css('title::text').get()
            f.write(title + '\n')
            
            date = "".join(response.css('.fsDateTime ::text').getall()).strip()

            if not date:
                date = ""
            #date = ""
            f.write(date + '\n')
            
            # All text on website are either in the .node__content class or the .content-wrapper class.
            text = " ".join([x.replace("\n", " ").replace("\t", "").strip() for x in response.css('.fsDiv ::text').getall()])
            if not text:
                text = " ".join([x.replace("\n", " ").replace("\t", "").strip() for x in response.css('.fsPageLayout ::text').getall()])
            
            f.write(text)
            f.close()

            for link in response.css('a::attr(href)').getall():
                # Check if next page is a non-english page.
                #if (link.startswith('https://bellevuewa.gov') and link[23:26] not in languages) or (link.startswith("/") and link[1:4] not in languages):
                if "mailto:" not in link and "tel:" not in link:
                    yield response.follow(link, callback=self.parse)

    

    def closed(self, reason):
        pass
