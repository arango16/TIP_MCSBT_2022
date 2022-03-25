from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

ocl_pw = r'Iberia123456'
pub_ip = r"35.198.145.47"
dbname = r"Iberia_IT"
project_id = r"elated-lotus-344717"
instance_name = r"iberia-it"
db_port = "3306"

app.config["SECRET_KEY"] = "this is not secret, remember, change it!"

db_url = f"mysql+pymysql://root:{ocl_pw}@{pub_ip}:{db_port}/{dbname}" #TCP

engine = create_engine(db_url)


mo1 = 'jan'
mo2 = 'feb'
mo3 = 'mar'
mo4 = 'apr'
year = 2021


@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))
    
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
    SELECT password, userid, first_name
    FROM users
    WHERE username='{username}'
    """

    with engine.connect() as connection:
        user = connection.execute(login_query).fetchone()

        if user and check_password_hash(user[0], password):
            session["user_id"] = user[1]
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("404.html"), 404
        session["first_name"] = user[2]

@app.route("/logout")
def logout():
    session.pop("username")
    session.pop("user_id")

    return redirect(url_for("index"))

#DASHBOARD FUNCTIONS

@app.route("/dashboard")
def dashboard():
    
    if "username" in session:
        
        name_query = f"""
        SELECT first_name
        FROM users
        WHERE username='{session["username"]}'
        """
    
        with engine.connect() as connection:
            logged_in_query = connection.execute(name_query).fetchone()   
        
        logged_in = logged_in_query[0]
        
        return render_template('base.html', logged_in = logged_in)
    
    else:
        return render_template('login.html')

@app.route("/status_kpi1")
def status_kpi1():
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
        
        low = data.get('Baja')
        medium = data.get('Media')
        high = data.get('Alta')
        critical = data.get('Crítica') 
    
        return render_template('dashboard_status_kpi1.html', labels=labels, low=low, medium=medium, high=high, critical=critical)
    
    else:
        return render_template('login.html')

@app.route("/status_kpi2")
def status_kpi2():
    mo1 = 'jan'
    mo2 = 'feb'
    mo3 = 'mar'
    mo4 = 'apr'
    year = 2021
    labels = [mo1.title()+str(year), mo2.title()+str(year), mo3.title()+str(year), mo4.title()+str(year)]
    if "username" in session:  
        data = {'Tower Group':[], 'Application Tower':[], 'Server Tower':[], 'Service Ops Tower':[], 'Network Tower':[], 'Delivery':[],\
            'EUC':[], 'Equipos Multifunción':[], 'Seguridad':[], 'UNKNOW':[]}
            
        for k in data.keys():
            
            
            query_jan = f"""
            SELECT count(*)
            FROM monthly_incidents_raised_jan irj
            WHERE (Tower_Group='{k}' AND Customer_Company_Group='IBERIA')
            """
    
            query_feb = f"""
            SELECT count(*)
            FROM monthly_incidents_raised_feb irf
            WHERE (Tower_Group='{k}' AND Customer_Company_Group='IBERIA')
            """
            
            query_mar = f"""
            SELECT count(*)
            FROM monthly_incidents_raised_mar irm
            WHERE (Tower_Group='{k}' AND Customer_Company_Group='IBERIA')
            """
            
            query_apr = f"""
            SELECT count(*)
            FROM monthly_incidents_raised_apr ira
            WHERE (Tower_Group='{k}' AND Customer_Company_Group='IBERIA')
            """
            
            with engine.connect() as connection:
                jan2021 = connection.execute(query_jan).fetchone()
                feb2021 = connection.execute(query_feb).fetchone()
                mar2021 = connection.execute(query_mar).fetchone()
                apr2021 = connection.execute(query_apr).fetchone()
                
            data_list = [jan2021[0], feb2021[0], mar2021[0], apr2021[0]]
            data[k] = data_list        

            twr_grp = data.get('Tower Group')
            app_twr = data.get('Application Tower')
            serv_twr = data.get('Server Tower')
            serv_op_twr = data.get('Service Ops Tower')
            net_twr = data.get('Network Tower')
            delv = data.get('Delivery')
            euc = data.get('EUC')
            eq_mf = data.get('Equipos Multifunción')
            seg = data.get('Seguridad')
            unk = data.get('UNKNOW')  
    
        return render_template('dashboard_status_kpi2.html', labels=labels,twr_grp=twr_grp, app_twr=app_twr, serv_twr=serv_twr, \
                               serv_op_twr=serv_op_twr, net_twr=net_twr, delv=delv, euc=euc, eq_mf=eq_mf, seg=seg, unk=unk)

  
    else:
        return render_template('login.html')
    
    
    
    
    
    
    
    
@app.route("/capacity_kpis")
def capacity_kpis():
    
    #KPI 1 - Resolution Ratio

    labels = [mo1.title()+str(year), mo2.title()+str(year), mo3.title()+str(year), mo4.title()+str(year)]
    
    if "username" in session:
        months = ['jan', 'feb', 'mar', 'apr']   
        data = []
        
        # FIND TOTAL NUMBER OF CLOSED CASES
        for month in months:
            
            
            closed_query = f"""
            SELECT count(*)
            FROM monthly_incidents_closed_{month}
            WHERE Customer_Company_Group='IBERIA'
            """
    
            raised_query = f"""
            SELECT count(*)
            FROM monthly_incidents_raised_{month}
            WHERE Customer_Company_Group='IBERIA'
            """
            
            with engine.connect() as connection:
                closed_no = connection.execute(closed_query).fetchone()
                raised_no = connection.execute(raised_query).fetchone()
                
            res_ratio = round(closed_no[0] / raised_no[0], 3)
            data.append(res_ratio)
    
        return render_template('dashboard_capacity.html', labels=labels, data=data  )
  
    
    else:
        return render_template('login.html')
    

@app.route("/planning_kpis")
def planning_kpis():
    # KPI 1 - TABLE OF OLDEST INCIDENTS
    latest_month = 'apr'
    if "username" in session:
        
        open_tickets_query = f"""
        SELECT Incidenct_Code, Inc_Type, Incident_Status,  Assigned_Organization, Priority, aging_days FROM monthly_incidents_backlog_{latest_month}
        WHERE Customer_Company_Group = 'IBERIA'
        ORDER BY aging_days DESC
        LIMIT 5
        """
        
        with engine.connect() as connection:
            open_tickets = connection.execute(open_tickets_query).fetchall()
            
        
        
        return render_template('dashboard_planning.html', open_tickets=open_tickets)

# app.run(debug=True)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))