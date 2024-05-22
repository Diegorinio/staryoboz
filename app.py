from flask import Flask, render_template,request,jsonify
import database
app = Flask(__name__,template_folder='templates')
import uuid
@app.route('/')
def index():
    api_key = str(uuid.uuid4())
    print(api_key)
    return render_template('index.html',msg="")


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


@app.route('/instruction')
def instruction():
    return render_template('instruction.html')

@app.route('/api/users',methods=['GET','POST'])
def api():
        api_key = request.headers.get('x-api-key')
        print(api_key)
        if not api_key:
            api_key = request.args.get('api_key')
            print(api_key)
        # database.checkIfKeyExists(api_key)
        response_data = {
            "success":True,
            "data":[]
        }
        if request.method=='GET':
            sql = "select * from users"
            db = database.get_db()
            cursor = db.execute(sql)
            users = cursor.fetchall()
            schema = database.UsersSchema(many=True)
            if users is not None:
                response_data["data"]=schema.dump(users)
                return jsonify(response_data)
            else:
                return notFound()
        elif request.method=='POST':
            data = request.json
            if checkData(data):
                pohaszowaniu = str(database.getHash(app,data['password']))[2:-1]
                print(type(pohaszowaniu))
                data['password'] = pohaszowaniu
                response_data['data']=data
                response = jsonify(response_data)
                response.status_code = 201
                database.addUser(data)
                return response
            else:
                response_data['success']=False
                response_data['data']="Cannot add empty field"
                return response_data


def checkData(data):
    if data['email']=='' or data['username']=='' or data['password']=='':
        return False
    else:
        return True


@app.route('/api/users/<string:input>',methods=['GET','DELETE','PUT'])
def findUser(input):
        typ = ""
        if input.isdigit():
                typ="id"
        else:
            if isEmail(input):
                typ="email"
            else:
                typ="username"
        if request.method=='GET':
            sql= f'select * from users where {typ}=?'
            db = database.get_db()
            cursor = db.execute(sql,[input])
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
            "success":True,
            "data":[]
            }
            try:
                sql = f'delete from users where {typ}=?'
                db =  database.get_db()
                db.execute(sql,[input])
                db.commit()
                return response_data
            except:
                notFound()
        elif request.method=='PUT':
            response_data = {
            "success":True,
            "data":[]
            }
            data = request.json
            sql = f'select * from users where {typ}=?'
            db = database.get_db()
            db_res_cursor = db.execute(sql,input)
            dane = {}
            row = db_res_cursor.fetchone()
            dane = {'id':row['id'],'username':row['username'],'email':row['email'],'password':row['password']}
            print( dane)
            if 'username' in data or 'email' in data or 'password' in data and checkData(data):
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
            print(dane)
            try:
                sql2 = f'UPDATE users SET username=?,email=?,password=? where {typ}=?'
                db.execute(sql2,(dane['username'],dane['email'],dane['password'],input))
                db.commit()
                db.close()
                response_data['data']="Updated"
            except Exception as error:
                response_data['data']=str(error)
            return response_data



def saveToDatabase(req):
    email = req['email']
    login=req['login']
    password = req['password']
    api = database.generateApiKey()
    if email!='' and login!='' and password!='':
        try:
            hash_pass = database.getHash(app,password)
            db = database.get_db()
            sql_command = "insert into users(email,username,password, api_key) values(?,?,?,?)"
            db.execute(sql_command,[email,login,hash_pass,api])
            db.commit()
            db.close()
            return True
        except:
            return False
    else:
        return False
def readFromDatabase(req):
    login = req['login']
    password = req['password']
    return database.checkHash(app,login,password)

def notFound():
    return jsonify(
        {"success":False,
        "data":"Data not found"
        }),404

def isEmail(data):
    if '@' in data:
        return True
    else:
        return False