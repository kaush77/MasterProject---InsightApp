import psycopg2
import tweepy
from db_connection import DBConnection

class ErrorFound(Exception):
    def __init__(self, message):
        self.message = message


class ReportModel:

    def __init__(self):
        pass


    # twitter report data

    @classmethod
    def get_twitter_article(cls,limit,offset,sentiment_type_id,user_id):

        # psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user, password=t_pw)

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            if int(sentiment_type_id) == 2:

                query = """
                        SELECT td.id,td.screen_id,td.tweet_date,td.tweet_message,ts.nltk_classify as "classifier"
                        FROM twitter_data_dump td JOIN twitter_sentiment ts
                        ON td.id = ts.tweet_id WHERE td.screen_id in (
                        SELECT DISTINCT screen_id FROM twitter_account ta LEFT JOIN user_twitter_account_mapping
                        tam ON ta.id = tam.twitter_account_id
                        WHERE ta.is_active = True AND tam.user_id=%s)
                        AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                        AND RIGHT(td.tweet_message, 1) != '?'
                        ORDER BY td.tweet_date DESC LIMIT %s OFFSET %s ROWS"""

                db_cursor.execute(query,(user_id,limit,offset))
                result = db_cursor.rowcount

                if result <= 0:
                    query = """
                            SELECT td.id,td.screen_id,td.tweet_date,td.tweet_message,ts.nltk_classify as "classifier"
                            FROM twitter_data_dump td JOIN twitter_sentiment ts
                            ON td.id = ts.tweet_id
                            WHERE array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                            AND RIGHT(td.tweet_message, 1) != '?'
                            ORDER BY td.tweet_date DESC LIMIT %s OFFSET %s ROWS"""

                    db_cursor.execute(query,(limit,offset))

                records_list = db_cursor.fetchall()
                return records_list

            elif int(sentiment_type_id) == 0 or int(sentiment_type_id) == 1:

                query = """
                        SELECT td.id,td.screen_id,td.tweet_date,td.tweet_message,ts.nltk_classify as "classifier"
                        FROM twitter_data_dump td JOIN twitter_sentiment ts
                        ON td.id = ts.tweet_id WHERE nltk_classify = %s
                        AND td.screen_id in (
                        SELECT DISTINCT screen_id FROM twitter_account ta LEFT JOIN user_twitter_account_mapping
                        tam ON ta.id = tam.twitter_account_id
                        WHERE ta.is_active = True AND tam.user_id=%s)
                        AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                        AND RIGHT(td.tweet_message, 1) != '?'
                        ORDER BY td.tweet_date DESC LIMIT %s OFFSET %s ROWS"""

                db_cursor.execute(query,(sentiment_type_id,user_id,limit,offset))
                result = db_cursor.rowcount

                if result <= 0:

                    query = """
                            SELECT td.id,td.screen_id,td.tweet_date,td.tweet_message,ts.nltk_classify as "classifier"
                            FROM twitter_data_dump td JOIN twitter_sentiment ts
                            ON td.id = ts.tweet_id WHERE nltk_classify = %s
                            AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                            AND RIGHT(td.tweet_message, 1) != '?'
                            ORDER BY td.tweet_date DESC LIMIT %s OFFSET %s ROWS"""

                    db_cursor.execute(query,(sentiment_type_id,limit,offset))

                records_list = db_cursor.fetchall()
                return records_list

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    @classmethod
    def get_twitter_article_count(cls,sentiment_type_id,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            if int(sentiment_type_id) == 2:

                query = """
                        SELECT count(*) as "record_count"
                        FROM twitter_data_dump td JOIN twitter_sentiment ts
                        ON td.id = ts.tweet_id
                        WHERE td.screen_id in (
                        SELECT DISTINCT screen_id FROM twitter_account ta LEFT JOIN user_twitter_account_mapping
                        tam ON ta.id = tam.twitter_account_id
                        WHERE ta.is_active = True AND tam.user_id=%s)
                        AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                        AND RIGHT(td.tweet_message, 1) != '?' """

                db_cursor.execute(query,(user_id,))
                records_list = db_cursor.fetchall()

                if records_list[0][0] <= 0:
                    query = """
                            SELECT count(*) as "record_count"
                            FROM twitter_data_dump td JOIN twitter_sentiment ts
                            ON td.id = ts.tweet_id
                            WHERE array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                            AND RIGHT(td.tweet_message, 1) != '?'
                            """

                    db_cursor.execute(query)

                records_list = db_cursor.fetchall()
                return records_list

            elif int(sentiment_type_id) == 0 or int(sentiment_type_id) == 1:

                query = """
                        SELECT count(*) as "record_count"
                        FROM twitter_data_dump td JOIN twitter_sentiment ts
                        ON td.id = ts.tweet_id WHERE nltk_classify = %s
                        AND td.screen_id in ( SELECT DISTINCT screen_id FROM twitter_account ta LEFT JOIN user_twitter_account_mapping
                        tam ON ta.id = tam.twitter_account_id
                        WHERE ta.is_active = True AND tam.user_id=%s)
                        AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                        AND RIGHT(td.tweet_message, 1) != '?' """

                db_cursor.execute(query,(sentiment_type_id,user_id))
                records_list = db_cursor.fetchall()

                if records_list[0][0] <= 0:
                    query = """
                            SELECT count(*) as "record_count"
                            FROM twitter_data_dump td JOIN twitter_sentiment ts
                            ON td.id = ts.tweet_id WHERE nltk_classify = %s
                            AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                            AND RIGHT(td.tweet_message, 1) != '?' """

                    db_cursor.execute(query,(sentiment_type_id,))

                records_list = db_cursor.fetchall()
                return records_list

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    @classmethod
    def get_latest_twitter_article(cls,last_date,sentiment_type_id,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            if int(sentiment_type_id) == 2:
                query = """
                    SELECT td.id,td.screen_id,td.tweet_date,td.tweet_message,ts.nltk_classify as "classifier"
                    FROM twitter_data_dump td JOIN twitter_sentiment ts ON td.id = ts.tweet_id
                    WHERE td.tweet_date > %s
                    AND td.screen_id in (SELECT DISTINCT screen_id FROM twitter_account ta LEFT JOIN user_twitter_account_mapping
                    tam ON ta.id = tam.twitter_account_id
                    WHERE ta.is_active = True AND tam.user_id=%s)
                    AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                    AND RIGHT(td.tweet_message, 1) != '?'
                    ORDER BY td.tweet_date DESC """

                db_cursor.execute(query,(last_date,user_id))
                records_list = db_cursor.fetchall()
                return records_list


            elif int(sentiment_type_id) == 0 or int(sentiment_type_id) == 1:

                query = """
                        SELECT td.id,td.screen_id,td.tweet_date,td.tweet_message,ts.nltk_classify as "classifier"
                        FROM twitter_data_dump td JOIN twitter_sentiment ts ON td.id = ts.tweet_id
                        WHERE td.tweet_date > %s AND nltk_classify = %s
                        AND td.screen_id in (SELECT DISTINCT screen_id FROM twitter_account ta LEFT JOIN user_twitter_account_mapping
                        tam ON ta.id = tam.twitter_account_id
                        WHERE ta.is_active = True AND tam.user_id=%s)
                        AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                        AND RIGHT(td.tweet_message, 1) != '?'
                        ORDER BY td.tweet_date DESC"""

                db_cursor.execute(query,(last_date,sentiment_type_id,user_id))
                records_list = db_cursor.fetchall()
                return records_list

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    # plots data
    @classmethod
    def get_twitter_pie_plot_data(cls,sentiment_type_id,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            if int(sentiment_type_id) == 2:

                query = """
                        SELECT CASE WHEN ts.nltk_classify = 1 THEN 'Positive' ELSE 'Negative' END AS "nltk_classify",
                        count(td.id) FROM twitter_data_dump td JOIN twitter_sentiment ts
                        ON td.id = ts.tweet_id WHERE td.screen_id in (SELECT DISTINCT screen_id FROM twitter_account ta
                        LEFT JOIN user_twitter_account_mapping tam ON ta.id = tam.twitter_account_id
                        WHERE ta.is_active = True AND tam.user_id=%s)
                        AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                        AND RIGHT(td.tweet_message, 1) != '?'
                        GROUP BY nltk_classify"""

                db_cursor.execute(query,(user_id,))
                result = db_cursor.rowcount

                if result <= 0:
                    query = """
                            SELECT CASE WHEN ts.nltk_classify = 1 THEN 'Positive' ELSE 'Negative' END AS "nltk_classify",
                            count(td.id) FROM twitter_data_dump td JOIN twitter_sentiment ts
                            ON td.id = ts.tweet_id
                            WHERE array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                            AND RIGHT(td.tweet_message, 1) != '?'
                            GROUP BY nltk_classify """

                    db_cursor.execute(query)

                records_list = db_cursor.fetchall()
                return records_list

            elif int(sentiment_type_id) == 0 or int(sentiment_type_id) == 1:

                query = """
                        SELECT CASE WHEN ts.nltk_classify = 1 THEN 'Positive' ELSE 'Negative' END AS "nltk_classify",
                        count(td.id) FROM twitter_data_dump td JOIN twitter_sentiment ts
                        ON td.id = ts.tweet_id WHERE nltk_classify = %s
                        AND td.screen_id in (
                        SELECT DISTINCT screen_id FROM twitter_account ta LEFT JOIN user_twitter_account_mapping
                        tam ON ta.id = tam.twitter_account_id
                        WHERE ta.is_active = True AND tam.user_id=%s)
                        AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                        AND RIGHT(td.tweet_message, 1) != '?'
                        GROUP BY nltk_classify"""

                db_cursor.execute(query,(sentiment_type_id,user_id))
                result = db_cursor.rowcount

                if result <= 0:

                    query = """
                            SELECT CASE WHEN ts.nltk_classify = 1 THEN 'Positive' ELSE 'Negative' END AS "nltk_classify",
                            count(td.id) FROM twitter_data_dump td JOIN twitter_sentiment ts
                            ON td.id = ts.tweet_id WHERE nltk_classify = %s
                            AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                            AND RIGHT(td.tweet_message, 1) != '?'
                            GROUP BY nltk_classify """

                    db_cursor.execute(query,(sentiment_type_id,))

                records_list = db_cursor.fetchall()
                return records_list

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    @classmethod
    def get_twitter_bar_plot_data(cls,sentiment_type_id,user_id,type):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            if int(sentiment_type_id) == 2:

                query = """
                        SELECT 'Sentiment' AS "entry_time",COUNT(ts.nltk_classify)
                        FROM twitter_data_dump td JOIN twitter_sentiment ts
                        ON td.id = ts.tweet_id WHERE td.screen_id in (SELECT DISTINCT screen_id FROM twitter_account ta
                        LEFT JOIN user_twitter_account_mapping tam ON ta.id = tam.twitter_account_id
                        WHERE ta.is_active = True  AND ts.nltk_classify = %s AND tam.user_id=%s)
                        AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                        AND RIGHT(td.tweet_message, 1) != '?'
                        GROUP BY ts.entry_time ORDER BY ts.entry_time ASC"""

                db_cursor.execute(query,(type,user_id))
                result = db_cursor.rowcount

                if result <= 0:
                    query = """
                            SELECT 'Sentiment' AS "entry_time",COUNT(ts.nltk_classify)
                            FROM twitter_data_dump td JOIN twitter_sentiment ts
                            ON td.id = ts.tweet_id WHERE ts.nltk_classify = %s
                            AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                            AND RIGHT(td.tweet_message, 1) != '?'
                            GROUP BY ts.entry_time ORDER BY ts.entry_time ASC"""

                    db_cursor.execute(query,(type,))

                records_list = db_cursor.fetchall()
                return records_list

            elif int(sentiment_type_id) == 0 or int(sentiment_type_id) == 1:

                query = """
                        SELECT 'Sentiment' AS "entry_time",COUNT(ts.nltk_classify)
                        FROM twitter_data_dump td JOIN twitter_sentiment ts
                        ON td.id = ts.tweet_id WHERE nltk_classify = %s AND ts.nltk_classify = %s
                        AND td.screen_id in (
                        SELECT DISTINCT screen_id FROM twitter_account ta LEFT JOIN user_twitter_account_mapping
                        tam ON ta.id = tam.twitter_account_id
                        WHERE ta.is_active = True AND tam.user_id=%s)
                        AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                        AND RIGHT(td.tweet_message, 1) != '?'
                        GROUP BY ts.entry_time ORDER BY ts.entry_time ASC"""

                db_cursor.execute(query,(sentiment_type_id,type,user_id))
                result = db_cursor.rowcount

                if result <= 0:

                    query = """
                            SELECT 'Sentiment' AS "entry_time",COUNT(ts.nltk_classify)
                            FROM twitter_data_dump td JOIN twitter_sentiment ts
                            ON td.id = ts.tweet_id WHERE nltk_classify = %s AND ts.nltk_classify = %s
                            AND array_length(regexp_split_to_array(td.tweet_message, '\s'),1) > 10
                            AND RIGHT(td.tweet_message, 1) != '?'
                            GROUP BY ts.entry_time ORDER BY ts.entry_time ASC"""

                    db_cursor.execute(query,(sentiment_type_id,type))

                records_list = db_cursor.fetchall()
                return records_list

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()
    # end twitter report data
