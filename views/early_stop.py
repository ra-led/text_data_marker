from flask import request, make_response

from app import app

@app.route('/early_stop', methods=['GET'])
def early_stop():
    app.config['ml'].store_probs()
    return make_response('Probs stored')
