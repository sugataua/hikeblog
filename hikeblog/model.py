# http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#a-minimal-application
# http://flask.pocoo.org/docs/0.12/patterns/sqlalchemy/
# http://docs.sqlalchemy.org/en/latest/core/type_basics.html#generic-types
# http://lucumr.pocoo.org/2011/7/19/sqlachemy-and-you/

from datetime import datetime

from hikeblog import app
from hikeblog import db


tags = db.Table('tags_posts',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                db.Column('post_id', db.Integer, db.ForeignKey('post.id')))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    views = db.Column(db.Integer)
    
    pub_date = db.Column(db.DateTime)
    last_update = db.Column(db.DateTime)
    
    deleted = db.Column(db.Boolean)
    
    tags = db.relationship('Tag', secondary=tags,
                           backref=db.backref('posts', lazy='dynamic'))
    
    def __init__(self):
        self.pub_date = datetime.now()
        self.last_update = self.pub_date
        self.deleted = False
        self.views = 0

    def __repr__(self):
        return '<Post %r>' % self.title
        

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(128))
    author_email = db.Column(db.String(254))
    message = db.Column(db.Text)
    
    pub_date = db.Column(db.DateTime)
    
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post',
                           backref=db.backref('comments', lazy='dynamic'))
    
    def __init__(self):
        self.pub_date = datetime.now()
        
    def __repr__(self):
        return '<Comment to %r post>' % self.post_id


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    def __repr__(self):
        return '<Tag %r>' % self.name    