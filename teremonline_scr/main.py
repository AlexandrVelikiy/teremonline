from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

process = CrawlerProcess(settings)

print('Парсер для  www.teremonline.ru запущен ... ')
print('Детальнная информация о процесе в файле  log.txt')
process.crawl('teremonline_scr')

#print('Парсер для  www.sharangroup.ru запущен ... ')
#print('Детальнная информация о процесе в файле  log.txt')
#process.crawl('sharangroup_scr')


#print('Парсер для  www.termoros.com запущен ... ')
#print('Детальнная информация о процесе в файле  log.txt')
#process.crawl('termoros_scr')

process.start()
print('Парсинг закончен')
input()