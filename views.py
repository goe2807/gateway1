from gateway import app, db
from models import User, Mesaj, Modem
from forms import LoginForm
from flask import render_template, redirect, request, url_for, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from uuid import uuid4
from functools import wraps
import jwt, math
import time, datetime
from driver import *
from utils import *

def token_requiered(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']
            if not token:
                return jsonify({'message' : 'Token is missing!'}), 401

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                current_user = User.query.filter_by(public_id=data['public_id']).first()
            except:
                return jsonify({'message' : 'Token is invalid!'}), 401

            return f(current_user, *args, **kwargs)
        return decorated

# Rute pentru api fdfd gfgsfd
@app.route('/api_login')
def api_login():
    auth = request.authorization
    add_ip =request.remote_addr

    if not auth or not auth.username or not auth.password:
        writelog(add_ip + ' Could not verify', 1)
        return make_response('Could not verify', 401, {'WWW=Authenticate' : 'Basic realm = "Login required"'})
    user =User.query.filter_by(username=auth.username).first()

    if not user:
        writelog(add_ip + ' Could not verify', 1)
        return make_response('Could not verify', 401, {'WWW=Authenticate' : 'Basic realm = "Login required"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=360)}, app.config['SECRET_KEY'])
        writelog(add_ip + ' Am emis tokenul pentru ' + user.username, user.id)
        return jsonify({'token' : token.decode('UTF-8')})
    writelog(add_ip + ' Could not verify', 1)
    return make_response('Could not verify', 401, {'WWW=Authenticate' : 'Basic realm = "Login required"'})

@app.route('/api_mesaj', methods = ['POST'])
@token_requiered
def api_create_mesaj(current_user):
    data = request.get_json()
    if data['name']  == '' or data['mesaj'] == '':
        return jsonify({'message' : 'Aveti campuri goale'})
    elif len(data['telefon']) > 10 or len(data['telefon']) < 10:
        return jsonify({'message' : 'Telefonul trebuie sa contina 10 caractere'})
    else:
        mesaj_lenght = len(data['mesaj'])
        print(mesaj_lenght)
        mesaj_count = math.ceil(mesaj_lenght / 160)
        new_mesaj = Mesaj(name = data['name'],
                            telefon = data['telefon'],
                            mesaj = data['mesaj'],
                            mesaj_count = mesaj_count,
                            mesaj_lenght = mesaj_lenght,
                            user_id = current_user.id,
                            is_sent = False)
        db.session.add(new_mesaj)
        db.session.commit()
        writelog('Mesaj adaugat prin api', current_user.id)
        return jsonify({'message' : 'Message sent'})

# Rute pentru webclient
@app.route('/')
def index():
    firstuser = User.query.first()
    return render_template('index.html')

@app.route('/mesaje')
def mesaje():
    all_mesaje = Mesaj.query.all()
    return render_template('mesaje.html', all_mesaje=all_mesaje)

@app.route('/logs')
def logs():
    all_logs = Logs.query.all()
    return render_template('logs.html', all_logs=all_logs)

@app.route('/modems')
def modem():
    all_modems = Modem.query.all()
    return render_template('modems.html', all_modems=all_modems)

@app.route('/login')
def login():
    form.LoginForm()
    return render_template('index.html', form=form)

@app.route('/close_driver')
def close_driver():
    myWebsite.letsclose()

@app.route('/send_test')
def send_test():
    modem1 = Modem.query.filter_by(name='google_message_web').first()
    mesaje_netrimise = Mesaj.query.filter_by(is_sent=False).all()
    if mesaje_netrimise and modem1.status == 'running':
        for mesaj in mesaje_netrimise:

            send_sms(mesaj.name, mesaj.telefon, mesaj.mesaj)
            mesaj.date_sent = datetime.utcnow()
            mesaj.is_sent = True
            db.session.commit()
            time.sleep(2)
        modem1 = Modem.query.filter_by(name='google_message_web').first()
        modem1.status = 'running'
        db.session.commit()
        return "<a href='/'>am trimis ceva... cred</a>"
    elif modem1.status != 'running':
        return "<a href='/'>Modemul nu este pornit </a>"
    else:
        return "nu pot trimite nimic"
