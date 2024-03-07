from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
 
import application.models # Is needed for tables to be created!

def create_tables():
    db.create_all()

