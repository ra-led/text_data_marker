import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from yandex_translate import YandexTranslate
from conf import CFG

sql_sample = '''
SELECT *
FROM {table}
WHERE id IN (
    SELECT id
    FROM {table}
    ORDER BY RANDOM()
    LIMIT {n_rows}
    )
'''
sql_delete = 'DELETE FROM {table} WHERE id = {row_id}'
sql_drop = 'DROP TABLE {table}'
sql_read = 'SELECT * FROM {table} WHERE id = {row_id}'


class Database:
    def __init__(self):
        self.database = create_engine('sqlite:///labels.db')
        for lang in CFG['langs']:
            reviews = pd.read_sql_query(
                'PRAGMA table_info({}_reviews)'.format(lang),
                self.database
            )
            if reviews.empty:
                reviews = (
                    pd
                    .read_csv(
                        'uniformed_dataset_{}.csv'.format(lang),
                        sep='\t'
                    )
                    .fillna('')
                )
                reviews.to_sql(
                    '{}_reviews'.format(lang),
                    self.database,
                    if_exists='append',
                    index_label='id'
                )
        print('DB init completed')

    def write_rows(self, rows, table):
        rows = pd.DataFrame(rows)
        try:
            last_id = self.query('select max(id) from {}'.format(table)).iloc[0, 0]
            rows.index += last_id + 1
        except OperationalError:
            pass
        rows.to_sql(table, self.database, if_exists='append', index_label='id')

    def query(self, sql):
        return pd.read_sql_query(sql, self.database)

    def get_random_sample(self, table, n_rows=1):
        sql = sql_sample.format(table=table, n_rows=n_rows)
        return self.query(sql)

    def delete_row(self, table, row_id):
        sql = sql_delete.format(table=table, row_id=row_id)
        with self.database.connect() as con:
            con.execute(sql)

    def delete_table(self, table):
        sql = sql_drop.format(table=table)
        with self.database.connect() as con:
            con.execute(sql)

    def read_row(self, table, row_id):
        sql = sql_read.format(table=table, row_id=row_id)
        return self.query(sql).iloc[0]


class Translater:
    def __init__(self, target='ru'):
        self.target = target
        self.api = YandexTranslate(CFG['ya_tr_api'])

    def translate(self, text):
        response = self.api.translate(text, self.target)

        return response['text']
