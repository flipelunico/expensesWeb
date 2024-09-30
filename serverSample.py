import json
import os
import webbrowser
from functools import wraps

import serverSample
from flask import Flask, jsonify, render_template, request, redirect, url_for, session

import webview

gui_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'gui')  # development path

if not os.path.exists(gui_dir):  # frozen executable path
    gui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui')

#server = Flask(__name__, static_folder=gui_dir, template_folder=gui_dir)
serverSample = Flask(__name__)
serverSample.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1  # disable caching
serverSample.secret_key = 'tu_clave_secreta_aqui'
# Simulated rules storage
rules = [
    {"id": 1, "name": "PDF Documents", "file_type": "pdf", "destination": "Documents", "action": "copy"},
    {"id": 2, "name": "Images", "file_type": "jpg", "destination": "Pictures", "action": "move"},
    {"id": 3, "name": "Music Files", "file_type": "mp3", "destination": "Music", "action": "copy"},
]

def verify_token(function):
    @wraps(function)
    def wrserverer(*args, **kwargs):
        data = json.loads(request.data)
        token = data.get('token')
        if token == webview.token:
            return function(*args, **kwargs)
        else:
            raise Exception('Authentication error')

    return wrserverer


@serverSample.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


@serverSample.route('/')
def landing():
    """
    Render index.html. Initialization is performed asynchronously in initialize() function
    """
    return render_template('index.html', token=webview.token, rules=rules)


@serverSample.route('/init', methods=['POST'])
@verify_token
def initialize():
    """
    Perform heavy-lifting initialization asynchronously.
    :return:
    """
    can_start = serverSample.initialize()

    if can_start:
        response = {
            'status': 'ok',
        }
    else:
        response = {'status': 'error'}

    return jsonify(response)


@serverSample.route('/choose/path', methods=['POST'])
@verify_token
def choose_path():
    """
    Invoke a folder selection dialog here
    :return:
    """
    dirs = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
    if dirs and len(dirs) > 0:
        directory = dirs[0]
        if isinstance(directory, bytes):
            directory = directory.decode('utf-8')

        response = {'status': 'ok', 'directory': directory}
    else:
        response = {'status': 'cancel'}

    return jsonify(response)


@serverSample.route('/fullscreen', methods=['POST'])
@verify_token
def fullscreen():
    webview.windows[0].toggle_fullscreen()
    return jsonify({})


@serverSample.route('/open-url', methods=['POST'])
@verify_token
def open_url():
    url = request.json['url']
    webbrowser.open_new_tab(url)

    return jsonify({})


@serverSample.route('/do/stuff', methods=['POST'])
@verify_token
def do_stuff():
    result = serverSample.do_stuff()

    if result:
        response = {'status': 'ok', 'result': result}
    else:
        response = {'status': 'error'}

    return jsonify(response)

@serverSample.route('/')
def index():
    return redirect(url_for('rules'))

@serverSample.route('/rules')
def rules_page():
    dark_mode = session.get('dark_mode', True)
    return render_template('index.html', active_page='rules', rules=rules, dark_mode=dark_mode)

@serverSample.route('/logs')
def logs_page():
    dark_mode = session.get('dark_mode', True)
    return render_template('index.html', active_page='logs', dark_mode=dark_mode)

@serverSample.route('/settings')
def settings_page():
    dark_mode = session.get('dark_mode', True)
    return render_template('index.html', active_page='settings', dark_mode=dark_mode)

@serverSample.route('/toggle_dark_mode', methods=['POST'])
def toggle_dark_mode():
    current_mode = session.get('dark_mode', True)
    session['dark_mode'] = not current_mode
    return redirect(url_for('settings_page'))

@serverSample.route('/add_rule', methods=['POST'])
def add_rule():
    data = request.form
    new_rule = {
        "id": len(rules) + 1,
        "name": data['name'],
        "file_type": data['file_type'],
        "destination": data['destination'],
        "action": data['action']
    }
    rules.serverend(new_rule)
    return redirect(url_for('rules_page'))

@serverSample.route('/delete_rule/<int:rule_id>', methods=['POST'])
def delete_rule(rule_id):
    global rules
    rules = [rule for rule in rules if rule['id'] != rule_id]
    return redirect(url_for('rules_page'))