from flask_bcrypt import Bcrypt
import sqlite3
from flask import Flask,g
from marshmallow import Schema,fields
import uuid
import mysql.connector


# db = "./data.sql"
# HOST = 'localhost'
# USER = 'root'
# PASSWORD = ''
# TABLE  = 'users'


def get_db():
    # if not hasattr(g,'sqlite.db'):
    #     conn = sqlite3.connect(db)
    #     conn.row_factory = sqlite3.Row
    #     g.sqlite_db = conn
    #sql = "CREATE TABLE IF NOT EXISTS users(id integer primary key autoincrement,email text, username text, password text, api_key text);"
    #     conn.execute(sql)
    #     conn.commit
    # return g.sqlite_db
    dbb = mysql.connector.connect(host=HOST,user=USER,password=PASSWORD,db=TABLE)

    return dbb
def close_db():
    return

def getHash(ctx,password):
    bcrypt = Bcrypt(ctx)
    return bcrypt.generate_password_hash(password)
def checkHash(ctx,name,pass_to_check):
    db = get_db()
    sql_command = "select password from users where username=%s"
    cursor = db.cursor()
    cursor.execute(sql_command,[name])
    try:
        db_pass = cursor.fetchone()[0]
        bcrypt = Bcrypt(ctx)
        return bcrypt.check_password_hash(db_pass,pass_to_check)
    except TypeError:
        return False
def getUser(id):
    db = get_db()
    sql = "select username from users where id=%s"
    cursor = db.cursor()
    cursor.execute(sql,[id])
    return cursor.fetchone()[0]

def addUser(user):
    email = user['email']
    username=user['username']
    password = user['password']
    api = generateApiKey()
    db = get_db()
    cursor = db.cursor()
    sql = "insert into users(email,username,password,api_key) values(%s,%s,%s,%s)"
    cursor.execute(sql,[email,username,password,api])
    db.commit()
def getPosts():
    db = get_db()
    posts = db.execute("select * from posts")
    postsList = []
    for p in posts.fetchall():
        u_id = p['user_id']
        author = getUser(u_id)
        postsList.append({'id':p['post_id'],'user_name':author,'content':p['post_content']})
    return postsList



def getApiKey(username):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    print(username)
    sql = f'SELECT api_key from users where username=%s'
    cursor.execute(sql,[username])
    return cursor.fetchone()['api_key']

def isKeyValid(key):
    db=get_db()
    cursor = db.cursor(dictionary=True)
    sql = 'select api_key from users where api_key=%s'
    cursor.execute(sql,[key])
    found_key = cursor.fetchone()
    # print(found_key['api_key'])
    if(found_key is None):
        return False
    else:
        if(found_key['api_key']==key):
            return True
        else:
            return False
    return False
        
def generateApiKey():
    api_key = str(uuid.uuid4())
    return api_key
class UsersSchema(Schema):
    id = fields.Integer()
    email = fields.String()
    username = fields.String()
    password = fields.String()

class PostsSchema(Schema):
    postID = fields.Integer()
    userID = fields.Integer()
    content = fields.String()