from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

ocl_pw = r'Iberia123456'
pub_ip = r"35.198.145.47"
dbname = r"Iberia_IT"
project_id = r"elated-lotus-344717"
instance_name = r"iberia-it"
db_port = 3306

app.config["SECRET_KEY"] = "this is not secret, remember, change it!"

db_url = f"mysql+pymysql://root:{ocl_pw}@{pub_ip}:{db_port}/{dbname}" #TCP

engine = create_engine(db_url)



@app.route("/")
def index():
    if "username" in session:
        return render_template("base.html")
    
    else:
        return render_template("login.html")

#REGISTRATION FUNCTIONS

@app.route("/register")
def register():
    return render_template("create_account.html")

@app.route("/register", methods=["POST"])
def handle_register():
    auth_code=request.form["auth_code"]
    first_name=request.form["first_name"]
    last_name=request.form["last_name"]
    email=request.form["email"].lower()
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
    
    #CRITERIA TO BE REGISTERED:
        #There must be an available auth_code in db
        #Email cannot already exist
        #Username cannot already exist
        #Password equals repeated password
    
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
 
#LOGIN FUNCTIONS

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

#DASHBOARD FUNCTIONS

@app.route("/dashboard")
def dashboard():
    return render_template('base.html')

@app.route("/status_kpis")
def status_kpis():
    #KPI 1 - Line Chart Priority
    mo1 = 'jan'
    mo2 = 'feb'
    mo3 = 'mar'
    mo4 = 'apr'
    year = 2021
    labels = [mo1.title()+str(year), mo2.title()+str(year), mo3.title()+str(year), mo4.title()+str(year)]
    
    if "username" in session:
        
        data = {'Baja':[], 'Media':[], 'Alta':[], 'Crítica':[]}
        
        for k in data.keys():
            
            
            query_jan = f"""
            SELECT count(*)
            FROM monthly_incidents_raised_jan irj
            WHERE (priority='{k}' AND Customer_Company_Group='IBERIA')
            """
    
            query_feb = f"""
            SELECT count(*)
            FROM monthly_incidents_raised_feb irf
            WHERE (priority='{k}' AND Customer_Company_Group='IBERIA')
            """
            
            query_mar = f"""
            SELECT count(*)
            FROM monthly_incidents_raised_mar irm
            WHERE (priority='{k}' AND Customer_Company_Group='IBERIA')
            """
            
            query_apr = f"""
            SELECT count(*)
            FROM monthly_incidents_raised_apr ira
            WHERE (priority='{k}' AND Customer_Company_Group='IBERIA')
            """
            
            with engine.connect() as connection:
                jan2021 = connection.execute(query_jan).fetchone()
                feb2021 = connection.execute(query_feb).fetchone()
                mar2021 = connection.execute(query_mar).fetchone()
                apr2021 = connection.execute(query_apr).fetchone()
                
            data_list = [jan2021[0], feb2021[0], mar2021[0], apr2021[0]]
            data[k] = data_list        
        
        labels=labels
        low = data.get('Baja')
        medium = data.get('Media')
        high = data.get('Alta')
        critical = data.get('Crítica') 
        
        return render_template('test_chart.html', labels=labels, low=low, medium=medium, high=high, critical=critical)
    
    else:
        return render_template('login.html')

@app.route("/capacity_kpis")
def capacity_kpis():
    return render_template('test_chart.html')

@app.route("/planning_kpis")
def planning_kpis():
    return render_template('dashboard_planning.html')

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





app.run(debug=True)