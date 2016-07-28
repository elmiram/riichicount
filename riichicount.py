# !flask/bin/python
__author__ = 'elmira'

from flask import Flask
from flask import render_template, url_for, request
from generatehand import Hand, random_pick

app = Flask(__name__, static_folder='./static/', static_path='/static')


@app.route('/')
def hello_world():
    isvalid = random_pick([True, False], [0.8, 0.2])
    a = Hand()
    while a.isvalid != isvalid:
        a = Hand()
    return render_template('text.html', hand=a)
if __name__ == '__main__':
    app.run(debug=True)
