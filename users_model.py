import psycopg2
from werkzeug.security import generate_password_hash,check_password_hash
from db_connection import DBConnection

class UserNotFoundError(Exception):
    def __init__(self, message):
        self.message = message

class User:
    def __init__(self,first_name,last_name,email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

    def create_account(self):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:
            password_hash = generate_password_hash(self.password, "sha256")

            query = """ INSERT INTO users (first_name, last_name, email, password) VALUES (%s,%s,%s,%s)"""
            record_to_insert = (self.first_name, self.last_name, self.email, password_hash)

            db_cursor.execute(query,record_to_insert)
            result = db_cursor.rowcount

            return result

        except (Exception, psycopg2.Error) as error:
            raise UserNotFoundError(error)
        finally:
            db_conn.commit()
            db_conn.close()

    @classmethod
    def verify_user(cls, email, password):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:
            query = """SELECT password, first_name, last_name, email,id FROM users
                            WHERE is_active = True and email = %s"""

            db_cursor.execute(query, (email,))
            record = db_cursor.fetchone()

            result = db_cursor.rowcount
            if result > 0:
                # return True
                if check_password_hash(record[0], password):
                    return record
                else:
                    return False
            else:
                return False
        except (Exception, psycopg2.Error) as error:
            raise UserNotFoundError(error)
        finally:
            db_conn.close()

    @classmethod
    def get_user_details(cls, user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:
            query = """SELECT first_name, last_name, email,id FROM users
                            WHERE id = %s"""

            db_cursor.execute(query, (user_id,))
            record = db_cursor.fetchone()
            result = db_cursor.rowcount

            return record

        except (Exception, psycopg2.Error) as error:
            raise UserNotFoundError(error)
        finally:
            db_conn.close()

    @classmethod
    def set_user_session_data(self,user_id,session_key,session_data):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            # delete existing session
            query = """DELETE FROM user_session_data WHERE user_id = %s and session_key = %s"""
            db_cursor.execute(query,(user_id,session_key))
            result = db_cursor.rowcount

            # insert sessin data
            if session_data != "":
                query = """ INSERT INTO user_session_data (user_id,session_key,session_data) VALUES (%s,%s,%s)"""
                record_to_insert = (user_id,session_key, session_data)

                db_cursor.execute(query,record_to_insert)
                result = db_cursor.rowcount

            return result

        except (Exception, psycopg2.Error) as error:
            raise UserNotFoundError(error)
        finally:
            db_conn.commit()
            db_conn.close()

    @classmethod
    def get_user_session_data(cls, user_id,session_key):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:
            query = """SELECT session_data FROM user_session_data WHERE user_id = %s and session_key = %s"""

            db_cursor.execute(query, (user_id,session_key))
            record = db_cursor.fetchone()
            result = db_cursor.rowcount

            return record

        except (Exception, psycopg2.Error) as error:
            raise UserNotFoundError(error)
        finally:
            db_conn.close()
