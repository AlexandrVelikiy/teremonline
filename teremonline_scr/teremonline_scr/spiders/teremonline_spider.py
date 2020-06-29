import scrapy
from teremonline_scr.items import TeremonlineScrItem
import os

class TeremonlineSpider(scrapy.Spider):
    name = "teremonline_scr"

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
        plaginate = response.xpath('.//div [@ class="scfr-pag"]/div/ul/li/a/text()').extract()
        if plaginate:
            count_page = int(plaginate[len(plaginate)-2])
            for i in range(count_page):
                url = response.url + f'?PAGEN_3={i+1}'
                yield scrapy.Request(url=url ,callback=self.parse)

        else:
            # одна страница
            url = response.url + f'?PAGEN_3=1'
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if not response.xpath('.//h1').get():
            yield scrapy.Request(url=response.url, dont_filter=True)

        category_name = response.xpath('.//h1/text()').get()
        category_path = response.xpath('.//ul[@itemtype="https://schema.org/BreadcrumbList"]/li/a/div/text()').extract()
        urls = response.xpath('.//div[@ itemtype="http://schema.org/Product"]/a/@href').extract()

        for url in urls:
            yield scrapy.Request(url='https://www.teremonline.ru'+url, cb_kwargs = dict(category_name = category_name),callback=self.parse_item)


    def parse_item(self, response, category_name):
        items = TeremonlineScrItem()
        self.brand = ''

        category_path = response.xpath('.//ul[@itemtype="https://schema.org/BreadcrumbList"]/li/a/div/text()').extract()
        if len(category_path) > 2:
            # удалим 2 лишние
            category_path.pop(0)
            category_path.pop(0)
            main_category = '|'.join(category_path)
        else:
            main_category ='|'.join(category_path)

        name = response.xpath('.//h1/text()').get()

        # class="art_container"
        price  = response.xpath('.//div [@ class="ted-row prices"]/div/span/span/text()').get()
        unit = response.xpath('.//div [@ class="ted-sum-wrap"]/span/text()').get()
        model = response.xpath('.//div[@ class="art_container"]/span/text()').get()


        chracter_list  = response.xpath(('.//div [@ class="sced-itm"]'))
        if len(chracter_list) > 0:
            # обрабатываем характетристики
            # списко названий подкатегорий
            sced_list_cat = chracter_list[0].xpath('span[@ class="sced-bg-hdr"]/text()').extract()
            sced_list = chracter_list[0].xpath('div[@ class="sced-list"]')
            if len(sced_list) > 1:
                # тут несколько разделов
                atribute = ''
                for i in range(len(sced_list)):
                    atribute = atribute + self.get_atributes(sced_list[i],'Характеристики')
            else:
                # тут один раздел
                atribute = self.get_atributes(sced_list[0], 'Характеристики')


        pdf_urls = []
        if len(chracter_list) > 1:
            # ищем в документации техпаспорта
            sced_list_cat = chracter_list[1].xpath('span[@ class="sced-bg-hdr"]/text()').extract()
            sced_list = chracter_list[1].xpath('div[@ class="serti-block"]/span/text()').extract()
            if 'Технические паспорта' in sced_list:
                tp = chracter_list[1].xpath('div[@ class="serti-block"]/span[text()="Технические паспорта"]/following-sibling::div')
                pdf_urls = tp[0].xpath('a/@href').extract()

        # нужно обработать убрав лишнее
        images_url, images_urls = self.processing_img_urls(response.xpath('.//div[@ class="swiper-wrapper"]/div/span/span/img/@big_foto').extract())

        description = response.xpath('.//div[@ class="sc-element-descr"]/span/text()').get()

        self.brand = response.xpath('.//div[@ class="brand_element_block"]/a/@href').get()

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
        items['_DOCUMENTS_'] = self.processing_pdf_urls(pdf_urls)
        items['_URL_'] = response.url

        return items

    def get_atributes(self,sced_list,sced_list_cat):
        # получаем название характеристик и их значение и формируем строку
        charact_name = sced_list.xpath('div/span [@class="sced-l-descr-1"]/text()').extract()
        charact_value = sced_list.xpath('div/span [@class="sced-l-descr-2"]')
        charact_value_t = []
        for value in charact_value:
            v = value.xpath('a/text()').get()
            if not v:
                v = value.xpath('text()').get()
            charact_value_t.append(v)

        atribute = ''
        for i in range(len(charact_name)):
            if charact_name[i] == 'Бренд':
                # self.brand = charact_value_t[i]
                pass
            a = '|'.join([sced_list_cat, charact_name[i], charact_value_t[i]])
            atribute = atribute + a + '\n'
        return atribute

    def processing_img_urls(self,urls):
        # обрабатываем список уклов удаляя лишнее
        # https://www.teremonline.ru/upload/resize_cache/iblock/c4c/1024_1024_1f0ccde5e7a13ae51894a3eef4fcac3e6/RG008M1LRK3KMM.jpg
        # https://www.teremonline.ru/upload/iblock/c4c/RG008M1LRK3KMM.jpg
        if urls:
            new_urls = []
            for url in urls:
                split_urls = url.split('/')
                if len(split_urls) > 5:
                    del(split_urls[2])
                    del(split_urls[4])

                split_urls[0] = 'www.teremonline.ru'
                new_url = '/'.join(split_urls)
                new_urls.append(new_url)

            new_url = new_urls.pop(0)
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