from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import cx_Oracle
import keyring
import os

app = Flask(__name__)

##ORACLE Connection
#os.environ['TNS_ADMIN'] = r'\adb'
# lib_dir = '/instantclient_21_3'
# cx_Oracle.init_oracle_client(lib_dir=lib_dir)
# #ocl_host = cx_Oracle.makedsn(r'adb.eu-frankfurt-1.oraclecloud.com', '1522', service_name=r'g0db1faf08c4cbf_db202203191726_medium.adb.oraclecloud.com')
# ocl_user = 'ADMIN'
# ocl_host = r'db202203191726_medium'
# ocl_connection = cx_Oracle.connect(ocl_user, password=ocl_pw, dsn=ocl_host)
# #ocl_connection = ocl_connection.cursor()

ocl_pw = r'Iberia123456'
pub_ip = r"35.198.145.47"
dbname = r"Iberia_IT"
project_id = r"elated-lotus-344717"
instance_name = r"iberia-it"
db_port = 3306

app.config["SECRET_KEY"] = "this is not secret, remember, change it!"
app.config["SQLALCHEMY_DATABASE_URI"]= f"mysql+mysqldb://root:{ocl_pw}@{pub_ip}/{dbname}?unix_socket=/cloudsql/{project_id}:{instance_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

db_url = f"mysql+pymysql://root:{ocl_pw}@{pub_ip}:{db_port}/{dbname}" #TCP
#db_url = r"mysql+pymysql://root:{ocl_pw}@{pub_ip}/{dbname}?unix_socket=/cloudsql/{project_id}:{instance_name}" #UNIX

engine = create_engine(db_url)

@app.route("/")
def index():
    if "username" in session:
        return render_template("base.html")
    
    else:
        return render_template("login.html")

@app.route("/register")
def register():
    return render_template("create_account.html")

@app.route("/register", methods=["POST"])
def handle_register():
    auth_code=request.form["auth_code"]
    first_name=request.form["first_name"]
    last_name=request.form["last_name"]
    email=request.form["email"]
    username=request.form["username"]
    password=request.form["password"]
    repeat_pass=request.form["repeat_pass"]
    hashed_password = generate_password_hash(password)
    
    #Check that auth_code exists in db
    check_auth_query = f"""
    SELECT * FROM users
    WHERE auth_code = '{auth_code}'
    """
    
    with engine.connect() as connection:
        auth_code_db=connection.execute(check_auth_query).fetchone()
        
    #Check if username is taken
    user_taken_query = f"""
    SELECT username FROM users
    WHERE username = '{username}'
    """    
    with engine.connect() as connection:
        user_db=connection.execute(user_taken_query).fetchone()
        
    #Check if email exists in db
    email_taken_query = f"""
    SELECT email FROM users
    WHERE email = '{email}'
    """    
    
    with engine.connect() as connection:
        email_db=connection.execute(email_taken_query).fetchone()  
    
        
    if auth_code_db is not None and email.find('@iberia.com')!=-1 and password==repeat_pass\
        and email_db is None and user_db is None:    
            insert_query = f"""
            UPDATE users SET first_name = '{first_name}', last_name = '{last_name}', email = '{email}', username = '{username}', password = '{hashed_password}'
            WHERE auth_code = '{auth_code_db[6]}'
            """
            with engine.connect() as connection:
                connection.execute(insert_query)
            
            #Delete auth_code once it is used
            delete_auth_query=f"""
            UPDATE users SET auth_code =NULL 
            WHERE auth_code={auth_code_db[6]}
            """
            with engine.connect() as connection:
                connection.execute(delete_auth_query)            
            
            return redirect(url_for("index"))
    else:
        return render_template('404.html')


# @tweeter.route("/users")
# def users():
#     if "username" in session:
#         query = f"""
#         SELECT id, username, picture
#         FROM users
#         WHERE id!={session['user_id']}
#         """
    
#         with engine.connect() as connection:
#             users = connection.execute(query)
    
#             return render_template("users.html", users=users)
#     else:
#         return render_template("404.html"), 404


# @tweeter.route("/users/<user_id>")
# def user_detail(user_id):
#     query = f"""
#     SELECT id, username, picture
#     FROM users
#     WHERE id={user_id}
#     """

#     tweets_query = f"""
#     SELECT tweet
#     FROM tweets
#     WHERE user_id={user_id}
#     """

#     with engine.connect() as connection:
#         user = connection.execute(query).fetchone()
#         tweets = connection.execute(tweets_query).fetchall()

#         if user:
#             return render_template("user_detail.html", user=user, tweets=tweets)
#         else:
#             return render_template("404.html"), 404

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def handle_login():
    username=request.form["username"]
    password=request.form["password"]

    login_query = f"""
    SELECT password, userid
    FROM users
    WHERE username='{username}'
    """

    with engine.connect() as connection:
        user = connection.execute(login_query).fetchone()

        if user and check_password_hash(user[0], password):
            session["user_id"] = user[1]
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("404.html"), 404

@app.route("/logout")
def logout():
    session.pop("username")
    session.pop("user_id")

    return redirect(url_for("index"))



app.run(debug=True)