import scrapy
from teremonline_scr.items import TermorosScrItem
import os

# https://www.termoros.com/brands/ape/

class TermorosSpider(scrapy.Spider):
    name = "termoros_scr"

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
                'handle_httpstatus_list': [302]}, callback=self.parse_pages)

    def parse_pages(self,response):
        # определеяем количество страниц
        plaginate = response.xpath('.//div [@ class="pager"]/a/text()').extract()
        if plaginate:
            count_page = int(plaginate[-1])
            for i in range(count_page):
                url = response.url + f'?PAGEN_4={i+1}'
                yield scrapy.Request(url=url ,callback=self.parse)
                if i > 10:
                    break

        else:
            # одна страница
            url = response.url + f'?PAGEN_4=1'
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if not response.xpath('.//h1').get():
            yield scrapy.Request(url=response.url, dont_filter=True)

        category_name = response.xpath('.//h1/text()').get()
        #category_path = response.xpath('.//ul[@itemtype="https://schema.org/BreadcrumbList"]/li/a/div/text()').extract()
        urls = response.xpath('.//div [@ class="cat_item"]/div[@class="item_i"]/a/@href').extract()

        for url in urls:
            yield scrapy.Request(url='https://www.termoros.com'+url, cb_kwargs = dict(category_name = category_name),callback=self.parse_item)


    def parse_item(self, response, category_name):
        items = TermorosScrItem()
        self.brand = ''

        category_path = response.xpath('.//div[@ itemtype="http://schema.org/Product"]/div/div/a/text()').extract()
        if len(category_path) > 2:
            # удалим 2 лишние Главная Каталог
            category_path.pop(0)
            category_path.pop(0)
            main_category = '|'.join(category_path)
        else:
            main_category ='|'.join(category_path)

        name = response.xpath('.//h1 [@ itemprop="name"]/text()').get()

        # class="art_container"
        price  = response.xpath('.//div [@ class="price_wp"]/p/span/text()').get()
        unit = response.xpath('.//div [@ class="num_wp"]/span/text()').get()
        model = response.xpath('.//div[@ itemprop="offers"]/p/text()').get()

        description = response.xpath('.//div[@ itemprop="offers"]/noindex/p/text()').get()

        atributes_name_list = response.xpath('.//table[@ class="char_table"]/tr/td')
        #atributes_value_list = response.xpath('.//div[@ id="description"]/div/div/div/dl/dd')

        atribute = self.get_atributes('Характеристики', atributes_name_list)

        # нужно обработать убрав лишнее

        images_url, images_urls = self.processing_img_urls(response.xpath('.//div[@ class="detpage_im"]/div/div/img/@src').extract())

        self.brand = 'APE'
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
            v = value.xpath('a/text()').get()
            if not v:
                v = value.xpath('text()').get()
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

            if urls[0].find('no-foto-big.jpg') >-1:
                # фото нет
                new_url = ''
                new_urls = ''
            else:
                new_url = 'https://www.termoros.com' + urls[0]
                new_urls = ''
        else:
            new_url = ''
            new_urls = ''

        return new_url,new_urls
