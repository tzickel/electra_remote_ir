from json import load, dump
from enum import IntEnum
from flask import Flask, request, jsonify, redirect
from .read import FanSpeed, Modes
from .send import send
try:
    from .serve_homekit import threaded
except:
    def threaded(getter, setter, port):
        pass

try:
    with open('state.json', 'rb') as f:
        initial_state = json.load(f)
except:
#    initial_state = {'power_cycle': False, 'speed': FanSpeed.medium, 'temp': 25, 'mode': Modes.cool}
    initial_state = {'power_cycle': False, 'speed': FanSpeed.low, 'temp': 27, 'mode': Modes.cool}
min_temp = 16
max_temp = 30


def verify(data):
    temp = data.get('temp')
    if temp is not None:
        temp = int(temp)
        if temp < 16 or temp > 30:
            raise Exception('Invalid temprature')


class Webify(object):
    def __init__(self, dict_, verify=None):
        if not isinstance(dict_, dict):
            raise TypeError('Please pass a dictionary')
        self._dict = dict_.copy()
        self._verify = verify

    def set(self, data):
        if not isinstance(data, dict):
            raise ValueError('Invalid input')
        if self._verify:
            self._verify(data)
        tmp = self._dict.copy()
        for key, current_value in tmp.items():
            if key in data:
                new_value = data[key]
                if isinstance(current_value, IntEnum):
                    if isinstance(new_value, int):
                        tmp[key] = type(tmp[key])(new_value)
                    elif isinstance(new_value, str):
                        tmp[key] = type(tmp[key])[new_value]
                elif isinstance(current_value, bool):
                    tmp[key] = bool(new_value)
                elif isinstance(current_value, int):
                    tmp[key] = int(new_value)
                else:
                    tmp[key] = new_value
        self._dict = tmp
        try:
            with open('state.json', 'wb') as f:
                json.dump(self._dict, f)
        except:
            pass

    def get(self):
        return {k: self.sane_value(v) for k, v in self._dict.items()}

    def sane_value(self, item):
        if isinstance(item, IntEnum):
            return item.name
        elif isinstance(item, dict):
            return item['value']
        else:
            return item

    def render(self, url):
        html = '<html><head><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Remote"><meta http-equiv="refresh" content="30"><meta name="viewport" content="width=device-width, initial-scale=1"></head><style>input{\nwidth: 100%;\nfont-size: large;\n}</style></head><body>'
        for k, v in self._dict.items():
            if isinstance(v, IntEnum):
                for item in type(v):
                    html += '<form action="%s?%s=%s" method="post">' % (url, k, item.name)
                    html += '<input type="submit" value="%s%s">' % (item.name, ' V' if v == item else '')
                    html += '</form>'
            elif isinstance(v, bool):
                html += '<form action="%s?%s=%s" method="post">' % (url, k, v)
                html += '<input type="submit" value="%s%s">' % (k, ' V' if v == True else '')
                html += '</form>'
            elif isinstance(v, int):
                for i in range(max_temp, min_temp - 1, -1):
                    html += '<form action="%s?%s=%s" method="post">' % (url, k, i)
                    html += '<input type="submit" value="%s%s">' % (i, ' V' if v == i else '')
                    html += '</form>'
            html += '<br>'
        html += '</body></html>'
        return html


app = Flask(__name__)
web = Webify(initial_state, verify)


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.route('/', methods=['GET'])
def index():
    return web.render('/state')


@app.route('/state', methods=['POST'])
def set_state():
    data = request.get_json(silent=True)
    if data is None:
        data = request.form
    if len(data) == 0:
        data = request.args
    web.set(data)
    # TODO Refactor this outside
    try:
        send(gpio_pin, **web._dict)
    except:
        # TODO add error handling
        pass
    finally:
        web.set({'power_cycle': False})
    return redirect("/", code=302)


@app.route('/state', methods=['GET'])
def get_state():
    return jsonify(web.get())


def homekit_getter(name):
    if name == 'mode':
        mode = web.get()['mode']
        if mode == 'heat':
            return 1
        elif mode == 'cool':
            return 2
        else:
            return 3
    elif name == 'temp':
        temp = web.get()['temp']
        return temp


def homekit_setter(name, value):
    if name == 'mode':
        if value == 1:
            web.set({'mode': 'heat'})
        elif value == 2:
            web.set({'mode': 'cool'})
    elif name == 'temp':
        web.set({'temp': int(value)})
    try:
        send(gpio_pin, **web._dict)
    except:
        # TODO add error handling
        pass


if __name__ == "__main__":
    import os
    host = os.environ.get('LISTEN_HOST')
    port = os.environ.get('LISTEN_PORT')
    homekit_port = int(os.environ.get('HOMEKIT_PORT', '51827'))
    gpio_pin = int(os.environ.get('GPIO_PIN', '25'))
    threaded(homekit_getter, homekit_setter, homekit_port)
    if host:
        if port:
            app.run(host, port)
        else:
            app.run(host)
    else:
        app.run()
