
from pyexpat import model
from sqlalchemy.inspection import inspect
from flask import Flask, jsonify, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
db = SQLAlchemy(app)
ma = Marshmallow(app)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Alex:alexAdmin@localhost/expenses'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Alex:alexAdmin@localhost/expenses'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False






class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(80), unique=False, nullable=False)
    lastName = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(64))
    def __init__(self, firstName, lastName, username, email, password, token):
        self.firstName = firstName
        self.lastName = lastName
        self.username = username
        self.email = email
        self.password = password
        self.token = token


class UserSchema(ma.Schema):
    class Meta:
        model = User


@app.route("/")
def index():
    return jsonify({"hello": "Hello World!"})
# CREATE
@app.route('/newuser', methods=['POST'])
def new_user():
    if request.method == 'POST':
        fname = request.json['fname']
        lname = request.json['lname']
        username = request.json['username']
        email = request.json['email']
        password = request.json['password']
        newUser = User(fname, lname, username, email, password, token='')
        db.session.add(newUser)
        db.session.commit()
        return jsonify({"user": "created"}), 200, {'ContentType':'application/json'}

@app.route('/allusers', methods=['GET'])
def all_users():
    all_users = User.query.all()
    user_schema = UserSchema(many=True)
    output = user_schema.dump(all_users).data
    return jsonify(output)
    

if __name__ == '__main__':
    app.debug = True
    app.run()