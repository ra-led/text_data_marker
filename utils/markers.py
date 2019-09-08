import pandas as pd
from yandex_translate import YandexTranslate
from conf import CFG


class Marker:
    def __init__(self, data_csv):
        self.df = pd.read_csv(data_csv, sep='\t').fillna('')

        self.rows = []

        self.sem_class = CFG['sentiment']
        self.tag_class = CFG['tags']
        self.bug_class = CFG['bugs']

    def save_row(self, title, review, form):
        row = {'title': title, 'review': review}

        row.update(form)
        self.rows.append(row)

    def srore_xlsx(self, fname):
        pd.DataFrame(self.rows).fillna(0).to_excel(fname, index=False)


class Translater:
    def __init__(self, target='ru'):
        self.target = target
        self.api = YandexTranslate(CFG['ya_tr_api'])

    def translate(self, text):
        response = self.api.translate(text, self.target)

        return response['text']
