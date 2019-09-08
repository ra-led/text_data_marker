#!/usr/bin/env python3

from app import app

if __name__ == '__main__':
    # run app
    app.debug = True
    host = '0.0.0.0'
    port = 5050

    app.run(host=host, port=port)
