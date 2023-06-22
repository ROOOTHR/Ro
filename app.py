from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
# from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_login import LoginManager, logout_user, current_user, login_user, UserMixin, login_required
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
from flask.json import jsonify

app = Flask(__name__)
app.config["SECRET_KEY"] = 'test'
# bootstrap = Bootstrap(app)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456789@localhost:3306/bloginfo"
db = SQLAlchemy(app)
CORS(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(45), unique=True)
    password = db.Column(db.String(45))
    name = db.Column(db.String(45))
    about = db.Column(db.Text)

    def validate_password(self, password):
        return self.password == password

    def __init__(self, username, name, password, about):
        self.name = name
        self.password = password
        self.username = username
        self.about = about

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(256))
    createtime = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blog_id = db.Column(db.Integer, db.ForeignKey("blog.id"))
    blog = db.relationship("Blog", backref="blog")
    user = db.relationship("User", backref="use")


class Blog(db.Model):
    __tablename__ = "blog"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(45))
    text = db.Column(db.Text)
    createtime = db.Column(db.String(45))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='user')


@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print('Login successfully')
        return jsonify(success=True, message='Login successfully')
    username_form = request.form.get('username')
    password_form = request.form.get('password')
    print(username_form, password_form)
    user_dict = {
        'username': username_form,
        'password': password_form
    }
    print(user_dict)
    # Check whether user exists
    user = User.query.filter_by(username=username_form).first()
    print(user)
    # session['user'] = user.username
    password = User.query.filter_by(password=password_form).first()
    print(password)
    if user is not None and user.validate_password(password_form):
        login_user(user)
        user_info = {
            'id': user.id,
            'username': user.username,
            'password': user.password
        }
        print(login_user(user))
        return jsonify(success=True, message='Login successfully', user=user_info)
    else:
        return jsonify(success=False, message='Invalid username or password', user_dict=user_dict)


@app.route('/api/register', methods=['GET', 'POST'])
def register():
    username_form1 = request.form.get('username')
    password_form1 = request.form.get('password')
    name_form1 = request.form.get('name')
    print(username_form1, password_form1, name_form1)
    user_dict1 = {
        'username': username_form1,
        'password': password_form1,
        'name': name_form1
    }
    print(user_dict1)

    username = User.query.filter_by(username=username_form1).first()
    print(username)
    # password = User.query.filter_by(password=password_form1).first()
    # print(password)
    if username is None:
        about = "这个人很神秘，什么都没有写"
        newUser = User(username=username_form1, password=password_form1, name=name_form1, about=about)
        db.session.add(newUser)
        db.session.commit()
        user_dict1 = {
            'username': newUser.username,
            'password': newUser.password,
            'name': newUser.name
        }
        return jsonify(success=True, message='Register successfully', user_dict=user_dict1)
    else:
        return jsonify(success=False, message='Invalid username or password', user_dict=user_dict1)


@app.route('/api/dashboard', methods=['GET', 'POST'])
# @login_required
def dashboard():
    # user = request.json['user']
    # username = user.username
    #
    # print(login_user(username))
    # if current_user.is_authenticated:
    blogs = Blog.query.order_by(Blog.createtime.desc()).all()
    blogs_list = []
    for blog in blogs:
        blog_dict = {
            'blogtitle': blog.title,
            'blogtext': blog.text,
            'blog_user_id': blog.user_id,
            'blog_create_time': blog.createtime,
            'blogid': blog.id
        }
        blogs_list.append(blog_dict)
    return jsonify({'blogs': blogs_list})


@app.route('/api/user', methods=['GET', 'POST'])
def user():
    users = User.query.all()
    user_list = []
    for user in users:
        user_dict = {
            'username': user.username,
            'password': user.password,
            'id': user.id,
            'about': user.about
        }
        user_list.append(user_dict)
    return jsonify(user_list)


# @app.route('/api/user_blog_information', methods=['GET', 'POST'])
# def user_blog_information():
#     user_blog_result = []
#     users = User.query.all()
#     for user in users:
#         user_dict = {
#             "id": user.id,
#             "username": user.username,
#             "blogs": []
#         }
#         blogs = Blog.query.filter_by(user_id=user.id).order_by(Blog.createtime.desc()).all()
#         for blog in blogs:
#             blog_dict = {
#                 "id": blog.id,
#                 "blog_user_id": blog.user_id,
#                 "title": blog.title,
#                 "text": blog.text,
#                 "createtime": blog.createtime
#             }
#             user_dict['blogs'].append(blog_dict)
#         user_blog_result.append(user_dict)
#     return jsonify(user_blog_result)


@app.route('/api/blog_user_information', methods=['GET', 'POST'])
def blog_user_information():
    blog_user_result = []
    blogs = Blog.query.order_by(Blog.createtime.desc()).all()
    for blog in blogs:
        blog_dict = {
            "id": blog.id,
            "blog_user_id": blog.user_id,
            "title": blog.title,
            "text": blog.text,
            "createtime": blog.createtime,
            "users": []
        }
        users = User.query.filter_by(id=blog.user_id).all()
        for user in users:
            user_dict = {
                "id": user.id,
                "username": user.username,
            }
            blog_dict['users'].append(user_dict)
        blog_user_result.append(blog_dict)
    return jsonify(blog_user_result)


# @app.route('/api/blog_comment_user', methods=['GET', 'POST'])
# def blog_comment_user():
#     blog_comment_user_result = []
#     blogs = Blog.query.all()
#     for blog in blogs:
#         blog_dict = {
#             "id": blog.id,
#             "blog_user_id": blog.user_id,
#             "title": blog.title,
#             "text": blog.text,
#             "createtime": blog.createtime,
#             "comments": []
#         }
#         comments = Comment.query.filter_by(blog_id=blog.id).all()
#         for comment in comments:
#             comment_dict = {
#                 "id": comment.id,
#                 "text": comment.text,
#                 "comment_user_id": comment.user_id,
#                 "blog_comment_id": comment.blog_id,
#                 "users": []
#             }
#             users = User.query.filter_by(id=comment.user_id).all()
#             for user in users:
#                 user_dict = {
#                     "id": user.id,
#                     "username": user.username
#                 }
#                 comment_dict['users'].append(user_dict)
#             blog_dict['comments'].append(comment_dict)
#         blog_comment_user_result.append(blog_dict)
#     return jsonify(blog_comment_user_result)


@app.route('/api/blog/<int:blog_id>', methods=['GET', 'POST'])
def blog_comment_user(blog_id):
    blog_comment_user_result = []
    blog = Blog.query.filter_by(id=blog_id).first()
    blog_dict = {
        "id": blog.id,
        "blog_user_id": blog.user_id,
        "title": blog.title,
        "text": blog.text,
        "createtime": blog.createtime,
        "comments": []
    }
    comments = Comment.query.filter_by(blog_id=blog.id).all()
    for comment in comments:
        comment_dict = {
            "id": comment.id,
            "text": comment.text,
            "comment_user_id": comment.user_id,
            "blog_comment_id": comment.blog_id,
            "users": []
        }

        users = User.query.filter_by(id=comment.user_id).all()
        for user in users:
            user_dict = {
                "id": user.id,
                "username": user.username
            }
            comment_dict['users'].append(user_dict)
        blog_dict['comments'].append(comment_dict)
    blog_comment_user_result.append(blog_dict)
    return jsonify(blog_comment_user_result)


@app.route('/api/user/<int:user_id>', methods=['GET', 'POST'])
def user_blog(user_id):
    user_blog_result = []
    user = User.query.filter_by(id=user_id).first()
    # for user in users:
    user_dict = {
        "id": user.id,
        "username": user.username,
        "about": user.about,
        "name": user.name,
        "blogs": []
    }
    blogs = Blog.query.filter_by(user_id=user.id).order_by(Blog.createtime.desc()).all()
    for blog in blogs:
        blog_dict = {
            "id": blog.id,
            "blog_user_id": blog.user_id,
            "title": blog.title,
            "text": blog.text,
            "createtime": blog.createtime
        }
        user_dict['blogs'].append(blog_dict)
    user_blog_result.append(user_dict)
    return jsonify(user_blog_result)


@app.route('/api/myaccount/<int:user_id>', methods=['GET', 'POST'])
def myaccount(user_id):
    myaccount_result = []
    user = User.query.filter_by(id=user_id).first()
    user_dict = {
        "name": user.name,
        "about": user.about,
        "username": user.username,
        "id": user.id,
        "blogs": []
    }
    blogs = Blog.query.filter_by(user_id=user.id).order_by(Blog.createtime.desc()).all()
    for blog in blogs:
        blog_dict = {
            "id": blog.id,
            "blog_user_id": blog.user_id,
            "title": blog.title,
            "text": blog.text,
            "createtime": blog.createtime
        }

        user_dict['blogs'].append(blog_dict)
    myaccount_result.append(user_dict)
    return jsonify(myaccount_result)


@app.route('/api/editaccount/<int:user_id>', methods=['GET', 'POST'])
def editaccount(user_id):
    name_form1 = request.form.get('name')
    about_form1 = request.form.get('about')
    user_dict2 = {
        'name': name_form1,
        'about': about_form1,
    }
    print(user_dict2)
    user = User.query.filter_by(id=user_id).first()
    if name_form1 is not None:
        user.name = name_form1
        user.about = about_form1
        db.session.commit()
        user_dict3 = {
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'about': user.about
        }
        return jsonify(success=True, message='Submit successfully', user_dict=user_dict3)
    return jsonify(success=False, message='Invalid name')


@app.route('/api/addcomment/<int:user_id>', methods=['GET', 'POST'])
def addcomment(user_id):
    print(user_id)
    comment_form = request.form.get('comment')
    blog_id_form = request.form.get('blog_id')
    print(comment_form)
    blog = Blog.query.filter_by(user_id=user_id).first()
    createtime = str(datetime.now())
    user_id = user_id
    blog_id = blog_id_form
    comment = Comment(text=comment_form, createtime=createtime, user_id=user_id, blog_id=blog_id)
    print(comment.text)
    db.session.add(comment)
    db.session.commit()
    comment_dict = {
        "text": comment.text
    }
    return jsonify(success=True, message='Submit successfully', comment=comment_dict)


@app.route('/api/editblog/<int:blog_id>', methods=['GET', 'POST'])
def editblog(blog_id):
    title_form = request.form.get('title')
    text_form = request.form.get('text')
    blog = Blog.query.filter_by(id=blog_id).first()
    if title_form and text_form is not None:
        blog.text = text_form,
        blog.title = title_form,
        db.session.commit()
        blog_dict1 = {
            'id': blog.id,
            'title': blog.title,
            'text': blog.text,
        }
        return jsonify(success=True, message='Submit successfully', blog_dict=blog_dict1)
    return jsonify(success=False, message='Invalid name')


@app.route('/api/myblogs/<int:user_id>', methods=['GET', 'POST'])
def myblogs(user_id):
    myblogs_result = []
    blogs = Blog.query.filter_by(user_id=user_id).all()
    for blog in blogs:
        blog_dict = {
            "text": blog.text,
            "title": blog.title,
            "id": blog.id
        }
        myblogs_result.append(blog_dict)
    return jsonify(myblogs_result)


@app.route('/api/mycomments/<int:user_id>', methods=['GET', 'POST'])
def mycomments(user_id):
    mycomments_result = []
    comments = Comment.query.filter_by(user_id=user_id).all()
    for comment in comments:
        comment_dict = {
            "id": comment.id,
            "text": comment.text,
            "blog_id": comment.id
        }
        mycomments_result.append(comment_dict)
    return jsonify(mycomments_result)


@app.route('/api/deleteblog/<int:blog_id>', methods=['GET', 'POST', 'DELETE'])
def deleteblog(blog_id):
    comments = Comment.query.filter_by(blog_id=blog_id).all()
    for comment in comments:
        db.session.delete(comment)
    blog = Blog.query.filter_by(id=blog_id).first()
    db.session.delete(blog)
    db.session.commit()
    return jsonify(success=True, message='Delete successfully')


@app.route('/api/deletecomment/<int:comment_id>', methods=['GET', 'POST', 'DELETE'])
def deletecomment(comment_id):
    # id_form = request.form.get('comment_id')
    comment = Comment.query.filter_by(id=comment_id).first()
    db.session.delete(comment)
    db.session.commit()
    return jsonify(success=True, message='Delete successfully')


@app.route('/api/writeblogs/<int:user_id>', methods=['GET', 'POST'])
def writeblogs(user_id):
    title_form = request.form.get('title')
    text_form = request.form.get('text')
    createtime = str(datetime.now())
    blog = Blog(text=text_form, title=title_form, user_id=user_id, createtime=createtime)
    db.session.add(blog)
    db.session.commit()
    return jsonify(success=True, message='Submit successfully')


if __name__ == '__main__':
    app.run(debug=True)
