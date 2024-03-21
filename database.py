from flask_bcrypt import Bcrypt
import sqlite3
from flask import Flask,g

db = "database.db"
def get_db():
    if not hasattr(g,'sqlite.db'):
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        g.sqlite_db = conn
    return g.sqlite_db
def close_db():
    if hasattr(g,'sqlite.db'):
        g.sqlite_db.close()

def getHash(ctx,password):
    bcrypt = Bcrypt(ctx)
    return bcrypt.generate_password_hash(password)
def checkHash(ctx,name,pass_to_check):
    db = get_db()
    sql_command = "select password from users where username=?"
    cursor = db.execute(sql_command,[name])
    try:
        db_pass = cursor.fetchone()[0]
        bcrypt = Bcrypt(ctx)
        return bcrypt.check_password_hash(db_pass,pass_to_check)
    except TypeError:
        return False