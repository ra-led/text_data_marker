#!/usr/bin/env python3
from flask import Flask, render_template
from utils.tools import Translater, Database
from utils.front_obj import MarkPage

app = Flask(__name__)
app.config['translater'] = Translater()
app.config['db'] = Database()
app.config['mp'] = MarkPage()

from views import en_mark, early_stop


@app.route('/')
def index():
    return render_template("index.html")
