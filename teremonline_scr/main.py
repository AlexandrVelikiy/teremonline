from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

process = CrawlerProcess(settings)

#print('Парсер для  www.teremonline.ru запущен ... ')
#print('Детальнная информация о процесе в файле  log.txt')
#process.crawl('teremonline_scr')

#print('Парсер для  www.sharangroup.ru запущен ... ')
#print('Детальнная информация о процесе в файле  log.txt')
#process.crawl('sharangroup_scr')

#print('Парсер для  www.termoros.com запущен ... ')
#print('Детальнная информация о процесе в файле  log.txt')
#process.crawl('termoros_scr')

#print('Парсер для  www.margroid.ru запущен ... ')
#print('Детальнная информация о процесе в файле  log.txt')
#process.crawl('margroid_scr')

#print('Парсер для  www.margroid.ru запущен ... ')
#print('Детальнная информация о процесе в файле  log.txt')
#process.crawl('famarket_scr')

#print('Парсер для  www.santehgrad.ru запущен ... ')
#print('Детальнная информация о процесе в файле  log.txt')
#process.crawl('santehgrad_scr')


print('Парсер для  www.steklo-car.ru запущен ... ')
print('Детальнная информация о процесе в файле  log.txt')
process.crawl('steklo_car_scr')

process.start()
print('Парсинг закончен')
input()