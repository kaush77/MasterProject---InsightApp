import psycopg2
from db_connection import DBConnection

class CommonData:

    def __init__(self,first_name,last_name,email, message):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.message = message

    def save_user_message(self):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:
            query = """ INSERT INTO contact_us (first_name, last_name, email, message) VALUES (%s,%s,%s,%s)"""
            record_to_insert = (self.first_name, self.last_name, self.email, self.message)

            db_cursor.execute(query,record_to_insert)
            result = db_cursor.rowcount

            return result

        except (Exception, psycopg2.Error) as error:
            raise UserNotFoundError(error)
        finally:
            db_conn.commit()
            db_conn.close()
