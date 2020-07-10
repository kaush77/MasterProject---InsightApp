import psycopg2
import tweepy
from db_connection import DBConnection


class ErrorFound(Exception):
    def __init__(self, message):
        self.message = message


class ReportNewsModel:

    def __init__(self):
        pass

    # twitter report data

    @classmethod
    def get_news_article(cls,limit,offset,sentiment_type_id,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            if int(sentiment_type_id) == 2:

                query = """
                        SELECT ndump.id,ndump.header,case when coalesce(ndump.sub_header, '') != '' AND ndump.sub_header != 'NaN' THEN ndump.sub_header ELSE 'no_value' END "sub_header",
                        ndump.website,
                        CASE WHEN ndump.news_link LIKE 'http' THEN ndump.news_link ELSE CONCAT(ndump.website_link,ndump.news_link) END AS "web_link",
                        nsentiment.nltk_classify as "classifier",TO_DATE(TO_CHAR(nsentiment.entry_time :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') AS "entry_time"
                        FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                        ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header')
                        AND ndump.website_link in ( select DISTINCT website_link from website_configuration wconfig JOIN user_newssite_account_mapping uconfigmap
                        ON wconfig.id = uconfigmap.news_account_id WHERE user_id=%s)
                        ORDER BY nsentiment.entry_time DESC LIMIT %s OFFSET %s ROWS"""

                db_cursor.execute(query,(user_id,limit,offset))
                result = db_cursor.rowcount

                if result <= 0:
                    query = """
                            SELECT ndump.id,ndump.header,case when coalesce(ndump.sub_header, '') != '' AND ndump.sub_header != 'NaN' THEN ndump.sub_header ELSE 'no_value' END "sub_header",
                            ndump.website,
                            CASE WHEN ndump.news_link LIKE 'http' THEN ndump.news_link ELSE CONCAT(ndump.website_link,ndump.news_link) END AS "web_ink",
                            nsentiment.nltk_classify as "classifier",TO_DATE(TO_CHAR(nsentiment.entry_time :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') AS "entry_time"
                            FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                            ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header')
                            ORDER BY nsentiment.entry_time DESC LIMIT %s OFFSET %s ROWS"""

                    db_cursor.execute(query,(limit,offset))

                records_list = db_cursor.fetchall()
                return records_list

            elif int(sentiment_type_id) == 0 or int(sentiment_type_id) == 1:

                query = """
                        SELECT ndump.id,ndump.header,case when coalesce(ndump.sub_header, '') != '' AND ndump.sub_header != 'NaN' THEN ndump.sub_header ELSE 'no_value' END "sub_header",
                        ndump.website,
                        CASE WHEN ndump.news_link LIKE 'http' THEN ndump.news_link ELSE CONCAT(ndump.website_link,ndump.news_link) END AS "web_ink",
                        nsentiment.nltk_classify as "classifier",TO_DATE(TO_CHAR(nsentiment.entry_time :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') AS "entry_time"
                        FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                        ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header') AND nsentiment.nltk_classify = %s
                        AND ndump.website_link in ( select DISTINCT website_link from website_configuration wconfig JOIN
                        user_newssite_account_mapping uconfigmap
                        ON wconfig.id = uconfigmap.news_account_id WHERE user_id=%s)
                        ORDER BY nsentiment.entry_time DESC LIMIT %s OFFSET %s ROWS"""

                db_cursor.execute(query,(sentiment_type_id,user_id,limit,offset))
                result = db_cursor.rowcount

                if result <= 0:

                    query = """
                            SELECT ndump.id,ndump.header,case when coalesce(ndump.sub_header, '') != '' AND ndump.sub_header != 'NaN' THEN ndump.sub_header ELSE 'no_value' END "sub_header",
                            ndump.website,
                            CASE WHEN ndump.news_link LIKE 'http' THEN ndump.news_link ELSE CONCAT(ndump.website_link,ndump.news_link) END AS "web_ink",
                            nsentiment.nltk_classify as "classifier",TO_DATE(TO_CHAR(nsentiment.entry_time :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') AS "entry_time"
                            FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                            ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header') AND nsentiment.nltk_classify = %s
                            ORDER BY ndump.entry_time DESC LIMIT %s OFFSET %s ROWS"""

                    db_cursor.execute(query,(sentiment_type_id,limit,offset))

                records_list = db_cursor.fetchall()
                return records_list

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    @classmethod
    def get_news_article_count(cls,sentiment_type_id,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            if int(sentiment_type_id) == 2:

                query = """
                        SELECT count(*) FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                        ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header')
                        AND ndump.website_link in ( select DISTINCT website_link from website_configuration
                        wconfig JOIN user_newssite_account_mapping uconfigmap
                        ON wconfig.id = uconfigmap.news_account_id WHERE user_id=%s)  """

                db_cursor.execute(query,(user_id,))
                records_list = db_cursor.fetchall()

                if records_list[0][0] <= 0:
                    query = """
                            SELECT count(*) FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                            ON ndump.id = nsentiment.news_id WHERE sentiment_for in('header') """

                    db_cursor.execute(query)

                records_list = db_cursor.fetchall()
                return records_list

            elif int(sentiment_type_id) == 0 or int(sentiment_type_id) == 1:

                query = """
                        SELECT count(*) FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                        ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header') AND nsentiment.nltk_classify = %s
                        AND ndump.website_link in ( select DISTINCT website_link from website_configuration wconfig JOIN user_newssite_account_mapping uconfigmap
                        ON wconfig.id = uconfigmap.news_account_id WHERE user_id=%s)  """

                db_cursor.execute(query,(sentiment_type_id,user_id))
                records_list = db_cursor.fetchall()

                if records_list[0][0] <= 1:
                    query = """
                            SELECT count(*) FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                            ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header') AND nsentiment.nltk_classify = %s  """

                    db_cursor.execute(query,(sentiment_type_id,))

                records_list = db_cursor.fetchall()
                return records_list

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    @classmethod
    def get_latest_news_article(cls,last_date,sentiment_type_id,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            if int(sentiment_type_id) == 2:
                query = """
                    SELECT ndump.id,ndump.header,case when coalesce(ndump.sub_header, '') != '' AND ndump.sub_header != 'NaN' THEN ndump.sub_header ELSE 'no_value' END "sub_header",
                    ndump.website,
                    CASE WHEN ndump.news_link LIKE 'http' THEN ndump.news_link ELSE CONCAT(ndump.website_link,ndump.news_link) END AS "web_ink",
                    nsentiment.nltk_classify as "classifier",TO_CHAR(nsentiment.entry_time :: DATE, 'yyyy-mm-dd') AS "entry_time"
                    FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                    ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header') AND nsentiment.entry_time >  %s
                    AND ndump.website_link in (select DISTINCT website_link from website_configuration wconfig JOIN user_newssite_account_mapping uconfigmap
                    ON wconfig.id = uconfigmap.news_account_id WHERE user_id=%s)
                    ORDER BY nsentiment.entry_time DESC   """

                db_cursor.execute(query,(last_date,user_id))
                records_list = db_cursor.fetchall()
                return records_list


            elif int(sentiment_type_id) == 0 or int(sentiment_type_id) == 1:

                query = """
                        SELECT ndump.id,ndump.header,case when coalesce(ndump.sub_header, '') != '' AND ndump.sub_header != 'NaN' THEN ndump.sub_header ELSE 'no_value' END "sub_header"
                        ,ndump.website,
                        CASE WHEN ndump.news_link LIKE 'http' THEN ndump.news_link ELSE CONCAT(ndump.website_link,ndump.news_link) END AS "web_ink",
                        nsentiment.nltk_classify as "classifier",TO_CHAR(nsentiment.entry_time :: DATE, 'yyyy-mm-dd') AS "entry_time"
                        FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                        ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header') AND nsentiment.entry_time >  %s AND nltk_classify = %s
                        AND ndump.website_link in (select DISTINCT website_link from website_configuration wconfig JOIN user_newssite_account_mapping uconfigmap
                        ON wconfig.id = uconfigmap.news_account_id WHERE user_id=%s)
                        ORDER BY nsentiment.entry_time DESC """

                db_cursor.execute(query,(last_date,sentiment_type_id,user_id))
                records_list = db_cursor.fetchall()
                return records_list

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    # plots data

    @classmethod
    def get_news_pie_plot_data(cls,sentiment_type_id,user_id):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            if int(sentiment_type_id) == 2:

                query = """
                        SELECT CASE WHEN nsentiment.nltk_classify = 1 THEN 'Positive' ELSE 'Negative' END AS "nltk_classify",
                        COUNT(ndump.id) FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                        ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header')
                        AND ndump.website_link in (select DISTINCT website_link from website_configuration wconfig JOIN user_newssite_account_mapping uconfigmap
                        ON wconfig.id = uconfigmap.news_account_id WHERE user_id=%s)
                        GROUP BY nltk_classify"""

                db_cursor.execute(query,(user_id,))
                result = db_cursor.rowcount

                if result <= 0:
                    query = """
                            SELECT CASE WHEN nsentiment.nltk_classify = 1 THEN 'Positive' ELSE 'Negative' END AS "nltk_classify",
                            COUNT(ndump.id) FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                            ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header')
                            GROUP BY nltk_classify """

                    db_cursor.execute(query)

                records_list = db_cursor.fetchall()
                return records_list

            elif int(sentiment_type_id) == 0 or int(sentiment_type_id) == 1:

                query = """
                        SELECT CASE WHEN nsentiment.nltk_classify = 1 THEN 'Positive' ELSE 'Negative' END AS "nltk_classify",
                        COUNT(ndump.id) FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                        ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header') AND nltk_classify = %s
                        AND ndump.website_link in (select DISTINCT website_link from website_configuration wconfig JOIN user_newssite_account_mapping uconfigmap
                        ON wconfig.id = uconfigmap.news_account_id WHERE user_id=%s)
                        GROUP BY nltk_classify"""

                db_cursor.execute(query,(sentiment_type_id,user_id))
                result = db_cursor.rowcount

                if result <= 0:

                    query = """
                            SELECT CASE WHEN nsentiment.nltk_classify = 1 THEN 'Positive' ELSE 'Negative' END AS "nltk_classify",
                            COUNT(ndump.id) FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                            ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header') AND nltk_classify = %s
                            GROUP BY nltk_classify """

                    db_cursor.execute(query,(sentiment_type_id,))

                records_list = db_cursor.fetchall()
                return records_list

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    @classmethod
    def get_news_bar_plot_data(cls,sentiment_type_id,user_id,type):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        try:

            if int(sentiment_type_id) == 2:

                query = """
                        SELECT 'Sentiment' AS "entry_time",COUNT(nsentiment.nltk_classify)
                        FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                        ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header') AND nsentiment.nltk_classify = %s
                        AND ndump.website_link in (select DISTINCT website_link from website_configuration wconfig JOIN user_newssite_account_mapping uconfigmap
                        ON wconfig.id = uconfigmap.news_account_id WHERE user_id = %s)
                        GROUP BY nsentiment.entry_time ORDER BY nsentiment.entry_time ASC """

                db_cursor.execute(query,(type,user_id))
                result = db_cursor.rowcount

                if result <= 0:
                    query = """
                            SELECT 'Sentiment' AS "entry_time",COUNT(nsentiment.nltk_classify)
                            FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                            ON ndump.id = nsentiment.news_id WHERE sentiment_for in('header')
                            AND nsentiment.nltk_classify = %s GROUP BY nsentiment.entry_time ORDER BY nsentiment.entry_time ASC"""

                    db_cursor.execute(query,(type,))

                records_list = db_cursor.fetchall()
                return records_list

            elif int(sentiment_type_id) == 0 or int(sentiment_type_id) == 1:

                query = """
                        SELECT 'Sentiment' AS "entry_time",COUNT(nsentiment.nltk_classify)
                        FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                        ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header') AND nltk_classify =  %s AND nsentiment.nltk_classify = %s
                        AND ndump.website_link in (select DISTINCT website_link from website_configuration wconfig JOIN user_newssite_account_mapping uconfigmap
                        ON wconfig.id = uconfigmap.news_account_id WHERE user_id = %s)
                        GROUP BY nsentiment.entry_time ORDER BY nsentiment.entry_time ASC """

                db_cursor.execute(query,(sentiment_type_id,type,user_id))
                result = db_cursor.rowcount

                if result <= 0:

                    query = """
                            SELECT 'Sentiment' AS "entry_time",COUNT(nsentiment.nltk_classify)
                            FROM news_feeds_dump ndump JOIN news_feeds_sentiment nsentiment
                            ON ndump.id = nsentiment.news_id WHERE sentiment_for in('sub_header') AND nltk_classify = %s AND nsentiment.nltk_classify = %s
                            GROUP BY nsentiment.entry_time ORDER BY nsentiment.entry_time ASC """

                    db_cursor.execute(query,(sentiment_type_id,type))

                records_list = db_cursor.fetchall()
                return records_list

        except (Exception, psycopg2.Error) as error:
            raise ErrorFound(error)

        finally:
            db_conn.close()

    # end twitter report data
