import psycopg2
import tweepy
import pandas as pd
import numpy as np

# Database creds
t_host = ""
t_port = "" #default postgres port
t_dbname = ""
t_user = ""
t_pw = ""

 

class UserNotFoundError(Exception):
    def __init__(self, message):
        self.message = message


class DBConnection:

    def __init__(self):
        pass

    @classmethod
    def get_connection(cls):

        db_connection = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user, password=t_pw)

        return db_connection
