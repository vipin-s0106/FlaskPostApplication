'''
Created on Sep 8, 2018

@author: vipin
'''
from flask import Flask,request,flash,redirect,url_for,session,logging
from flask.templating import render_template
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from DBConnectivity import DBConnectivity
from functools import wraps
from wsgiref.validate import validator


app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template("Home.html")


@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/articles')
def articles():
    connection = DBConnectivity.getConnection("localhost", "root", "0106", "myflaskapp")
    query = "SELECT * from ARTICLES"
    cur = DBConnectivity.getQueryResult(connection, query)
    result = cur.fetchall()
    if result != None:
        return render_template("articles.html",articles=result)
    else:
        msg = "No Articles"
        return render_template("articles.html",msg=msg)
    DBConnectivity.closeConnection(connection)
    

@app.route('/article/<string:id>')
def article(id):
    connection = DBConnectivity.getConnection("localhost", "root", "0106", "myflaskapp")
    query = "SELECT * from ARTICLES WHERE ID ="+id
    cur = DBConnectivity.getQueryResult(connection, query)
    result = cur.fetchone()
    if result != None:
        return render_template("article.html",article=result)
    else:
        msg = "No Articles"
        return render_template("article.html",msg=msg)
    DBConnectivity.closeConnection(connection)



class Register(Form):
    name = StringField('Name',[validators.Length(min = 1,max = 50)])
    username = StringField('UserName',[validators.Length(min = 4,max = 25)])
    email = StringField('Email',[validators.Length(min = 6 ,max = 50)])
    password = PasswordField('Password',[
        validators.DataRequired,
        validators.equal_to('confirm', "Password do not match")
        ])
    confirm = PasswordField('Confirm Password')
    
@app.route('/register',methods=['GET','POST'])
def register():
    form = Register(request.form)
    if (request.method == 'POST'):
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        
        #Write the Data into the Database
        con = DBConnectivity.getConnection("localhost", "root", "0106", "myflaskapp")
        query = "SELECT USERNAME from USERS where username = '"+username+"'"
        cursor = DBConnectivity.getQueryResult(con, query)
        result = cursor.fetchone()
        if(result == None):
            query = "INSERT INTO USERS (NAME,EMAIL,USERNAME,PASSWORD) VALUES('"+name+"','"+email+"','"+username+"','"+password+"')"
            #print(query)
            DBConnectivity.updateDatabase(con, query)
            DBConnectivity.closeConnection(con)
            
            flash("You have Successfully Registered", "success")
            
            return redirect(url_for('login'))
        else:
            flash("User has already registered", "danger")
            return redirect(url_for("register"))
        
    return render_template("register.html",form = form)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        
        con = DBConnectivity.getConnection("localhost", "root", "0106", "myflaskapp")
        query = "SELECT username,password from users where username = '"+username+"'"
        result = DBConnectivity.getQueryResult(con, query)
        result = result.fetchone()
        if result != None:
            if sha256_crypt.verify(password_candidate, result[1]):
                session['logged_in'] = True
                session['username'] = username
                flash("You are successfully logged in", "success")
                return redirect(url_for("dashboard"))
            else:
                error = "Incorrect Username/Password"
                app.logger.info("Incorrect Username/Password")
                return render_template('login.html',error=error)
        else:
            error = username+" does not exist"
            app.logger.info(username+" does not exist")
            return render_template('login.html',error=error)
        
        
        DBConnectivity.closeConnection(con)
    return render_template('login.html')
            
#check User logged in or not
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash("Unauthorized, Please Login", "danger")
            return redirect(url_for("login"))      
    return wrap

  
@app.route("/dashboard")
@is_logged_in
def dashboard():
    connection = DBConnectivity.getConnection("localhost", "root", "0106", "myflaskapp")
    query = "SELECT * from ARTICLES where author='"+session['username']+"'"
    cur = DBConnectivity.getQueryResult(connection, query)
    result = cur.fetchall()
    if result != None:
        return render_template("dashboard.html",articles=result)
    else:
        msg = "No Articles"
        return render_template("dashboard.html",msg=msg)
    DBConnectivity.closeConnection(connection)
    

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash("You are successfully Logged out","success")
    return redirect(url_for('login'))

class ArticleForm(Form):
    title = StringField('Title',[validators.Length(min = 1,max = 200)])
    body = StringField('Body')


@app.route('/add_article',methods=['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        
        #creating Connection
        connection = DBConnectivity.getConnection("localhost", "root", "0106", "myflaskapp")
        query = "INSERT INTO ARTICLES (TITLE,BODY,AUTHOR) VALUES('"+title+"','"+body+"','"+session['username']+"')"
        DBConnectivity.updateDatabase(connection, query)
        DBConnectivity.closeConnection(connection)
        flash("Article Created", "success")
        return redirect(url_for('dashboard'))
    return render_template("add_article.html",form=form)

@app.route('/delete_article/<string:id>')
@is_logged_in
def delete_article(id):
    connection = DBConnectivity.getConnection("localhost", "root", "0106", "myflaskapp")
    query = "DELETE from ARTICLES WHERE ID ="+id
    DBConnectivity.updateDatabase(connection, query)
    DBConnectivity.closeConnection(connection)
    
    flash("Article ID "+str(id)+" Sucessfully Deleted","success")
    return redirect(url_for('dashboard'))

@app.route('/edit_article/<string:id>',methods=['GET','POST'])
@is_logged_in
def edit_article(id):
    connection = DBConnectivity.getConnection("localhost", "root", "0106", "myflaskapp")
    query = "SELECT * from ARTICLES WHERE ID ="+id
    cur = DBConnectivity.getQueryResult(connection, query)
    result = cur.fetchone()
    form = ArticleForm(request.form)
    
    form.title.data = result[1]
    form.body.data = result[3]
    if request.method == 'POST' and form.validate():
        title1 = form.title.data
        body1 = form.body.data
        query = "UPDATE ARTICLES SET TITLE='"+title1+"',BODY='"+body1+"' WHERE ID ="+id
        print(query)
        DBConnectivity.updateDatabase(connection, query)
        
        flash("Article ID "+str(id)+" Updated","success")
        return redirect(url_for("dashboard"))
    return render_template("edit_article.html",form=form)
        
    DBConnectivity.closeConnection(connection)
if(__name__ == "__main__"):
    app.secret_key = 'secret123'
    app.run(debug=True)