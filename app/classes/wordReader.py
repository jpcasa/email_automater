import json
import docx2txt
import pandas as pd
from docx.api import Document

class WordReader:

    def __init__(self, word='word/', images='img'):
        self.word_location = word
        self.images_location = images


    def to_text(self, p):
        """Converts cell contents into text"""
        rs = p._element.xpath('.//w:t')
        return u" ".join([r.text for r in rs])


    def get_tables(self, file_path):
        """Gets the tables in the Docx"""
        document = Document(file_path)
        tables = []

        for table in document.tables:
            data = []
            keys = None

            for i, row in enumerate(table.rows):
                text = (self.to_text(cell) for cell in row.cells)
                if i == 0:
                    keys = tuple(text)
                    continue
                row_data = dict(zip(keys, text))
                data.append(row_data)

            tables.append(pd.DataFrame(data))

        return tables


    def extract_images(self, file_path):
        """Extract Images from the doc"""
        docx2txt.process(file_path, "img")
