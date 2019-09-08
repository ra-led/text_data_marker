import pandas as pd

from flask import request, render_template

from utils.markers import Marker, Translater
from app import app


@app.route('/en_mark', methods=['GET'])
def en_mark_start():
    app.config['marker'] = Marker('sample_en.csv')
    app.config['translater'] = Translater()

    sample = app.config['marker'].df.iloc[0]
    return render_template(
        'en_mark.html',
        title=sample['Title'],
        review=sample['Review'],
        translated=app.config['translater'].translate(sample['Review']),
        i=0,
        total=app.config['marker'].df.shape[0],
        sem=app.config['marker'].sem_class,
        tag=app.config['marker'].tag_class,
        bug=app.config['marker'].bug_class
        )


@app.route('/en_mark', methods=['POST'])
def en_mark_next():
    params = request.form.to_dict()

    i = int(params.pop('index'))

    if (i + 1) < app.config['marker'].df.shape[0]:
        i += 1
    else:
        app.config['marker'].srore_xlsx('marked_r_en.xlsx')

    sample = app.config['marker'].df.iloc[i]

    app.config['marker'].save_row(sample['Title'], sample['Review'], params)

    return render_template(
        'en_mark.html',
        title=sample['Title'],
        review=sample['Review'],
        translated=app.config['translater'].translate(sample['Review']),
        i=i,
        total=app.config['marker'].df.shape[0],
        sem=app.config['marker'].sem_class,
        tag=app.config['marker'].tag_class,
        bug=app.config['marker'].bug_class
        )
