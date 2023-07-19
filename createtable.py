from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]='postgresql://admin:123456@127.0.0.1:5432/petola'
db = SQLAlchemy(app)

@app.route('/')
def index():
    sql = """
    CREATE TABLE pethouse (
    id serial Not NULL,
    uid character varying(50) NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    fan BOOLEAN,
    PRIMARY KEY (id));
    
    CREATE TABLE peteat (
    id serial Not NULL,
    uid character varying(50) NOT NULL,
    feederweight character varying(50) NOT NULL,
    feedertime character varying(50) NOT NULL,
    PRIMARY KEY (id));
    
    CREATE TABLE petlive (
    id serial Not NULL,
    uid character varying(50) NOT NULL,
    urllink VARCHAR(255) NOT NULL,
    PRIMARY KEY (id));

    CREATE TABLE login (
    id serial Not NULL,
    uid character varying(50) NOT NULL,
    petolacode character varying(50) NOT NULL,
    petolapassword VARCHAR(50) NOT NULL,
    PRIMARY KEY (id));
    
    CREATE TABLE users(
    id serial Not NULL, 
    uid character varying(50) NOT NULL,
    PRIMARY KEY (id));
    
    """
    db.engine.execute(sql)
    return "資料表建立成功 !"

if __name__ =='__main__':
    app.run(debug=True,use_reloader=False)

