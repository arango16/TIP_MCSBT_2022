from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import csv

name = 'Monthly_Incidents_Raised_CONSOLIDATED.csv'
table = 'monthly_incidents_raised_consolidated'


def upload_csv(name, table):
    ocl_pw = r'Iberia123456'
    pub_ip = r"35.198.145.47"
    dbname = r"Iberia_IT"
    project_id = r"elated-lotus-344717"
    instance_name = r"iberia-it"
    db_port = 3306
    
    
    db_url = f"mysql+pymysql://root:{ocl_pw}@{pub_ip}:{db_port}/{dbname}" #TCP
    
    engine = create_engine(db_url)

    file = open('csv/consolidated-final/'+f'{name}', mode='r', encoding="utf8")
    csvreader = csv.reader(file)
    csvreader = csv.reader(file)
    header = next(csvreader)
    rows = []
    for row in csvreader:
        rows.append(row)
    file.close()
    
    header = "','".join(header)
    header = header.replace("'", "")
    header = header.replace(" ", "_")
    header = header.replace(",", ", ")
    header = header.replace("-","")
    header = header.replace("(","")
    header = header.replace(")","")
    header = header.replace(".","")
    header = header[1:]   
    
    n=0
    
    for line in rows:
    
        if n <= len(rows):
            
        
        
        
        
            lines = rows[n]
            
            # for line in lines: 
            lines = "', '".join(lines)
            lines = "'"+lines+"'"
            
            sql = f"""INSERT INTO {table} ({header})
            VALUES ({lines})
            """
                
            with engine.connect() as connection:
                connection.execute(sql) 
            
            # print(sql)
            print("Record inserted")
            n += 1
        else:
            print("Success! All lines loaded!")
    
upload_csv(name, table)
        
