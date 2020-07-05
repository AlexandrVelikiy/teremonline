import scrapy
from teremonline_scr.items import MargroidScrItem
import os
import json
class MargroidSpider(scrapy.Spider):
    name = "margroid_scr"

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
        plaginate = response.xpath('.//div [@class="bx-pagination-container row"]/ul/li/a/span/text()').extract()
        if plaginate:
            count_page = int(plaginate[len(plaginate)-2])
            for i in range(count_page):
                url = response.url + f'?PAGEN_1={i+1}'
                yield scrapy.Request(url=url ,callback=self.parse)

        else:
            # одна страница
            url = response.url + f'?PAGEN_1=1'
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if not response.xpath('.//h1').get():
            yield scrapy.Request(url=response.url, dont_filter=True)

        category_name = response.xpath('.//h1/text()').get()
        urls = response.xpath('.//div [@data-entity="items-row"]//div[@class="element-img-wrap"]/a/@href').extract()

        for url in urls:
            yield scrapy.Request(url='https://www.margroid.ru'+url, cb_kwargs = dict(category_name = category_name),callback=self.parse_item)


    def parse_item(self, response, category_name):
        items = MargroidScrItem()
        self.brand = ''

        category_path = response.xpath('.//div [@class="breadcrumb-item"]/a/span/text()').extract()
        if len(category_path) > 2:
            # удалим 2 лишние Главная
            category_path.pop(0)
            category_path.pop(0)
            main_category = '|'.join(category_path)
        else:
            main_category ='|'.join(category_path)

        name = response.xpath('.//h1/text()').get()
        name = name.strip('\n')
        item_name = name.strip()

        description = ''
        des_p = response.xpath('.//div [@class="item-info-column--bottom"]/div[1]/p/text()').extract()
        for p in des_p:
            if p:
                p = p.strip('\n')
                p = p.strip('\t')
                p = p.strip('\r')
                description = description +' '+ p

        atributes_name_list = response.xpath('.//div [@ class="item-characteristics-full"]/div/div [@class="col-xs-6 characteristic-name"]/text()').extract()
        atributes_value_list = response.xpath('.//div [@ class="item-characteristics-full"]/div/div [@class="col-xs-6 characteristic-value"]/text()').extract()

        atribute = self.get_atributes('Характеристики', atributes_name_list,atributes_value_list)

        # нужно обработать убрав лишнее
        p = response.xpath('.//ul [@class="slides product-carousel__slides"]/li/img/@src').extract()
        if p:
            images_url, images_urls = self.processing_img_urls(p)
        else:
            images_url = ''
            images_urls = ''

        items['_MAIN_CATEGORY_'] = main_category
        #items['_NAME_'] = name
        items['_MODEL_'] = ''
        items['_SKU_'] = ''
        items['_MANUFACTURER_'] = self.brand  # из атрибутов бренд
        #items['_PRICE_'] = price
        items['_UNIT_'] = ''
        #items['_ATTRIBUTES_'] = atribute
        items['_IMAGE_'] = images_url
        items['_IMAGES_'] = images_urls
        items['_DESCRIPTION_'] = description
        items['_DOCUMENTS_'] = ''  # self.processing_pdf_urls(pdf_urls)
        items['_URL_'] = response.url

        script = response.xpath('.//div [@class="item-info-column-row"]/script[@type="text/javascript"]').get()
        n = script.find('new universe.catalog.offers')
        if n > 0:
            p = script.find('}}});')
            offers = script[n + 28:p + 3]
            offers = offers.replace("\'", '\"')

            try:
                offer = json.loads(offers)
                item_offers = offer.get('OFFERS')
                for offer in item_offers:
                    price = offer.get('PRICE').get('VALUE')
                    # добавлем цену
                    items['_PRICE_'] = price

                    prop = offer.get('DISPLAY_PROPERTIES')
                    # получаем список характеристик для конкретного размера
                    add_name = ''
                    add_atributes = ''
                    for p in prop:
                        name = p.get('NAME')
                        value = p.get('VALUE')
                        # добавляем к названию высоту и ширину
                        if name == 'A (высота)':
                            add_name = add_name+'В'+str(value)+'*'
                        if name == 'B (ширина)':
                            add_name = add_name+'Ш'+str(value)
                        a = '|'.join(['Характеристики', name, str(value)])
                        add_atributes = add_atributes + a + '\n'

                    items['_NAME_'] = item_name + ' ' + add_name
                    items['_ATTRIBUTES_'] = atribute + add_atributes.strip('\n')

                    yield items

            except Exception as e:
                print(e)
        else:
            # один вариант
            price = response.xpath('.//div [@class="item-current-price-wrap"]/div/text()').get()
            items['_PRICE_'] = price
            items['_NAME_'] = item_name
            items['_ATTRIBUTES_'] = atribute.strip('\n')

            yield items

    def get_atributes(self,haract,atributes_name_list,atributes_value_list):
        atribute = ''
        for i in range(len(atributes_name_list)):
            a = '|'.join([haract, atributes_name_list[i], atributes_value_list[i].strip()])
            atribute = atribute + a + '\n'
        return atribute

    def processing_img_urls(self,urls):
        # обрабатываем список уклов
        if urls:
            if len(urls) > 1:
                new_urls = []
                for url in urls:
                    new_url = 'https://www.margroid.ru' + url
                    new_urls.append(new_url)
                new_url = new_urls.pop(0)
            else:
                new_url = 'https://www.margroid.ru' + urls[0]
                new_urls = ''
        else:
            new_url = ''
            new_urls = ''

        return new_url,new_urls

