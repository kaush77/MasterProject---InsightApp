import psycopg2
import tweepy
from users_model import User
import pandas as pd
import numpy as np
from db_connection import DBConnection


class ErrorFound(Exception):
    def __init__(self, message):
        self.message = message


class IndicesModel:

    def __init__(self):
        pass

    # plots data

    @classmethod
    def get_indices_plot_data(cls,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            query = """ CREATE TEMPORARY TABLE temp_table(
            		   entry_date DATE
            		 );
            	 	 insert into temp_table
            		 select entry_date from indices_data where index_id=1
            		 intersect
            		 select entry_date from indices_data where index_id=2
            		 intersect
            		 select entry_date from indices_data where index_id=3
					 intersect
            		 select entry_date from indices_data where index_id=4
					 intersect
            		 select entry_date from indices_data where index_id=5
					 intersect
            		 select entry_date from indices_data where index_id=6
					 intersect
            		 select entry_date from indices_data where index_id=7
					 intersect
            		 select entry_date from indices_data where index_id=9
					 intersect
            		 select entry_date from indices_data where index_id=13
					 intersect
            		 select entry_date from indices_data where index_id=14;

            		 SELECT ind.index_symbol,TO_CHAR(idata.entry_date :: DATE, 'dd/mm/yyyy') AS "entry_date",
                     ROUND(idata.adj_close,2) AS "adj_close" FROM  indices ind JOIN indices_data idata
                     ON ind.id = idata.index_id
            		 WHERE idata.entry_date IN (SELECT DISTINCT entry_date FROM temp_table)
                     ORDER BY index_symbol, idata.entry_date ASC """

            db_cursor.execute(query)
            records_list = db_cursor.fetchall()

            df_indices_data = pd.DataFrame(records_list,columns=["index_symbol","entry_date","adj_close"])
            df_indices_data['adj_close'] = df_indices_data['adj_close'].astype(float)

            # get user session data
            user_session_list = User.get_user_session_data(user_id,"selected_indices")
            if user_session_list is not None and len(user_session_list) > 0:
                selected_indices_list = user_session_list[0]
                selected_indices_list = selected_indices_list.split("_")
                df_indices_data = df_indices_data.loc[df_indices_data['index_symbol'].isin(selected_indices_list)]

            return df_indices_data

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    @classmethod
    def get_indices(cls):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            query = """ SELECT DISTINCT ind.index_symbol FROM  indices ind JOIN indices_data idata
                        ON ind.id = idata.index_id ORDER BY index_symbol ASC"""

            db_cursor.execute(query)
            records_list = db_cursor.fetchall()

            # df_indices_data = pd.DataFrame(records_list,columns=["index_symbol"])
            return records_list

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()
