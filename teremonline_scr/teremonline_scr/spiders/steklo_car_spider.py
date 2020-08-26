import scrapy
from teremonline_scr.items import StekloCarItem
import os

class StekloCarSpider(scrapy.Spider):
    name = "steklo_car_scr"

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

    def parse(self,response):
        # определеяем количество страниц
        # https://steklo-car.ru
        # ('.//div [@id="cat_top_tree"]/table/tbody/tr/td//a/@href')
        urls = response.xpath('.//div [@id="cat_top_tree"]//table//a/@href').extract()
        for url in urls:
            yield scrapy.Request(url='https://steklo-car.ru' + url + 'all/', callback=self.parse_model_auto)



    def parse_model_auto(self, response):
        if not response.xpath('.//h1').get():
            yield scrapy.Request(url=response.url, dont_filter=True)

        urls = response.xpath('.//div [@class="prdbrief_name"]/a/@href').extract()

        for url in urls:
            yield scrapy.Request(url='https://steklo-car.ru' + url, callback=self.parse_item)


    def parse_item(self, response):
        items = StekloCarItem()
        self.brand = ''

        category_path = response.xpath('.//div[@class="cpt_product_category_info"]/table/tr/td/a/text()').extract()
        if len(category_path) > 2:
            # удалим 1 лишние
            category_path.pop(0)
            main_category = '|'.join(category_path)
        else:
            main_category ='|'.join(category_path)

        name = response.xpath('.//h1/text()').get()

        price  = response.xpath('.//div [@class="cpt_product_price"]//span/text()').get()
        unit = ''
        model = ''#response.xpath('.//div [@ class="small"]/text()').get()
        self.brand = ''

        chracter_list  = response.xpath('.//div [@class="cpt_product_params_fixed"]/table/tr/td')
        if len(chracter_list) > 0:
            # обрабатываем характетристики
            atribute = self.get_atributes('Характеристики',chracter_list)
        else:
            # нет харакетристик
            atribute = ''

        # нужно обработать убрав лишнее
        list_img_urls = response.xpath('.//div [@class="cpt_product_images"]//img/@src').extract()
        if len(list_img_urls) == 1:
            images_url = 'https://steklo-car.ru' + list_img_urls[0]
            images_urls = ''
        else:
            # убрать
            list_img_urls = response.xpath('.//div [@id="productSlider"]//img[@data-elem="bg"]/@src').extract()
            images_url, images_urls = self.processing_img_urls(list_img_urls)
        #if list_img_urls:
        #    images_url, images_urls = self.processing_img_urls(list_img_urls)
        #else: # одно фото
        #    img_url = response.xpath('.//div [@id="fotoload"]//img/@src').get()
        #    images_url = 'https://famarket.ru' + img_url
        #    images_urls = ''

        #descriptions = response.xpath('//div [@id="desc"]//text()').extract()
        descriptions = response.xpath('.//table[@class="tovar-info"]/tbody/tr[@class="tovar-info-shema"]/td/text()').extract()
        if len(descriptions) >0 :
            description = descriptions[0].strip()
        else:
            description = ''


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
            v = value.xpath('b/text()').get()
            if not v:
                v = value.xpath('text()').get()
            if not v:
                v = ''
            if (i + 1) % 2:
                name.append(v.strip())
            else:
                znach.append(v.strip())

        atribute = ''
        for i in range(len(name)):
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
