import json
from flask import Flask, render_template, request, redirect, url_for, make_response
from classeviva import Utente

app = Flask(__name__)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    uid = data['uid']
    pwd = data['pwd']

    user_token = Utente().login(uid, pwd)

    if user_token != '':
        return {'token': user_token}
    else:
        return {'error': "Credenziali non valide. Riprova."}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)


