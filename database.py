from flask_bcrypt import Bcrypt
import sqlite3
from flask import Flask,g
from marshmallow import Schema,fields
import uuid
import mysql.connector

HOST = 'localhost'
USER = 'root'
PASSWORD = ''
TABLE  = 'users'

# Funkcja zwracająca połączenie z bazą danych
def get_db():
    dbb = mysql.connector.connect(host=HOST,user=USER,password=PASSWORD,db=TABLE)
    return dbb

# Funkcja zwracająca hasło po przekształceniu przez algorytm hashowania
# Funkcja przyjmuje instancje aplikacji oraz ciąg znaków( hasło ) jako argument
def getHash(ctx,password):
    bcrypt = Bcrypt(ctx)
    return bcrypt.generate_password_hash(password)

# Funkcja sprawdzająca czy podane hasło jest równoznacze z hashem przypisanym do użytkownika w bazie danych
# Funkcja jako argument przyjmuje instancje aplikacji, nazwe uzytkownika oraz podane hasło do sprawdzenia
def checkHash(ctx,name,pass_to_check):
    db = get_db()
    sql_command = "select password from users where username=%s"
    cursor = db.cursor()
    cursor.execute(sql_command,[name])
    try:
        db_pass = cursor.fetchone()[0]
        bcrypt = Bcrypt(ctx)
        # Sprawdzenie czy po odkształceniu hashu z bazy ciąg jest taki sam jak podany w argumencie
        return bcrypt.check_password_hash(db_pass,pass_to_check)
    except TypeError:
        return False

# Funkcja zwracająca dane użytkownika na podstawie jego id w bazie danych
def getUser(id):
    db = get_db()
    sql = "select username from users where id=%s"
    cursor = db.cursor()
    cursor.execute(sql,[id])
    return cursor.fetchone()[0]

# Funkcja wprowadzająca dane do bazy danych
def insertUserToDB(user):
    email = user['email']
    username=user['username']
    password = user['password']
    api = generateApiKey()
    db = get_db()
    cursor = db.cursor()
    sql = "insert into users(email,username,password,api_key) values(%s,%s,%s,%s)"
    cursor.execute(sql,[email,username,password,api])
    db.commit()

# Funkcja zwracająca api_key z bazy danych dla danego użytkownika
def getApiKey(username):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    sql = f'SELECT api_key from users where username=%s'
    cursor.execute(sql,[username])
    return cursor.fetchone()['api_key']

# Funkcja sprawddzająca czy dany użytkownik o danej nazwie lub emailu jest już w bazie
def isUserExists(user):
    sql = "select * from users where username=%s or email=%s"
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(sql,(user['username'],user['email']))
    ans = cursor.fetchall()
    res= {"msg":'',"status":False}
    if len(ans)>0:
        for x in ans:
            if x['username']==user['username']:
                res['msg']="Nazwa użytownika jest już zajęta"
                res['status']=True
                return res
            if x['email']==user['email']:
                res['msg']="Adres email jest już w użyciu"
                res['status']=True
                return res
    return res

# Funkcja sprawdzająca czy podany klucz api znajduje się w bazie
def isKeyValid(key):
    db=get_db()
    cursor = db.cursor(dictionary=True)
    sql = 'select api_key from users where api_key=%s'
    cursor.execute(sql,[key])
    found_key = cursor.fetchone()
    if(found_key is None):
        return False
    else:
        if(found_key['api_key']==key):
            return True
        else:
            return False

# Funkcja generująca i zwracająca klucz api
def generateApiKey():
    api_key = str(uuid.uuid4())
    return api_key

class UsersSchema(Schema):
    id = fields.Integer()
    email = fields.String()
    username = fields.String()
    password = fields.String()