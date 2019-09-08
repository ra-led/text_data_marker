from flask import request, make_response

from app import app

@app.route('/early_stop', methods=['GET'])
def early_stop():
    app.config['marker'].srore_xlsx(f'marked_r.xlsx')

    return make_response('XLSX stored')
