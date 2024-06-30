import scrapy
import uuid
import os

# The City's website translates all pages into these languages. 
# We are only concerned about the english pages, so we check if the following languages appear in the URL.
languages = set(["es/", "ja/", "ko/", "ru/", "vi/", "km/", "ar/", "hi/", "fa/", "pa/", "te/", "ur/", "am/", "zh-"])

class CityBellevueSpider(scrapy.Spider):
    name = 'city_bellevue_spider'
    
    start_urls = ['https://bellevuewa.gov/sitemap']
    allowed_domains = ['bellevuewa.gov']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extracted_text = []

        
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        if response.url[-4:] == ".pdf":
            # The scraper saves all the PDFs directly.
            pdf_filename = os.environ.get("CHATBOT_PATH") + "/Data/bellevue_extracted/pdfs/" + str(uuid.uuid4()) + '.pdf'
            
            with open(pdf_filename, 'wb') as pdf_file:
                pdf_file.write(response.body)
                pdf_file.close()

        else:
            f = open(os.environ.get("CHATBOT_PATH") + '/Data/bellevue_extracted/' + str(uuid.uuid4()) + '.txt', 'w')
            #  Format of Text Files
            #  Line 1: URL, 2: Title, 3: Date (if applicable), 4-: Website content
            
            f.write(response.url + '\n')
            
            title = response.css('title::text').get()
            f.write(title + '\n')
            
            date = "".join(response.css('.date ::text').getall()).strip()

            if not date:
                date = ""
            f.write(date + '\n')
            
            # All text on website are either in the .node__content class or the .content-wrapper class.
            text = " ".join([x.replace("\n", " ").replace("\t", "").strip() for x in response.css('.node__content ::text').getall()])
            if not text:
                text = " ".join([x.replace("\n", " ").replace("\t", "").strip() for x in response.css('.content-wrapper ::text').getall()])
            
            f.write(text)
            f.close()

            for link in response.css('a::attr(href)').getall():
                # Check if next page is a non-english page.
                if (link.startswith('https://bellevuewa.gov') and link[23:26] not in languages) or (link.startswith("/") and link[1:4] not in languages):
                    yield response.follow(link, callback=self.parse)

    

    def closed(self, reason):
        pass
