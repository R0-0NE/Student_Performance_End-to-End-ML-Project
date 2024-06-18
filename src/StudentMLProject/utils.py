import os
import sys 
from src.StudentMLProject.exception import CustomException
from src.StudentMLProject.logger import logging
import pandas as pd 
from dotenv import load_dotenv
import pymysql
##from sqlalchemy import create_engine

load_dotenv()

host=os.getenv("host")
user=os.getenv("user")
password=os.getenv("password")
db=os.getenv('db')


def read_sql_data():
    logging.info("Reading SQL database started")
    try:
        ##engine = create_engine('mysql+pymysql://user:password@host/db')
        mydb=pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db
        )
        logging.info("Connection established",mydb)
        
        df=pd.read_sql_query('Select * from student',mydb)
        print(df.head())

        return df

    except Exception as ex:
        raise CustomException(ex)
