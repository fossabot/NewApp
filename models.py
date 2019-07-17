import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app import bcrypt, db, db_engine,ma,fields
import flask_whooshalchemy

Base = declarative_base()


class UserModel(db.Model):

    __tablename__ = 'users'


    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key = True, index=True)
    join_date = db.Column(db.Date, primary_key = False, default = datetime.datetime.now)
    name = db.Column(db.String(50), primary_key = False)
    real_name = db.Column(db.String(50), primary_key = False)
    github_name = db.Column(db.String(50), primary_key = False)
    email = db.Column(db.String(50), primary_key = False)
    password = db.Column(db.String(255), primary_key = False)
    avatar = db.Column(db.String, primary_key = False, default = 'None')
    genre = db.Column(db.String, primary_key = False, default = 'None')
    role = db.Column(db.Integer, ForeignKey('roles.id') ,default = 0)
    bio = db.Column(db.String(250), primary_key = False, default = 'Hey i`m new here')
    activated = db.Column(db.Boolean, primary_key=False)

    posts = relationship("PostModel", backref="user_in")
    replyes = relationship("ReplyModel", backref="user_in")
    likes = relationship("LikeModel", backref="user_in")

    def __init__(self,id,join_date,name,real_name,github_name,email,password,avatar,genre,role,bio,activated):
        self.id = id
        self.join_date = join_date
        self.name = name
        self.real_name = real_name
        self.github_name = github_name
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.avatar = avatar
        self.genre = genre
        self.role = role
        self.bio = bio
        self.activated = activated

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return ('<name {}').format(self.name)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','join_date','name','real_name','github_name','email','avatar')
    
UsersSchema = UserSchema(many=True)

class OUserSchema(ma.Schema):
    class Meta:
        fields = ('id','join_date','name','real_name','github_name','email','genre','role','bio','avatar')
    
OUserSchema = OUserSchema()

class RoleModel(db.Model):

    __tablename__ = 'roles'


    id = db.Column(db.Integer, db.Sequence('role_id_seq'), primary_key = True)
    name = db.Column(db.String(30), primary_key = False)

    user = relationship("UserModel", backref="roleinfo")

    def __init__(self,id,name):
        self.id = id
        self.name = name

    def __repr__(self):
        return ('<name {}').format(self.name)

class PostModel(db.Model):

    __tablename__ = 'posts'

    __searchable__ = ['title']

    id = db.Column(db.Integer, db.Sequence('posts_id_seq'), primary_key = True)
    title = db.Column(db.String(100), primary_key = False)
    text = db.Column(db.String, primary_key = False)
    views = db.Column(db.Integer, primary_key = False, default=0)
    reply = db.Column(db.Integer, primary_key = False, default=0)
    user = db.Column(db.Integer, ForeignKey('users.id')) 
    posted_on = db.Column(db.Date, primary_key = False, default = datetime.datetime.now)
    approved = db.Column(db.Boolean, primary_key = False)
    closed = db.Column(db.Boolean, primary_key = False)
    closed_on = db.Column(db.Date, primary_key = False)
    closed_by = db.Column(db.Integer, primary_key = False)
    
    author = db.relationship("UserModel", backref = "author")

    def __init__(self,id,title,text,views,reply,user,posted_on,approved,closed,closed_on,closed_by):
        self.id = id
        self.title = title
        self.text = text
        self.views = views
        self.reply = reply
        self.user = user
        self.posted_on = posted_on
        self.approved = approved
        self.closed = closed
        self.closed_on = closed_on
        self.closed_by = closed_by

    def __repr__(self):
        return '{0}(title={1})'.format(self.__class__.__name__, self.title)

    def replies(self):
        return db.session.query(ReplyModel).filter_by(post_id=self.id).count()

    def closed_by_name(self):
        users = UserModel.query.filter_by(id=self.closed_by).first()
        return users.name

class PostSchema(ma.Schema):
    author = fields.Nested(UserSchema())
    class Meta:
        fields = ('id','title','text','views','posted_on','author')
    
PostsSchema = PostSchema(many=True)
OPostSchema = PostSchema()

class ReplyModel(db.Model):

    __tablename__ = 'replyes'
 
    id = db.Column(db.Integer, db.Sequence('replyes_id_seq'), primary_key = True)
    text = db.Column(db.String(250), primary_key = False)
    post_id = db.Column(db.Integer, primary_key = False)
    user = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self,id,text,post_id,user):
        self.id = id
        self.text = text
        self.post_id = post_id
        self.user = user

    def __repr__(self):
        return ('<id {}').format(self.id)

class ReplySchema(ma.Schema):
    class Meta:
        fields = ('id','text','post_id','user')
    
RepliesSchema = ReplySchema(many=True)

class LikeModel(db.Model):

    __tablename__ = 'likes'


    id = db.Column(db.Integer, db.Sequence('likes_id_seq'), primary_key = True)
    post_id = db.Column(db.Integer, primary_key = False)
    user = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self,id,post_id,user):
        self.id = id
        self.post_id = post_id
        self.user = user

    def __repr__(self):
        return ('<id {}').format(self.id)

class TagModel(db.Model):

    __tablename__ = 'post_tags'

 
    id = db.Column(db.Integer, db.Sequence('post_tags_id_seq'), primary_key = True)
    tag = db.Column(db.String(50), primary_key = False)
    post_id = db.Column(db.Integer, primary_key = False)

    def __init__(self,id,tag,post_id):
        self.id = id
        self.tag = tag
        self.post_id = post_id


class Gits:

    def __init__(self,name,link,desc):
        self.name = name
        self.link = link
        self.desc = desc

Base.metadata.create_all(db_engine, Base.metadata.tables.values(),checkfirst=True)
