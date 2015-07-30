# encoding: utf-8
# author:   Jan Hybs
from flask.templating import render_template
import markdown
from server import app, mongo
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
    root = mongo.get_ist_by_id()
    html += '\n<ul class="treeView">' + create_list(root, True) + '</ul>'
    print db.ist.find({})
    # result = list(mongo.pluck_field())
    # if result:
    #     data = result[0]['data']
    #     print data
    return render_template('index.html', content=html)


def create_list(item, collapsible=False):
    html = "<li>"
    if item['children']:
        html += "<a href='#'>{:s}</a>".format(item['tag'])
        html += "<ul class='collapsibleList'>" if collapsible else "<ul>"
        for child_id in item['children']:
            json_child = mongo.get_ist_by_id(child_id)
            html += create_list(json_child)
        html += "</ul>"
    else:
        html += "{:s}".format(item['tag'])
    html += "</li>"
    return html