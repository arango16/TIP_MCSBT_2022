
from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
import cx_Oracle
import os
import socket

app = Flask(__name__)

os.environ['TNS_ADMIN'] = r'/adb'
# lib_dir = '/instantclient_21_3'
# cx_Oracle.init_oracle_client(lib_dir=lib_dir)



# ocl_user = 'ADMIN'
ocl_pw = r'Iberia123456'
# ocl_host = r'db202203191726_medium'

pub_ip = r"adb.eu-frankfurt-1.oraclecloud.com"
dbname = r"db202203191726_medium"
project_id = r"elated-lotus-344717"
instance_name = r"iberia-it"
db_port = 1552

# ocl_host = cx_Oracle.makedsn(pub_ip, db_port, sid=dbname)
# ocl_connection = cx_Oracle.connect(ocl_user, password=ocl_pw, dsn=ocl_host)
# #ocl_connection = ocl_connection.cursor()

# app.config["SECRET_KEY"] = "this is not secret, remember, change it!"
# app.config["SQLALCHEMY_DATABASE_URI"]= f"mysql+mysqldb://root:{ocl_pw}@{pub_ip}/{dbname}?unix_socket =/cloudsql/{project_id}:{instance_name}"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True


tnsnames = r'(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-frankfurt-1.oraclecloud.com))(connect_data=(service_name=g0db1faf08c4cbf_db202203191726_medium.adb.oraclecloud.com))(security=(ssl_server_cert_dn="CN=adwc.eucom-central-1.oraclecloud.com, OU=Oracle BMCS FRANKFURT, O=Oracle Corporation, L=Redwood City, ST=California, C=US")))'

#db_url = f"oracle+cx_oracle://root:{ocl_pw}@{ocl_host}?encoding=UTF-8&nencoding=UTF-8&mode=SYSDBA&events=true" #other
#db_url = f"oracle+cx_oracle://root:{ocl_pw}@{pub_ip}:{db_port}/{dbname}" #TCP
#db_url = r"mysql+pymysql://root:{ocl_pw}@{pub_ip}/{dbname}?unix_socket=/cloudsql/{project_id}:{instance_name}" #UNIX
#db = SQLAlchemy(app)

cx_Oracle.init_oracle_client(lib_dir=r'C:\Yo\Masters\MCSBT\TIP\instantclient_21_3\',config_dir=r\'C:\Yo\Masters\MCSBT\TIP\instantclient_21_3\network\admin\')
connection = cx_Oracle.connect("tip", "Iberia123456", "db202203191726_low")

cursor = connection.cursor()
cursor.execute(""" select * from dual """)






# engine = create_engine(db_url)

# @app.route("/")
# def index():

      
#     test_query2 = f"""SELECT id FROM users"""   
    
#     with engine.connect() as connection:
#         test_final = connection.execute(test_query2).fetchone()
        
#     return render_template("test.html", test_final=test_final)
        
    
        
    


# app.run(debug=True)