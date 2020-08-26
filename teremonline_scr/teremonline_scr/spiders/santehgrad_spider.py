import scrapy
from teremonline_scr.items import SantehgradItem
import os

# https://www.termoros.com/brands/ape/

class SantehgradSpider(scrapy.Spider):
    name = "santehgrad_scr"

    def start_requests(self):
        urls = []
        try:
            with open(os.path.join(os.getcwd(), 'category_for_pars.txt'), 'r') as file:
                urls = [line.rstrip() for line in file]
        except:
            print('file category_for_pars.txt not found')
            return

        for url in urls:
            yield scrapy.Request(url=url, meta={
                'dont_redirect': True,
                'handle_httpstatus_list': [302]}, callback=self.parse)

    def parse(self, response):
         # определяем есть ли ссылки дальше, свяряем текущую ссылку и ту что в "следующая"
        plaginate = response.xpath('.//div [@ class="navigation"]/span/a/@href').extract()
        if plaginate:
            next_page_url = 'https://santehgrad.ru' + plaginate[-1]
            if response.url != next_page_url:
                yield scrapy.Request(url=next_page_url, callback=self.parse)

        category_name = response.xpath('.//h1/text()').get()
        urls = response.xpath('.//form//div[@class=" PLN"]/a/@href').extract()

        for url in urls:
            yield scrapy.Request(url='https://santehgrad.ru' + url, cb_kwargs=dict(category_name=category_name),
                                 callback=self.parse_item)

    def parse_item(self, response, category_name):
        items = SantehgradItem()
        self.brand = ''

        category_path = response.xpath('.//div[@id="navigation"]/span/a/text()').extract()
        if len(category_path) > 2:
            # удалим 1 лишние Главная
            category_path.pop(0)
            l = len(category_path)
            category_path.pop(l-1)
            main_category = '|'.join(category_path)
        else:
            main_category ='|'.join(category_path)

        name = response.xpath('.//h1/text()').get()

        # class="art_container"
        price  = response.xpath('.//div[@class="prodInfoRightBlockPrice"]/span/span[@class="Price-plain"]/text()').get()
        unit = 'шт'
        model = response.xpath('.//div[@class="prodInfoModel"]/text()').get()

        description = response.xpath('.//div[@ class="ProductInfoDesc-text"]/text()').get()

        atributes_name_list = response.xpath('.//div[@ class="productInfoSpec-line"]/div [@class="row"]/span/text()').extract()
        #atributes_value_list = response.xpath('.//div[@ id="description"]/div/div/div/dl/dd')

        atribute = self.get_atributes('Характеристики', atributes_name_list)

        # нужно обработать убрав лишнее
        urls = response.xpath('.//div[@ class="col-xs-12 col-sm-9 col-md-10 col-sm-push-3 col-md-push-2 ProductInfoImage"]//img/@src').extract()
        for url in urls:
            if url.find('noimage.gif') >-1:
                # пробуем найти другие
                urls = response.xpath('.//div[@ id="moreImages"]//img/@src').extract()

        images_url, images_urls = self.processing_img_urls(urls)

        self.brand = 'FIV'
        items['_MAIN_CATEGORY_'] = main_category
        items['_NAME_'] =  name
        items['_MODEL_'] = model
        items['_SKU_'] = model
        items['_MANUFACTURER_'] = self.brand# из атрибутов бренд
        items['_PRICE_'] = price
        items['_UNIT_'] = unit
        items['_ATTRIBUTES_'] = atribute
        items['_IMAGE_'] = images_url
        items['_IMAGES_'] = images_urls
        items['_DESCRIPTION_'] = description
        items['_DOCUMENTS_'] = ''#self.processing_pdf_urls(pdf_urls)
        items['_URL_'] = response.url

        return items

    def get_atributes(self,haract,atributes_name_list):
        # пробуем получить значения
        name = []
        znach = []
        for i, value in enumerate(atributes_name_list):
            v = value
            if (i+1) % 2:
                name.append(v)
            else:
                znach.append(v)

        atribute = ''
        for i in range(len(name)):
            a = '|'.join([haract, name[i], znach[i]])
            atribute = atribute + a + '\n'
        return atribute.strip('\n')

    def processing_img_urls(self,urls):
        # обрабатываем список уклов
        if urls:
            new_urls = []
            for url in urls:
                new_urls.append('https://santehgrad.ru/' + url)
            new_url = new_urls.pop(0)
        else:
            new_url = ''
            new_urls = ''

        return new_url,new_urls
