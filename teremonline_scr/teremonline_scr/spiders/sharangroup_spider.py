import scrapy
from teremonline_scr.items import SharangroupScrItem
import os

class SharangroupSpider(scrapy.Spider):
    name = "sharangroup_scr"

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
        plaginate = response.xpath('.//ul [@ class="c-pagination"]/li/a/text()').extract()
        if plaginate:
            count_page = int(plaginate[len(plaginate)-2])
            for i in range(count_page):
                url = response.url + f'?page={i+1}'
                yield scrapy.Request(url=url ,callback=self.parse)

        else:
            # одна страница
            url = response.url + f'?page=1'
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if not response.xpath('.//h1').get():
            yield scrapy.Request(url=response.url, dont_filter=True)

        category_name = response.xpath('.//h1/text()').get()
        #category_path = response.xpath('.//ul[@itemtype="https://schema.org/BreadcrumbList"]/li/a/div/text()').extract()
        urls = response.xpath('.//div[@ itemtype="http://schema.org/Product"]/div/form/div/a/@href').extract()

        for url in urls:
            yield scrapy.Request(url='https://www.sharangroup.ru'+url, cb_kwargs = dict(category_name = category_name),callback=self.parse_item)


    def parse_item(self, response, category_name):
        items = SharangroupScrItem()
        self.brand = ''

        category_path = response.xpath('.//li[@itemtype="https://schema.org/ListItem"]/a/span/text()').extract()
        if len(category_path) > 2:
            # удалим 1 лишние Главная
            category_path.pop(0)
            main_category = '|'.join(category_path)
        else:
            main_category ='|'.join(category_path)

        name = response.xpath('.//h1 [@ class="category-name"]/span/text()').get()

        # class="art_container"
        price  = response.xpath('.//div [@ class="show-price"]/span/text()').get()
        unit = ''#response.xpath('.//div [@ class="ted-sum-wrap"]/span/text()').get()
        model = response.xpath('.//div[@ class="articul"]/span/text()').get()

        description = response.xpath('.//div[@ id="description"]/div/div/div/span/text()').get()

        atributes_name_list = response.xpath('.//div[@ id="description"]/div/div/div/dl/dt/text()').extract()
        atributes_value_list = response.xpath('.//div[@ id="description"]/div/div/div/dl/dd')

        atribute = self.get_atributes('Характеристики', atributes_name_list,atributes_value_list)

        # нужно обработать убрав лишнее
        p = response.xpath('.//div[@ class="image"]/a/img/@src').extract()
        if p:
            images_url, images_urls = self.processing_img_urls(p)
        else:
            images_url, images_urls = self.processing_img_urls(response.xpath('.//div[@ class="more-images"]//img/@src').extract())

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

    def get_atributes(self,haract,atributes_name_list,atributes_value_list):
        # пробуем получить значения

        charact_value_t = []
        for value in atributes_value_list:
            v = value.xpath('text()').get()
            if not v:
                v = value.xpath('span/text()').get()
            charact_value_t.append(v)


        atribute = ''
        for i in range(len(atributes_name_list)):
            if atributes_name_list[i] == 'Бренд':
                self.brand = charact_value_t[i]
            a = '|'.join([haract, atributes_name_list[i], charact_value_t[i]])
            atribute = atribute + a + '\n'
        return atribute.strip('\n')

    def processing_img_urls(self,urls):
        # обрабатываем список уклов
        if urls:
            if len(urls) > 1:
                new_urls = []
                for url in urls:
                    new_url = 'https://www.sharangroup.ru/' + url
                    new_urls.append(new_url)
                new_url = new_urls.pop(0)
            else:
                new_url = 'https://www.sharangroup.ru/' + urls[0]
                new_urls = ''
        else:
            new_url = ''
            new_urls = ''

        return new_url,new_urls

    def processing_pdf_urls(self, urls):
        new_urls = []
        if urls:
            for url in urls:
                new_url = 'https://www.teremonline.ru/' + url
                new_urls.append(new_url)

        return new_urls