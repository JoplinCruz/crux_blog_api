from flask import Flask, request, make_response, jsonify
import jwt
from functools import wraps
from datetime import datetime, timedelta
from data_structure import app, db, Post, User




# Auth |------------------------;
def request_token(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if "access-token" not in request.headers:
            return jsonify({"message": "token not included. change login"}), 401
        else:
            request_token = request.headers["access-token"]
            try:
                token = jwt.decode(jwt=request_token, key=app.secret_key, algorithms=["HS256"])
            except:
                return jsonify({"message": "invalid token"}), 401
            
        user = User.query.filter_by(id=token["id"]).first()
        
        return function(user, *args, **kwargs)
    return decorated


@app.route("/login", methods=["GET"])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response("invalid login", 401, {"WWW-Authenticate": "Basic Realm='invalid login'"})
    
    user = User.query.filter_by(username=auth.username).first()
    if not user or user.password != auth.password:
        return make_response("invalid login", 401, {"WWW-Authenticate": "Basic Realm='invalid login'"})
    
    token = jwt.encode(payload={"id": user.id, "exp": datetime.now()+timedelta(hours=7)}, key=app.secret_key, algorithm="HS256")
    
    return jsonify({"token": token}), 200



# Post API |--------------------;

@app.route("/post")
@request_token
def posts(user):
    posts = Post.query.all()
    post_list = []
    for raw_post in posts:
        post={"id": raw_post.id,
              "title": raw_post.title,
              "text": raw_post.text,
              "created": raw_post.created}
        user = User.query.filter_by(id=raw_post.user_id).first()
        if user:
            post.update(author=user.firstname)
            
        post_list.append(post)
    
    return jsonify({"posts": post_list}), 200

@app.route("/post/<int:post_id>", methods=["GET", "PUT"])
@request_token
def post(user, post_id):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return jsonify({"message": "post not found"}), 404
    if request.method == "GET":
        get_post = {"id": post.id,
                    "title": post.title,
                    "text": post.text,
                    "created": post.created}
        user = User.query.filter_by(id=post.user_id).first()
        if user:
            get_post.update(author=user.firstname)
        
        return jsonify({"post": get_post}), 200
    
    title = request.json.get("title", None)
    text = request.json.get("text", None)
    
    if title:
        post.title = title
    if text:
        post.text = text
    if title or text:
        post.user_id = user.id
    
    db.session.commit()
    
    return jsonify({"message": "post <{}>, updated".format(post.title)}), 200

@app.route("/post", methods=["POST"])
@request_token
def create_post(user):
    title = request.json.get("title", None)
    text = request.json.get("text", None)
    
    if Post.query.filter_by(title=title).first():
        return jsonify({"message": "post title already exist"}), 401
    
    post = Post(title=title,
                text=text,
                user_id=user.id)
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({"message": "post <{}>, created successful".format(title)}), 200

@app.route("/post/<int:opst_id>", methods=["DELETE"])
@request_token
def erase_post(user, post_id):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return jsonify({"message": "post not found"}), 404
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({"message": "post deleted successful"}), 200




# Post API |--------------------;
@app.route("/user")
@request_token
def users(user):
    users = User.query.all()
    users_list = []
    for raw_user in users:
        user = {"id": raw_user.id,
                "username": raw_user.username,
                "firstname": raw_user.firstname,
                "lastname": raw_user.lastname,
                "email": raw_user.email,
                "birth": raw_user.birth,
                "password": raw_user.password,
                "created": raw_user.created}
        
        users_list.append(user)
    
    return jsonify({"users": users_list}), 200

@app.route("/user/<int:user_id>", methods=["GET", "PUT"])
@request_token
def user(user, user_id):
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return jsonify({"message": "user not found"}), 404
    if request.method == "GET":
        get_user = {"id": user.id,
                    "username": user.username,
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                    "email": user.email,
                    "birth": user.birth,
                    "password": user.password,
                    "created": user.created}
        
        return jsonify({"user": get_user}), 200
    
    username = request.json.get("username", None)
    firstname = request.json.get("firstname", None)
    lastname = request.json.get("lastname", None)
    email = request.json.get("email", None)
    birth = request.json.get("birth", None)
    password = request.json.get("password", None)
    
    if username:
        user.username = username
    if firstname:
        user.firstname = firstname
    if lastname:
        user.lastname = lastname
    if email:
        user.email = email
    if birth:
        user.birth = birth
    if password:
        user.password = password
    
    db.session.commit()
    
    return jsonify({"message": "user <{}> update successful".format(user.username)}), 200

@app.route("/user", methods=["POST"])
@request_token
def create_user(user):
    username = request.json.get("username", None)
    firstname = request.json.get("firstname", None)
    lastname = request.json.get("lastname", None)
    email = request.json.get("email", None)
    birth = request.json.get("birth", None)
    password = request.json.get("password", None)
    
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"message": "user <{}>, already exist".format(user.username)}), 401
    
    user = User(username=username,
                firstname=firstname,
                lastname=lastname,
                email=email,
                birth=birth,
                password=password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "user <{}>, created successful".format(user.username)}), 200

@app.route("/user/<int:user_id>", methods=["DELETE"])
@request_token
def erase_user(user, user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "user not found"}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "user deleted successful"}), 200



if __name__ == "__main__":
    app.run(host="localhost", port=5050, debug=True)