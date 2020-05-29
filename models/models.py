from datetime import datetime
from SKI.database import db

class Logindate(db.Model):
    __tablename__= 'logindate'
    id = db.Column(db.Integer,primary_key=True)
    logindate = db.Column(db.DateTime, nullable=False)
    signin_id = db.Column(db.Integer, db.ForeignKey('signin.id'), nullable=False)
    signin = db.relationship('Signin', back_populates='logindate')

class Signin(db.Model):
    __tablename__ = 'signin'
    id = db.Column(db.Integer,primary_key=True)
    uname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(1), nullable=False)
    users = db.relationship("User", back_populates="signin")
    logindate = db.relationship("Logindate", back_populates="signin")


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    major = db.Column(db.String(255), nullable=False)
    avator = db.Column(db.String(255), nullable=False)
    signin_id = db.Column(db.Integer, db.ForeignKey('signin.id'), nullable=False)
    signin = db.relationship('Signin', back_populates='users')
    problems = db.relationship('Problem', back_populates='users')
    ideas = db.relationship('Idea', back_populates='users')
    comments = db.relationship('Comment', back_populates='users')

class Problem(db.Model):
    __tablename__ = 'problems'
    id = db.Column(db.Integer,primary_key=True)
    p_title = db.Column(db.String(255), nullable=False)
    p_main =  db.Column(db.String(3000), nullable=False)
    u_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    users = db.relationship('User', back_populates='problems')
    ideas = db.relationship('Idea', back_populates='problems')
    comments = db.relationship('Comment', back_populates='problems')

class Idea(db.Model):
    __tablename__ = 'ideas'
    id = db.Column(db.Integer,primary_key=True)
    idea = db.Column(db.String(3000), nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    u_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    problems = db.relationship('Problem', back_populates='ideas')
    users = db.relationship('User', back_populates='ideas')
    comments = db.relationship('Comment', back_populates='ideas')

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key=True)
    comment = db.Column(db.String(3000), nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    u_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    i_id = db.Column(db.Integer, db.ForeignKey('ideas.id'), nullable=False)
    problems = db.relationship('Problem', back_populates='comments')
    users = db.relationship('User', back_populates='comments')
    ideas = db.relationship('Idea', back_populates='comments')
