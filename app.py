from flask import Flask, render_template, request, redirect, session, current_app, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_APP_KEY'] = '6acMYe38RSkC2ONm3nKVs4JQOSyCkDdX0tHMtuwGnS2NNYC2KYhIG6IyRauCCFbrRDQMl7GUwnw273WOboJSqnQ6HoKBymZenwbM'
app.config['SECRET_KEY'] = 'sas'

db = SQLAlchemy(app) 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

class LoginAllowedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    token = db.Column(db.String(100), nullable=False)

with app.app_context():  # Create an application context before creating the tables
    db.create_all()

@app.route('/')
def sign_in_with_main():
    # Triggered when the user clicks "Sign in with Main"
    return render_template('sign_in.html')

@app.route('/get-temp-token')
def get_temp_token():
    # Triggered when the user submits the form to sign in with Main
    key = current_app.config['SECRET_APP_KEY']
    response = requests.post("http://localhost:8000/accounts/get-temp-token/", data={"secret_key": key})

    response_data = response.json()
    temp_token = response_data.get("token")
    # Redirect the user to the Main Website with the access token
    
    return redirect(f'http://localhost:8000/accounts/sign-in-with-techsnap?access_token={temp_token}')

@app.route('/save-token', methods=['POST'])
def verification_token_with_username():
    data = request.get_json()

    # Get token and username from the request
    token = data.get('token')
    username = data.get('username')

    # Validate and save to the database
    if User.query.filter_by(username=username).first():
        prev_token = LoginAllowedToken.query.filter_by(username=username).first()
        if prev_token:
            prev_token.token = token
        else :
            new_token = LoginAllowedToken(token=token, username=username)
            db.session.add(new_token)
        db.session.commit()

        return jsonify({'message': 'Token and username saved successfully!'})
    
    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()

    new_token = LoginAllowedToken(token=token, username=username)
    db.session.add(new_token)
    db.session.commit()
    return jsonify({'message': 'Token and username saved successfully!'})


@app.route('/callback')
def callback():
    # Callback route on the Flask app to handle the final access token
    access_token = request.args.get('access_token')

    token = LoginAllowedToken.query.filter_by(token=access_token).first()
    # Validate the access token and store user details in the session
    if token:
        session['username'] = token.username
        print(token.username)
        db.session.delete(token)
        db.session.commit()
    return redirect('/index')  # Redirect to a dashboard or home page

@app.route('/index')
def index():
    try:
        username = session['username']
    except:
        username = ""
    return render_template('index.html', username=username)

@app.route('/logout')
def logout():
    session.clear()

    return redirect('/index')

if __name__ == '__main__':
    app.run(debug=True)
