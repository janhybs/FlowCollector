# encoding: utf-8
# author:   Jan Hybs
from flask.templating import render_template
import markdown
from server import app
from server.utils.flask_utils import with_title


@app.route('/')
@with_title('Browse')
def index():
    text = \
"""
# Flow collector

Simple collection of profiler metrics from project [Flow123d](https://github.com/flow123d/flow123d)
"""
    html = markdown.markdown(text)
    return render_template('index.html', content=html)