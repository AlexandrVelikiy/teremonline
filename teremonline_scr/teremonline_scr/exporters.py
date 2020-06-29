from scrapy.exporters import CsvItemExporter

class CsvCustomSeperator(CsvItemExporter):
    def __init__(self, *args, **kwargs):
        #kwargs['encoding'] = 'utf-8'

        kwargs['fields_to_export'] = ["_MAIN_CATEGORY_", "_NAME_", "_MODEL_", "_SKU_",
                                     "_MANUFACTURER_", "_PRICE_", "_UNIT_", "_ATTRIBUTES_",
                                      "_IMAGE_", "_IMAGES_", "_DESCRIPTION_",
                                       "_DOCUMENTS_", "_URL_"]
        kwargs['delimiter'] = ';'
        #kwargs['format'] = 'csv'
        #kwargs['uri'] = 'file:///export111.csv'
        super(CsvCustomSeperator, self).__init__(*args, **kwargs)