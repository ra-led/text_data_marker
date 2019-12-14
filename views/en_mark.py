import json
import pandas as pd
import numpy as np

from flask import request, render_template

from app import app
from conf import CFG
from utils.ml import Learner

app.config['ml'] = Learner('en', app.config['db'])

@app.route('/en_mark', methods=['GET'])
def en_mark_start():
    app.config['ml'].load_probs()
    source = np.random.choice(CFG['tags'])
    sample = app.config['ml'].sample_top(source)
    sample = app.config['db'].read_row('en_reviews', sample['id'])
    app.config['db'].delete_row('en_reviews', sample['id'])

    return render_template(
        'en_mark.html',
        title=sample['title'],
        content=sample['content'],
        translated=app.config['translater'].translate(
            sample['title'] + '.' + sample['content']
        ),
        tags=app.config['mp'].tag_table(),
        source=source
    )


@app.route('/en_mark', methods=['POST'])
def en_mark_next():
    params = request.form.to_dict()
    marked = {
        'title': params.pop('title'),
        'content': params.pop('content'),
        'tags': json.dumps(params)
    }
    app.config['db'].write_rows([marked], 'en_marked')

    if np.random.rand() > 0.1:
        source = np.random.choice(CFG['tags'])
        sample = app.config['ml'].sample_top(source)
        sample = app.config['db'].read_row('en_reviews', sample['id'])
        app.config['db'].delete_row('en_reviews', sample['id'])
    else:
        source = 'RANDOM'
        sample = app.config['db'].get_random_sample('en_reviews').iloc[0]
        app.config['db'].delete_row('en_reviews', sample['id'])

    return render_template(
        'en_mark.html',
        title=sample['title'],
        content=sample['content'],
        translated=app.config['translater'].translate(
            sample['title'] + '.' + sample['content']
        ),
        tags=app.config['mp'].tag_table(),
        source=source
    )
