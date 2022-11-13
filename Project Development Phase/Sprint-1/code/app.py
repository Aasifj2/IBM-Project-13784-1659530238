from flask import Flask, render_template, request, flash, redirect,url_for
import ibm_db


app = Flask(__name__)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=dzl38201;PWD=tWhkzDv86rhbXxTI",'','')

from flask_mail import Mail, Message


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'baap11102@gmail.com'
app.config['MAIL_PASSWORD'] = 'ybitwysenwtloxym'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)




@app.route('/')
def main():
    return render_template('index.html')


@app.route('/register_page', methods=['GET', 'POST'])
def register():
    return render_template('register.html')
    

@app.route('/login_page', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not username:
            flash('FullName is required!')
        elif not password:
            flash('Password is required!')
        elif not email:
            flash('Email is required!')
        
        
        print('user account created successfully!')
        send_verification_mail(username,email,password)
        return render_template('verify.html', email=email)
        



@app.route("/login_user",methods=['GET','POST'])
def login_user():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']

    if not email or not password:
        return render_template('login.html')
    query = "SELECT * FROM USERS WHERE email=?"
    stmt = ibm_db.prepare(conn, query)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    isUser = ibm_db.fetch_assoc(stmt)
    print(isUser,password)

    if not isUser:
      return render_template('message.html',message = 'No account associated with that email')
    if(isUser['PASSWORD']==password):
        if str(isUser['VERIFIED']) == '1':
            return render_template('upload_image.html')
        else:
            return render_template('verify.html', email = email)
    else:
        return render_template('message.html',message = ' Invalid Passowrd!')
    
  return redirect('/login_page')



def send_verification_mail(username,email,password):
    msg = Message('Hello !, ' + username , sender =   'baap11102@gmail.com', recipients = [email])
    from random import randint
    code = randint(10**3,(10**4)-1)
    msg.body = "Hey,"+username+" Your verification number is  "+ str(code)
    mail.send(msg)

    insert_sql = "INSERT INTO USERS VALUES (?,?,?,?,?);"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, username)
    ibm_db.bind_param(prep_stmt, 2, email)
    ibm_db.bind_param(prep_stmt, 3, password)
    ibm_db.bind_param(prep_stmt, 4, code)
    ibm_db.bind_param(prep_stmt, 5, '0')
    ibm_db.execute(prep_stmt)
    
    return "Message sent!"


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        code = request.form['code']
        email = request.form['email']
        
        query = "SELECT * FROM USERS WHERE email=?"

        stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        isUser = ibm_db.fetch_assoc(stmt)
        print(isUser)
        if not isUser:
            return render_template('index.html')
        if(str(isUser['CODE'])==str(code)):
            
            print('CODES ---> ',str(isUser['CODE']), str(code))
            update_query = "UPDATE USERS SET VERIFIED=\'1\' WHERE email= \'"+email+"\';"
            update_stmt = ibm_db.prepare(conn, update_query)
            print(update_query)
            print(update_stmt)
            ibm_db.execute(update_stmt)
            return render_template('message.html',message='Congratulations! Account Verified')
        else:
            return render_template('message.html', message='Sorry! The verification code is invalid!')

