from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import jwt
import hashlib
import datetime
from functools import wraps


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'Azerty654'

db = SQLAlchemy(app)
ma = Marshmallow(app)

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'msg': 'Toekn is missing'}), 401
        try:
            token_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            username = token_data['user']
        except:
            return jsonify({'msg': 'Token Invalid'}), 401

        return func(username,*args, **kwargs)
    return decorated    




# DB MODELS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        

#MARSHMALLOW MODELS
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'password')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# ROUTER
#POST NEW USER
@app.route('/newuser', methods=['POST'])
def post():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    password = hashlib.md5(password.encode()).hexdigest()
    newUser = User(username, email, password)

    db.session.add(newUser)
    db.session.commit()

    return user_schema.dump(newUser)


#POST LOGIN
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    entered_password = request.json['password']
    user = User.query.filter(User.username == username).first()
    if not user:
        return {'msg': 'User Not Found'}, 400
    else:
        if (hashlib.md5(entered_password.encode()).hexdigest() == user.password):
            exptime = datetime.datetime.utcnow() + datetime.timedelta(minutes= 1)
            token = jwt.encode({'user': username, 'exp': exptime}, app.config['SECRET_KEY'], algorithm="HS256")
            return jsonify({'token': token})
        else :
            return {'msg': 'Wrong Password'}, 400



#GET INDEX
@app.route('/', methods=['GET'])
def get():
    return jsonify({'msg' : 'Welcome'})


# GET ALL USERS
@app.route('/users', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    return users_schema.dump(all_users)

#GET UNPROTECTED
@app.route('/all', methods=['GET'])
def all():
    return jsonify({'msg': 'Unprotected'})


#GET PROTECTED
@app.route('/loged', methods=['GET'])
@token_required
def portected(username):
    return jsonify({f'msg': 'Welcome {username}'})


#GET ONE USER
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if (user == None):
        return {'msg': 'No User'}
    else: 
        return  user_schema.dump(user)




# APP RUN 
if __name__ == '__main__':
    app.run(debug=True)