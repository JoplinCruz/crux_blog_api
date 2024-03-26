from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]  = "sqlite:///my_blog.db"
app.config["SECRET_KEY"] = "HFJ+|DEVICE|@#/@STRUCTURE=#1101001%"

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
    def __repr__(self):
        return "<{},{}>".format(self.id, self.title)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    firstname = db.Column(db.String(200), nullable=False)
    lastname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    birth = db.Column(db.String(60), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now())
    posts = db.relationship("Post", backref="user", lazy=True)
    
    def __repr__(self):
        return "<{},{}>".format(self.id, self.username)

def create_database():
    
    with app.app_context() as context:
        context.push()
        db.drop_all()
        db.create_all()
    
    
    # first user |--------------------------;
    user = User(username="joplincruz",
                firstname="Joplin",
                lastname="Cruz",
                email="joplin.da.cruz@gmail.com",
                birth="10/01/1974",
                password="MyPass123456!")
    
    post = Post(title="My First Post",
                text="Bla bla bla is not a better text, but is this a better in moment.")
    
    db.session.add(user)
    db.session.add(post)
    db.session.commit()


if __name__ == "__main__":
    create_database()