import psycopg2
import tweepy
from db_connection import DBConnection

class ErrorFound(Exception):
    def __init__(self, message):
        self.message = message


class SettingModel:

    def __init__(self):
        pass

    # twitter account methods
    @classmethod
    def get_twitter_account(cls,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:
            query = """
            SELECT ta.id, screen_id, screen_name, country,(CASE WHEN twitter_account_id IS NOT NULL THEN True ELSE False END) "twitter_account_id"
            FROM twitter_account ta LEFT JOIN user_twitter_account_mapping tam ON ta.id = tam.twitter_account_id
            WHERE ta.is_active = True AND tam.user_id=%s
            UNION
            SELECT ta.id, screen_id, screen_name, country,False "twitter_account_id"
            FROM twitter_account ta WHERE ta.id NOT IN(SELECT DISTINCT ta.id
            FROM twitter_account ta LEFT JOIN user_twitter_account_mapping tam ON ta.id = tam.twitter_account_id
            WHERE ta.is_active = True AND tam.user_id=%s) ORDER BY twitter_account_id DESC"""


            db_cursor.execute(query,(user_id,user_id))
            twiter_records = db_cursor.fetchall()
            return twiter_records

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    @classmethod
    def add_twitter_account(cls,screen_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            CONSUMER_KEY = "9NfQodgml2Io3uUFslehvzZXd"
            CONSUMER_SECRET = "cF1dN1SNK4X4VShvzBPQSb872opJeHLI2oQ8W8fGaBrHZ5KKsb"
            ACCESS_TOKEN = "1143151270913552386-nTV6DXH8ri21Kdzbmjqbv167RfMS1V"
            ACCESS_TOKEN_SECRET = "l2DraSWLyqr2YNq4aK2dbwmVEmP3SLC205pTodNVDU5SA"

            # Authenticate to Twitter
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

            api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

            # get user details
            twitter_user_details = api.get_user(screen_name = screen_id)

            tweet_list = []

            screen_id = twitter_user_details.screen_name
            screen_name = twitter_user_details.name
            profile = twitter_user_details.description
            country = twitter_user_details.location
            details = twitter_user_details.description

            tweet_list.append({screen_id,screen_name,profile,country,details})

            # check if account already exists
            query = """SELECT id, screen_id, screen_name, country FROM twitter_account
                            WHERE screen_id = %s"""

            db_cursor.execute(query, (screen_id,))
            record = db_cursor.fetchone()
            result = db_cursor.rowcount

            if result > 0:
                query = """UPDATE twitter_account SET is_active = True WHERE screen_id = %s"""

                db_cursor.execute(query, (screen_id,))
                result = db_cursor.rowcount
            else:
                query = """ INSERT INTO twitter_account (screen_id,screen_name,profile,country,details)
                                        VALUES (%s,%s,%s,%s,%s) """

                db_cursor.execute(query, (screen_id,screen_name,profile,country,details))
                result = db_cursor.rowcount

            return result

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.commit()
            db_conn.close()


    @classmethod
    def map_twitter_account(cls,twitter_account_list,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            # delete existing mapping records
            query = """DELETE FROM user_twitter_account_mapping
                            WHERE user_id = %s"""

            db_cursor.execute(query, (user_id,))
            result = db_cursor.rowcount

            if len(twitter_account_list) > 0:
                # insert map twitter account
                query = """ INSERT INTO user_twitter_account_mapping (user_id,twitter_account_id)
                                    VALUES (%s,%s) """

                for twitter_account_id in twitter_account_list:
                    db_cursor.execute(query, (user_id,twitter_account_id))
                    result = db_cursor.rowcount

            return result

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.commit()
            db_conn.close()


    # website scrap methods
    @classmethod
    def get_website_urls(cls,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:
            query = """
            SELECT DISTINCT ta.id, website_category,website_link, (CASE WHEN news_account_id IS NOT NULL THEN True ELSE False END) "news_account_id"
            FROM website_configuration ta LEFT JOIN user_newssite_account_mapping tam ON ta.id = tam.news_account_id
            WHERE ta.is_active = True AND tam.user_id=%s
            UNION
            SELECT ta.id, website_category, website_link, False "news_account_id"
            FROM website_configuration ta WHERE ta.id NOT IN(SELECT DISTINCT ta.id
            FROM website_configuration ta LEFT JOIN user_newssite_account_mapping tam ON ta.id = tam.news_account_id
            WHERE ta.is_active = True AND tam.user_id=%s) ORDER BY news_account_id DESC"""


            db_cursor.execute(query,(user_id,user_id))
            news_records = db_cursor.fetchall()
            return news_records

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    @classmethod
    def get_monitor_newssite(cls,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:
            query = """ select id, website_url from user_monitor_newssite where user_id=%s"""

            db_cursor.execute(query,(user_id,))
            news_records = db_cursor.fetchall()
            return news_records

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    @classmethod
    def add_website_url(cls,website_url,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            # check if url already exists
            query = """SELECT id  FROM user_monitor_newssite
                            WHERE website_url = %s and user_id=%s"""

            db_cursor.execute(query, (website_url,user_id))
            record = db_cursor.fetchone()
            result = db_cursor.rowcount

            if result > 0:
                query = """UPDATE user_monitor_newssite SET is_active = True WHERE website_url = %s and user_id=%s"""

                db_cursor.execute(query, (website_url,user_id))
                result = db_cursor.rowcount
            else:
                query = """ INSERT INTO user_monitor_newssite (user_id,website_url)
                                        VALUES (%s,%s) """

                db_cursor.execute(query, (user_id,website_url))
                result = db_cursor.rowcount

            return result

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.commit()
            db_conn.close()

    @classmethod
    def update_monitor_site_list(cls,selected_website):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            # check if url already exists
            query = """DELETE FROM user_monitor_newssite WHERE id = %s"""

            for site_id in selected_website:
                db_cursor.execute(query, (site_id,))
                result = db_cursor.rowcount

            return result

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.commit()
            db_conn.close()

    @classmethod
    def map_user_website(cls,selected_website_url,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            # delete existing mapping records
            query = """DELETE FROM user_newssite_account_mapping
                            WHERE user_id = %s"""

            db_cursor.execute(query, (user_id,))
            result = db_cursor.rowcount

            if len(selected_website_url) > 0:
                # insert map twitter account
                query = """ INSERT INTO user_newssite_account_mapping (user_id,news_account_id)
                                        VALUES (%s,%s) """

                for website_id in selected_website_url:
                    db_cursor.execute(query, (user_id,website_id))
                    result = db_cursor.rowcount

            return result

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.commit()
            db_conn.close()


    # auto complete record and companies watch list

    @classmethod
    def get_autocomplete_records(cls):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:
            query = """ select CONCAT(symbol,'_', name) AS "search" from indices_componets WHERE is_active = True """

            db_cursor.execute(query)
            records = db_cursor.fetchall()
            return records

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    @classmethod
    def get_map_user_companies_list(cls,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:
            query = """
                    select t2.id, t1.exchange,t1.country,t1.symbol,t1.name,t2.search_criteria
                    from indices_componets t1 JOIN user_companies_watch_list t2 ON
                    t1.id = t2.indices_componets_id AND user_id=%s """

            db_cursor.execute(query,(user_id,))
            records = db_cursor.fetchall()
            return records

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    @classmethod
    def add_user_companies_watch_list(cls,search_company,search_criteria,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            query = """ select id from indices_componets WHERE is_active = True and CONCAT(symbol,'_', name) = %s """

            db_cursor.execute(query,(search_company,))
            search_record = db_cursor.fetchone()
            result = db_cursor.rowcount

            if result > 0:
                indices_componets_id = search_record[0]

                # delete existing mapping records
                query = """DELETE FROM user_companies_watch_list
                            WHERE user_id = %s and indices_componets_id=%s"""

                db_cursor.execute(query, (user_id,indices_componets_id))
                result = db_cursor.rowcount

                # insert map twitter account
                query = """ INSERT INTO user_companies_watch_list (user_id,indices_componets_id,search_criteria)
                                        VALUES (%s,%s,%s) """

                db_cursor.execute(query, (user_id,indices_componets_id,search_criteria))
                result = db_cursor.rowcount

            return result

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.commit()
            db_conn.close()


    @classmethod
    def update_user_companies_watch_list(cls,selected_list):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            # check if url already exists
            query = """DELETE FROM user_companies_watch_list WHERE id = %s"""

            for site_id in selected_list:
                db_cursor.execute(query, (site_id,))
                result = db_cursor.rowcount

            return result

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.commit()
            db_conn.close()
