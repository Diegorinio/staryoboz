from flask import Flask, render_template, url_for,request
import database
app = Flask(__name__,template_folder='Templates')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        print(request.form)
        if saveToDatabase(request.form):
            return render_template('register.html',msg="Zalozono konto")
        else:
            return render_template('register.html',msg="Cos poszlo nie tak")
    elif request.method=='GET':
        return render_template('register.html',msg="")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        print(request.form)
        if readFromDatabase(request.form):
            return render_template('index.html',msg="Zalogowano")
        else:
            return render_template('login.html',msg="Nieprawodłowa nazwa użytkownika lub hasło")
    elif request.method=='GET':
        return render_template('login.html')
if __name__ =='__main__':
    app.run(debug=True)
    
def saveToDatabase(req):
    email = req['email']
    login=req['login']
    password = req['password']
    hash_pass = database.getHash(app,password)
    db = database.get_db()
    sql_command = "insert into users(email,username,password) values(?,?,?)"
    try:
        db.execute(sql_command,[email,login,hash_pass])
        db.commit()
        database.close_db()
        return True
    except:
        return False
def readFromDatabase(req):
    login = req['login']
    password = req['password']
    return database.checkHash(app,login,password)
    