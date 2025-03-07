# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

def serialize_unit(value):
    # удаляем все до ,:
    in_s = str(value)
    s = in_s[in_s.find(',') + 1:]
    return s

def serialize_model(value):
    # удаляем Арт:
    in_s = str(value)
    s = in_s[in_s.find(':')+2:]
    return f"`{s}"

def serialize_sky(value):
    # удаляем Арт:
    in_s = str(value)
    s = in_s[in_s.find(':')+1:]
    return f"`{s}"

def serialize_price(value):
    # удаляем знак рубля
    return value[:len(value)-2]

def serialize_price2(value):
    # удаляем знак руб.
    return value[:len(value)-4]

def serialize_brend(value):
    in_s = str(value)
    in_s = in_s.replace('/brands/',"")
    in_s = in_s[:in_s.find('-')]
    return in_s

class TeremonlineScrItem(scrapy.Item):
    # define the fields for your item here like:
    _MAIN_CATEGORY_ = scrapy.Field()
    _NAME_ = scrapy.Field()
    _MODEL_ = scrapy.Field(serializer=serialize_model)
    _SKU_ = scrapy.Field(serializer=serialize_sky)
    _MANUFACTURER_ = scrapy.Field(serializer=serialize_brend)
    _PRICE_ = scrapy.Field(serializer=serialize_price)
    _UNIT_ = scrapy.Field(serializer=serialize_unit)
    _ATTRIBUTES_ = scrapy.Field()
    _IMAGE_ = scrapy.Field()
    _IMAGES_ = scrapy.Field()
    _DESCRIPTION_ = scrapy.Field()
    _DOCUMENTS_ = scrapy.Field()
    _URL_ = scrapy.Field()

def serialize_model1(value):
    return f"`{value}"

class SharangroupScrItem(scrapy.Item):
    # define the fields for your item here like:
    _MAIN_CATEGORY_ = scrapy.Field()
    _NAME_ = scrapy.Field()
    _MODEL_ = scrapy.Field(serializer=serialize_model1)
    _SKU_ = scrapy.Field(serializer=serialize_model1)
    _MANUFACTURER_ = scrapy.Field()
    _PRICE_ = scrapy.Field(serializer=serialize_price2)
    _UNIT_ = scrapy.Field()
    _ATTRIBUTES_ = scrapy.Field()
    _IMAGE_ = scrapy.Field()
    _IMAGES_ = scrapy.Field()
    _DESCRIPTION_ = scrapy.Field()
    _DOCUMENTS_ = scrapy.Field()
    _URL_ = scrapy.Field()

def serialize_model2(value):
    # удаляем Артикул:
    in_s = str(value)
    s = in_s[in_s.find(':')+2:]
    return f"`{s}"

def serialize_descr(value):
    # удаляем Артикул:
    in_s = str(value)
    in_s = in_s.replace("\t", "")
    return in_s.replace("\n", "")

class TermorosScrItem(scrapy.Item):
    # define the fields for your item here like:
    _MAIN_CATEGORY_ = scrapy.Field()
    _NAME_ = scrapy.Field()
    _MODEL_ = scrapy.Field(serializer=serialize_model2)
    _SKU_ = scrapy.Field(serializer=serialize_model2)
    _MANUFACTURER_ = scrapy.Field()
    _PRICE_ = scrapy.Field()
    _UNIT_ = scrapy.Field()
    _ATTRIBUTES_ = scrapy.Field()
    _IMAGE_ = scrapy.Field()
    _IMAGES_ = scrapy.Field()
    _DESCRIPTION_ = scrapy.Field(serializer=serialize_descr)
    _DOCUMENTS_ = scrapy.Field()
    _URL_ = scrapy.Field()

def serialize_descr(value):
    # удаляем всю информацию по данному изделию уточняйте по телефону ...
    in_s = str(value)
    in_s = in_s.strip()
    i = in_s.find('всю информацию по данному изделию уточняйте по телефону')
    if i > -1:
        in_s = in_s[:i]
    else:
        i = in_s.find('Оптовый отдел')
        if i > -1:
            in_s = in_s[:i]
    return in_s

def serializer_peice3(value):
    in_s = str(value)
    in_s = in_s.strip()
    i = in_s.find('руб.')
    if i > -1:
        in_s = in_s[:i]
    return in_s

class MargroidScrItem(scrapy.Item):
    # define the fields for your item here like:
    _MAIN_CATEGORY_ = scrapy.Field()
    _NAME_ = scrapy.Field()
    _MODEL_ = scrapy.Field()
    _SKU_ = scrapy.Field()
    _MANUFACTURER_ = scrapy.Field()
    _PRICE_ = scrapy.Field(serializer=serializer_peice3)
    _UNIT_ = scrapy.Field()
    _ATTRIBUTES_ = scrapy.Field()
    _IMAGE_ = scrapy.Field()
    _IMAGES_ = scrapy.Field()
    _DESCRIPTION_ = scrapy.Field(serializer=serialize_descr)
    _DOCUMENTS_ = scrapy.Field()
    _URL_ = scrapy.Field()

#---------------------------------------
def serialize_model_f(value):
    return f"{value}"

class FamarketScrItem(scrapy.Item):
    # define the fields for your item here like:
    _MAIN_CATEGORY_ = scrapy.Field()
    _NAME_ = scrapy.Field()
    _MODEL_ = scrapy.Field(serializer= serialize_model_f)
    _SKU_ = scrapy.Field(serializer= serialize_model_f)
    _MANUFACTURER_ = scrapy.Field()
    _PRICE_ = scrapy.Field()
    _UNIT_ = scrapy.Field()
    _ATTRIBUTES_ = scrapy.Field()
    _IMAGE_ = scrapy.Field()
    _IMAGES_ = scrapy.Field()
    _DESCRIPTION_ = scrapy.Field()
    _DOCUMENTS_ = scrapy.Field()
    _URL_ = scrapy.Field()


#---------

def serialize_model2(value):
    # удаляем Артикул:
    in_s = str(value)
    s = in_s[in_s.find(':')+2:]
    return f"`{s}"


class SantehgradItem(scrapy.Item):
    # define the fields for your item here like:
    _MAIN_CATEGORY_ = scrapy.Field()
    _NAME_ = scrapy.Field()
    _MODEL_ = scrapy.Field(serializer=serialize_model2)
    _SKU_ = scrapy.Field(serializer=serialize_model2)
    _MANUFACTURER_ = scrapy.Field()
    _PRICE_ = scrapy.Field()
    _UNIT_ = scrapy.Field()
    _ATTRIBUTES_ = scrapy.Field()
    _IMAGE_ = scrapy.Field()
    _IMAGES_ = scrapy.Field()
    _DESCRIPTION_ = scrapy.Field()
    _DOCUMENTS_ = scrapy.Field()
    _URL_ = scrapy.Field()


def serialize_price_steklo(value):
    # удаляем знак рубля
    res = ''
    try:
        res = value[:len(value) - 4]
    except:
        pass
    return res

class StekloCarItem(scrapy.Item):
    # define the fields for your item here like:
    _MAIN_CATEGORY_ = scrapy.Field()
    _NAME_ = scrapy.Field()
    _MODEL_ = scrapy.Field()
    _SKU_ = scrapy.Field()
    _MANUFACTURER_ = scrapy.Field()
    _PRICE_ = scrapy.Field(serializer=serialize_price_steklo)
    _UNIT_ = scrapy.Field()
    _ATTRIBUTES_ = scrapy.Field()
    _IMAGE_ = scrapy.Field()
    _IMAGES_ = scrapy.Field()
    _DESCRIPTION_ = scrapy.Field()
    _DOCUMENTS_ = scrapy.Field()
    _URL_ = scrapy.Field()