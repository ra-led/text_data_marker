#!/usr/bin/env python3
from flask import Flask, render_template

app = Flask(__name__)

from views import ru_mark, en_mark, early_stop


@app.route('/')
def index():
    return render_template("index.html")
