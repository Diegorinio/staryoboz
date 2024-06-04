from flask import Flask, render_template,request,jsonify
import database
app = Flask(__name__,template_folder='templates')

# Dekorator sprawdzający czy został wprowadzony prawidłowy klucz api
def requireApiKey(f):
    def decorator(*args,**kwargs):
        api_key = request.headers.get('X-api-key')
        if not api_key:
            api_key=request.args.get('api_key')
        valid = database.isKeyValid(api_key)
        if valid:
            return f(*args,**kwargs)
        else:
            resposnse = jsonify({"message":"Invalid or missing API key"})
            return resposnse
    return decorator

@app.route('/')
def index():
    return render_template('index.html',msg="")


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        return saveToDatabase(request.form)
    elif request.method=='GET':
        return render_template('register.html',msg='')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        if isLoginCorrect(request.form):
            apiKey = database.getApiKey(request.form['username'])
            welcomeMessage = "Witaj "+request.form['username']+"\ntwój klucz api: "+apiKey
            return render_template('index.html',msg=welcomeMessage)
        else:
            return render_template('login.html',msg="Nieprawidłowa nazwa użytkownika lub hasło")
    elif request.method=='GET':
        return render_template('login.html')
    
if __name__ =='__main__':
    # app.run(debug=True)
    app.run()


@app.route('/instruction')
@app.route('/api/')
def instruction():
    return render_template('instruction.html')

# Routing api do wyświetlenia oraz wprowadzania użytkowników
@app.route('/api/users',methods=['GET','POST'])
@requireApiKey
def api():
        response_data = {
            "success":True,
            "data":[]
        }
        if request.method=='GET':
            sql = "select * from users"
            db = database.get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute(sql)
            users = cursor.fetchall()
            schema = database.UsersSchema(many=True)
            if users is not None:
                response_data["data"]=schema.dump(users)
                return jsonify(response_data)
            else:
                return notFound()
        elif request.method=='POST':
            data = request.json
            if isDataNotEmpty(data):
                pohaszowaniu = str(database.getHash(app,data['password']))[2:-1]
                data['password'] = pohaszowaniu
                response_data['data']=data
                response = jsonify(response_data)
                response.status_code = 201
                database.insertUserToDB(data)
                return response
            else:
                response_data['success']=False
                response_data['data']="Cannot add empty field"
                return response_data


# Funkcja sprawdzająca czy podany email, nazwa uzytkownika lub haslo nie jest puste 
def isDataNotEmpty(data):
    if data['email']=='' or data['username']=='' or data['password']=='':
        return False
    else:
        return True


@app.route('/api/users/',methods=['GET','DELETE','PUT'])
def findUser():
        input = request.args.get('query')
        api_key = request.headers.get('X-api-key')
        if not api_key:
            api_key = request.args.get('api_key')
        if database.isKeyValid(api_key):
            typ = ""
            if input.isdigit():
                    typ="id"
            else:
                if isEmailValid(input):
                    typ="email"
                else:
                    typ="username"
            if request.method=='GET':
                sql= f'select * from users where {typ}=%s'
                db = database.get_db()
                cursor = db.cursor(dictionary=True)
                cursor.execute(sql,[input])
                users = cursor.fetchone()
                if users is not None:
                    schema = database.UsersSchema()
                    return jsonify(
                        {"success":True,
                        "data":schema.dump(users)
                        }),200
                else:
                    return notFound()
            elif request.method=='DELETE':
                response_data = {
                "success":True,"status":'Record delete'
                }
                try:
                    sql = f'delete from users where {typ}=%s'
                    db =  database.get_db()
                    cursor = db.cursor()
                    cursor.execute(sql,[input])
                    if(cursor.rowcount<=0):
                        response_data = {"success":False,"status":"No row affected"}
                        return response_data
                    else:
                        db.commit()
                        response_data['status']=f'{cursor.rowcount} rows affected'
                        return response_data
                except:
                    notFound()
            elif request.method=='PUT':
                response_data = {
                "success":True,
                "data":[]
                }
                data = request.json
                sql = f'select * from users where {typ}=%s'
                db = database.get_db()
                cursor = db.cursor(dictionary=True)
                cursor.execute(sql,[input])
                dane = {}
                row = cursor.fetchone()
                dane = {'id':row['id'],'username':row['username'],'email':row['email'],'password':row['password'],'api_key':row['api_key']}
                if 'username' in data or 'email' in data or 'password' in data and isDataNotEmpty(data):
                    if 'username' in data:
                        dane['username']=data['username']
                    if 'email' in data:
                        dane['email']=data['email']
                    if 'password' in data:
                        dane['password']=str(database.getHash(app,data['password']))[2:-1]
                else:
                    response_data['success']=False
                    response_data['data']="No arguments provided"
                    return response_data
                try:
                    sql2 = f'UPDATE users SET username=%s,email=%s,password=%s,api_key=%s where {typ}=%s'
                    cursor = db.cursor()
                    cursor.execute(sql2,[dane['username'],dane['email'],dane['password'],dane['api_key'],input])
                    db.commit()
                    db.close()
                    response_data['data']="Updated"
                except Exception as error:
                    response_data['data']=str(error)
                    response_data['success']=False
                return response_data
        else:
            response = jsonify({'message':'Invalid or missing API key'})
            return response


# GŁówna funkcja do zapisywania użytkownika w bazie danych
# Funkcja jako argument przyjmuje dane z formularza
# Funkcja sprawddza czy dane nie są puste, następnie sprawdza czy dane nie są już w bazie
# Jeżeli dane nie są w bazie zostaje wygenerowany klucz api, hasło zostaje przekształcona na hash a na końcu dane są zapisane do bazy danych
def saveToDatabase(req):
    email=req['email']
    login=req['username']
    password=req['password']
    if email!='' and login!='' and password!='':
        try:
            state = database.isUserExists(req)
            if not state['status']:
                api = database.generateApiKey()
                hash_pass = database.getHash(app,password)
                db = database.get_db()
                sql_command = "insert into users(email,username,password, api_key) values(%s,%s,%s,%s)"
                cursor = db.cursor()
                cursor.execute(sql_command,[email,login,hash_pass,api])
                db.commit()
                return render_template('register.html', msg="Założono konto")
            else:
                return render_template('register.html',msg=state['msg'])
        except:
            return render_template('register.html', msg="Coś poszło nie tak")
    else:
        return render_template('register.html', msg="Uzupełnij dane formularza")


# Funkcja do logowania sprawdzająca czy dany użytkownik istnieje
def isLoginCorrect(req):
    login = req['username']
    password = req['password']
    return database.checkHash(app,login,password)

# Funkcja zwracająca brak danych
def notFound():
    return jsonify(
        {"success":False,
        "data":"Data not found"
        }),404
    
# Funkcja sprawdzająca czy adres email jest prawidłowy przez sprawdzenie czy w ciągu znajduje się znak @
def isEmailValid(data):
    if '@' in data:
        return True
    else:
        return False