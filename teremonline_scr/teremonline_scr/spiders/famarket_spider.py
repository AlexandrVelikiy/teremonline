import scrapy
from teremonline_scr.items import FamarketScrItem
import os

class FamarketSpider(scrapy.Spider):
    name = "famarket_scr"

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
        url = response.url + f'?page=1'
        yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        if not response.xpath('.//h1').get():
            yield scrapy.Request(url=response.url, dont_filter=True)

        # определяем есть ли ссылки дальше, свяряем текущую ссылку и ту что в "следующая"
        plaginate = response.xpath('.//ul [@class="pagination"]/li/a/@href').extract()
        if plaginate:
            next_page_url = 'https:'+ plaginate[-1]
            if response.url != next_page_url:
                yield scrapy.Request(url= next_page_url,  callback=self.parse)

        category_name = response.xpath('.//h1/text()').get()
        urls = response.xpath('.//div [@class="caption"]/a/@href').extract()

        for url in urls:
            yield scrapy.Request(url='https:' + url, cb_kwargs = dict(category_name = category_name), callback=self.parse_item)


    def parse_item(self, response, category_name):
        items = FamarketScrItem()
        self.brand = ''

        category_path = response.xpath('.//ol [@ class="breadcrumb hidden-xs"]/li/a/text()').extract()
        if len(category_path) > 2:
            # удалим 1 лишние
            category_path.pop(0)
            main_category = '|'.join(category_path)
        else:
            main_category ='|'.join(category_path)

        name = response.xpath('.//h1/text()').get()

        price  = response.xpath('.//div [@ class="h2 text-primary"]/span/text()').get()
        unit = ''
        model = response.xpath('.//div [@ class="small"]/text()').get()

        chracter_list  = response.xpath('.//div [@ id="settings"]/div/div/table/tr/td')
        if len(chracter_list) > 0:
            # обрабатываем характетристики
            atribute = self.get_atributes('Характеристики',chracter_list)
        else:
            # нет харакетристик
            atribute = ''

        # нужно обработать убрав лишнее
        list_img_urls = response.xpath('.//div [@id="fotoload"]/div[@class="bx-pager"]/a/img/@src').extract()
        if list_img_urls:
            images_url, images_urls = self.processing_img_urls(list_img_urls)
        else: # одно фото
            img_url = response.xpath('.//div [@id="fotoload"]//img/@src').get()
            images_url = 'https://famarket.ru' + img_url
            images_urls = ''

        description = response.xpath('normalize-space(string(//div [@ itemprop="description"]))').get()


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
        items['_DOCUMENTS_'] = ''
        items['_URL_'] = response.url

        return items

    def get_atributes(self,haract, atributes_name_list):
        # получаем название характеристик и их значение и формируем строку
        name = []
        znach = []
        for i, value in enumerate(atributes_name_list):
            v = value.xpath('descendant-or-self::*/text()').get()
            if not v:
                v = value.xpath('text()').get()
            if (i + 1) % 2:
                name.append(v)
            else:
                znach.append(v)

        atribute = ''
        for i in range(len(name)):
            if name[i] == 'Бренд' or name[i] == 'Производитель':
                self.brand = znach[i]
            a = '|'.join([haract, name[i], znach[i]])
            atribute = atribute + a + '\n'
        return atribute.strip('\n')

    def processing_img_urls(self,urls):
        # обрабатываем список уклов удаляя лишнее
        # https://www.teremonline.ru/upload/resize_cache/iblock/c4c/1024_1024_1f0ccde5e7a13ae51894a3eef4fcac3e6/RG008M1LRK3KMM.jpg
        # https://www.teremonline.ru/upload/iblock/c4c/RG008M1LRK3KMM.jpg
        if urls:
            new_urls = []
            for url in urls:
                new_urls.append('https://famarket.ru'+url)
            new_url = new_urls.pop(0)
        else:
            new_url = ''
            new_urls = ''
        return new_url,new_urls
