import psycopg2
import tweepy
from users_model import User
import pandas as pd
import numpy as np
from db_connection import DBConnection


class ErrorFound(Exception):
    def __init__(self, message):
        self.message = message


class IndexPageModel:

    def __init__(self):
        pass

    @classmethod
    def get_indices_data(cls):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        query = """ SELECT DISTINCT ind.index_symbol FROM  indices ind JOIN indices_data idata
                             ON ind.id = idata.index_id ORDER BY index_symbol DESC"""

        db_cursor.execute(query)
        unique_indices_list = db_cursor.fetchall()

        columns = ['country','index_symbol','entry_date','lat','lon','open','adj_close','adj_close_change','percent_change']


        indices_data_list = []
        for row in unique_indices_list:

            query = """ CREATE TEMPORARY TABLE indices_data_temp
                    (
                    	index_id INT,
                    	index_name VARCHAR(100) NOT NULL,
                    	index_symbol VARCHAR(50) NOT NULL,
                    	entry_date DATE,
                    	lat VARCHAR(30) NOT NULL,
                    	lon VARCHAR(30) NOT NULL,
                    	open DECIMAL,
                    	adj_close DECIMAL
                    );

                    INSERT INTO indices_data_temp
                    SELECT DISTINCT idata.index_id,ind.country,ind.index_symbol,idata.entry_date,ind.lat,ind.lon,ROUND(idata.open,2) open,ROUND(idata.adj_close,2) adj_close
                    FROM indices ind JOIN indices_data idata ON ind.id = idata.index_id;

                    select ind.country,ind.index_symbol,idata.entry_date,ind.lat,ind.lon,ROUND(idata.open,2) open,
                    ROUND(idata.adj_close,2) adj_close,
                    ROUND(idata.adj_close,2) - lag(ROUND(idata.adj_close,2)) over (order by idata.entry_date, ind.index_symbol) as adj_close_change,
                    round(((ROUND(idata.adj_close,2) - lag(ROUND(idata.adj_close,2)) over (order by idata.entry_date, ind.index_symbol))/lag(ROUND(idata.adj_close,2))
                    over (order by idata.entry_date, ind.index_symbol))*100,2) as percent_change
                    FROM indices ind JOIN indices_data_temp idata ON ind.id = idata.index_id WHERE idata.index_symbol = %s
                    ORDER BY ind.index_symbol,idata.entry_date DESC;"""

            db_cursor.execute(query,(row[0],))
            indices_data = db_cursor.fetchall()
            row_count = db_cursor.rowcount

            if row_count > 0:
                indices_data_list.append(indices_data[0])

                indices_map_data = pd.DataFrame(indices_data_list,columns=columns)
                indices_map_data['adj_close'] = indices_map_data['adj_close'].astype(float)
                indices_map_data['adj_close_change'] = indices_map_data['adj_close_change'].astype(float)
                indices_map_data['percent_change'] = indices_map_data['percent_change'].astype(float)

                indices_map_data.sort_values(by=['entry_date','country'], inplace=True, ascending=False)

            query = "drop table indices_data_temp;"
            db_cursor.execute(query)

        return list(indices_map_data.itertuples(index=False))

    @classmethod
    def get_twitter_plot_data(cls,sentiment_type):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        query = """
                SELECT TO_DATE(TO_CHAR(tweet_date :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') "record_date",COUNT(tsentiment.nltk_classify)
                FROM twitter_data_dump tdump JOIN twitter_sentiment tsentiment ON tdump.id = tsentiment.tweet_id
                WHERE TO_DATE(TO_CHAR(tweet_date :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') >= '2020-03-01' AND tsentiment.nltk_classify = %s
                AND array_length(regexp_split_to_array(tdump.tweet_message, '\s'),1) > 10
                AND tdump.screen_id in (SELECT DISTINCT screen_id FROM twitter_account WHERE is_active = true)
                GROUP BY record_date ORDER BY record_date ASC """

        db_cursor.execute(query,(sentiment_type,))
        records_list = db_cursor.fetchall()
        return records_list

    @classmethod
    def get_news_plot_data(cls,sentiment_type):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        query = """
                SELECT CASE
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' AND position('hours' in LOWER(tdump.timestamp)) > 0
                THEN TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' AND position('ist' in LOWER(tdump.timestamp)) > 0
                THEN TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' AND position('ago' in LOWER(tdump.timestamp)) > 0
                THEN TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' THEN TO_DATE(TO_CHAR(timestamp:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                ELSE TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') END AS "record_date",COUNT(tsentiment.nltk_classify)
                FROM news_feeds_dump tdump JOIN news_feeds_sentiment tsentiment ON tdump.id = tsentiment.news_id
                WHERE TO_DATE(TO_CHAR(tdump.entry_time :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') >= '2020-03-01' AND tsentiment.nltk_classify = %s
                AND sentiment_for='sub_header'
                GROUP BY record_date ORDER BY record_date ASC """

        db_cursor.execute(query,(sentiment_type,))
        records_list = db_cursor.fetchall()
        return records_list

    @classmethod
    def get_indices_vs_sentiment_plot_data(cls):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        df_data_positive = pd.DataFrame(columns=['Record_Date','News_Positive_Sentiment_Count'])
        df_data_negative = pd.DataFrame(columns=['Record_Date','News_Negative_Sentiment_Count'])
        df_data_indices = pd.DataFrame(columns=['Record_Date','Indices_Sentiment'])

        query=""" SELECT CASE
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' AND position('hours' in LOWER(tdump.timestamp)) > 0
                THEN TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' AND position('ist' in LOWER(tdump.timestamp)) > 0
                THEN TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' AND position('ago' in LOWER(tdump.timestamp)) > 0
                THEN TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' THEN TO_DATE(TO_CHAR(timestamp:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                ELSE TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') END AS "record_date",COUNT(tsentiment.nltk_classify)
                FROM news_feeds_dump tdump JOIN news_feeds_sentiment tsentiment ON tdump.id = tsentiment.news_id
                WHERE TO_DATE(TO_CHAR(tdump.entry_time :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') >= '2020-03-01' AND tsentiment.nltk_classify = 1
                AND sentiment_for='sub_header'
                GROUP BY record_date ORDER BY record_date ASC """


        # AND tdump.website in ('businessinsider','economic_times')
        db_cursor.execute(query)
        positive_sentiment_data = db_cursor.fetchall()

        data_list = []
        for row in positive_sentiment_data:
            df_data_positive = df_data_positive.append({'Record_Date': row[0],
                                     'News_Positive_Sentiment_Count': row[1]},ignore_index=True)

        df_data_positive['News_Positive_Sentiment_Count'] = df_data_positive['News_Positive_Sentiment_Count'].astype(int)


        query=""" SELECT CASE
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' AND position('hours' in LOWER(tdump.timestamp)) > 0
                THEN TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' AND position('ist' in LOWER(tdump.timestamp)) > 0
                THEN TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' AND position('ago' in LOWER(tdump.timestamp)) > 0
                THEN TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' THEN TO_DATE(TO_CHAR(timestamp:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                ELSE TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') END AS "record_date",COUNT(tsentiment.nltk_classify)
                FROM news_feeds_dump tdump JOIN news_feeds_sentiment tsentiment ON tdump.id = tsentiment.news_id
                WHERE TO_DATE(TO_CHAR(tdump.entry_time :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') >= '2020-03-01' AND tsentiment.nltk_classify = 0
                AND sentiment_for='sub_header'
                GROUP BY record_date ORDER BY record_date ASC """

        db_cursor.execute(query)
        negative_sentiment_data = db_cursor.fetchall()

        data_list = []
        for row in negative_sentiment_data:
            df_data_negative = df_data_negative.append({'Record_Date': row[0],
                                     'News_Negative_Sentiment_Count': row[1]},ignore_index=True)

        df_data_negative['News_Negative_Sentiment_Count'] = df_data_negative['News_Negative_Sentiment_Count'].astype(int)

        # merge sentiment data
        sentiment_data = pd.merge(df_data_positive,df_data_negative[['Record_Date','News_Negative_Sentiment_Count']],
                 on='Record_Date')

        sentiment_data['Day_Sentiment'] = np.where(sentiment_data['News_Positive_Sentiment_Count'] >= sentiment_data['News_Negative_Sentiment_Count'], 1, 0)


        # indices data
        query = """ SELECT DISTINCT ind.index_symbol FROM  indices ind JOIN indices_data idata
                             ON ind.id = idata.index_id 
                             ORDER BY index_symbol DESC"""

        db_cursor.execute(query)
        unique_indices_list = db_cursor.fetchall()

        columns = ['entry_date','percent_change']

        query = """ select DISTINCT entry_date from indices_data order by entry_date desc; """

        db_cursor.execute(query)
        unique_indices_date = db_cursor.fetchall()

        for row_date in unique_indices_date:

            indices_data_list = []
            for row in unique_indices_list:

                query = """ CREATE TEMPORARY TABLE indices_data_temp
                                (
                                index_id INT,
                                index_name VARCHAR(100) NOT NULL,
                                index_symbol VARCHAR(50) NOT NULL,
                                entry_date DATE,
                                lat VARCHAR(30) NOT NULL,
                                lon VARCHAR(30) NOT NULL,
                                open DECIMAL,
                                adj_close DECIMAL
                                );

                                INSERT INTO indices_data_temp
                                SELECT DISTINCT idata.index_id,ind.country,ind.index_symbol,idata.entry_date,ind.lat,ind.lon,ROUND(idata.open,2) open,ROUND(idata.adj_close,2) adj_close
                                FROM indices ind JOIN indices_data idata ON ind.id = idata.index_id;

                                select idata.entry_date,
                                round(((ROUND(idata.adj_close,2) - lag(ROUND(idata.adj_close,2)) over (order by idata.entry_date, ind.index_symbol))/lag(ROUND(idata.adj_close,2))
                                over (order by idata.entry_date, ind.index_symbol))*100,2) as percent_change
                                FROM indices ind JOIN indices_data_temp idata ON ind.id = idata.index_id WHERE
                                idata.index_symbol = %s AND idata.entry_date <= %s
                                 ORDER BY ind.index_symbol,idata.entry_date DESC;"""

                db_cursor.execute(query,(row[0],row_date[0]))
                indices_data = db_cursor.fetchall()
                row_count = db_cursor.rowcount

                if row_count > 0:
                    indices_data_list.append(indices_data[0])

                    indices_map_data = pd.DataFrame(indices_data_list,columns=columns)
                    indices_map_data['percent_change'] = indices_map_data['percent_change'].astype(float)

                    indices_map_data.sort_values(by=['entry_date'], inplace=True, ascending=False)

                query = "drop table indices_data_temp;"
                db_cursor.execute(query)

            # price_change_sentiment =  np.where(indices_map_data[["percent_change"]].mean() > 0, 1, 0)

            seriesObj = indices_map_data.apply(lambda x: True if x['percent_change'] >= 0 else False , axis=1)
            numOfRows = len(seriesObj[seriesObj == True].index)
            numOfRows1 = len(seriesObj[seriesObj == False].index)

            price_change_sentiment = 0
            if numOfRows >= numOfRows1:
                price_change_sentiment = 1


            indices_map_data.sort_values(by=['entry_date'], inplace=True, ascending=False)
            df_data = indices_map_data[indices_map_data['entry_date'] == row_date[0]]

            #if df_data.empty == False:
            df_data_indices = df_data_indices.append({'Record_Date': df_data['entry_date'].iloc[0],
                                     'Indices_Sentiment': price_change_sentiment},ignore_index=True)

            # df_data_indices = df_data_indices.append({'Record_Date': indices_map_data['entry_date'][0],
            #                          'Indices_Sentiment': price_change_sentiment[0]},ignore_index=True)

        indices_vs_sentiment_data = pd.merge(sentiment_data,df_data_indices[['Record_Date','Indices_Sentiment']],
                 on='Record_Date')

        return indices_vs_sentiment_data

    @classmethod
    def get_indices_vs_sentiment_plot_data_v1(cls):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        df_data = pd.DataFrame(columns=['Record_Date','nltk_classify','spacy_count_vectorizer_classify','spacy_tfidf_vectorizer_classify'])
        # df_data_positive = pd.DataFrame(columns=['Record_Date','News_Positive_Sentiment_Count'])
        # df_data_negative = pd.DataFrame(columns=['Record_Date','News_Negative_Sentiment_Count'])
        df_data_indices = pd.DataFrame(columns=['Record_Date','Indices_Sentiment'])

        query=""" SELECT CASE
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' AND position('hours' in LOWER(tdump.timestamp)) > 0
                THEN TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' AND position('ist' in LOWER(tdump.timestamp)) > 0
                THEN TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' AND position('ago' in LOWER(tdump.timestamp)) > 0
                THEN TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                WHEN timestamp IS NOT NULL AND tdump.timestamp !='' THEN TO_DATE(TO_CHAR(timestamp:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy')
                ELSE TO_DATE(TO_CHAR(tdump.entry_time:: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') END AS "record_date",
                tsentiment.nltk_classify,tsentiment.spacy_count_vectorizer_classify,tsentiment.spacy_tfidf_vectorizer_classify
                FROM news_feeds_dump tdump JOIN news_feeds_sentiment tsentiment ON tdump.id = tsentiment.news_id
                WHERE TO_DATE(TO_CHAR(tdump.entry_time :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') >= '2020-03-01' """

        db_cursor.execute(query)
        sentiment_data_list = db_cursor.fetchall()

        for row in sentiment_data_list:
            df_data = df_data.append({'Record_Date': row[0],'nltk_classify':row[1],'spacy_count_vectorizer_classify':row[2],
                                     'spacy_tfidf_vectorizer_classify': row[3]},ignore_index=True)

        df_data['nltk_classify'] = df_data['nltk_classify'].astype(int)
        df_data['spacy_count_vectorizer_classify'] = df_data['spacy_count_vectorizer_classify'].astype(int)
        df_data['spacy_tfidf_vectorizer_classify'] = df_data['spacy_tfidf_vectorizer_classify'].astype(int)
        df_data['Record_Date'] = pd.to_datetime(df_data['Record_Date'])

        df_data['majority_vote'] = df_data.mode(axis=1,numeric_only=True)[0]

        df_postive_sentiment_data = df_data.loc[df_data['majority_vote'] == 1]
        df_negative_sentiment_data = df_data.loc[df_data['majority_vote'] == 0]

        df_postive_group_data = df_postive_sentiment_data.groupby('Record_Date')['majority_vote'].value_counts().reset_index(name="News_Positive_Sentiment_Count")
        df_negative_group_data = df_negative_sentiment_data.groupby('Record_Date')['majority_vote'].value_counts().reset_index(name="News_Negative_Sentiment_Count")

        df_data_positive = df_postive_group_data[['Record_Date','News_Positive_Sentiment_Count']]
        df_data_negative = df_negative_group_data[['Record_Date','News_Negative_Sentiment_Count']]

        # merge sentiment data
        sentiment_data = pd.merge(df_data_positive,df_data_negative[['Record_Date','News_Negative_Sentiment_Count']],
                 on='Record_Date')

        sentiment_data['Day_Sentiment'] = np.where(sentiment_data['News_Positive_Sentiment_Count'] >= sentiment_data['News_Negative_Sentiment_Count'], 1, 0)


        # indices data
        query = """ SELECT DISTINCT ind.index_symbol FROM  indices ind JOIN indices_data idata
                             ON ind.id = idata.index_id ORDER BY index_symbol DESC"""

        db_cursor.execute(query)
        unique_indices_list = db_cursor.fetchall()

        columns = ['entry_date','percent_change']


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

                    select DISTINCT entry_date from temp_table order by entry_date desc; """


        db_cursor.execute(query)
        unique_indices_date = db_cursor.fetchall()

        for row_date in unique_indices_date:

            indices_data_list = []
            for row in unique_indices_list:

                query = """ CREATE TEMPORARY TABLE indices_data_temp
                                (
                                index_id INT,
                                index_name VARCHAR(100) NOT NULL,
                                index_symbol VARCHAR(50) NOT NULL,
                                entry_date DATE,
                                lat VARCHAR(30) NOT NULL,
                                lon VARCHAR(30) NOT NULL,
                                open DECIMAL,
                                adj_close DECIMAL
                                );

                                INSERT INTO indices_data_temp
                                SELECT DISTINCT idata.index_id,ind.country,ind.index_symbol,idata.entry_date,ind.lat,ind.lon,ROUND(idata.open,2) open,ROUND(idata.adj_close,2) adj_close
                                FROM indices ind JOIN indices_data idata ON ind.id = idata.index_id;

                                select idata.entry_date,
                                round(((ROUND(idata.adj_close,2) - lag(ROUND(idata.adj_close,2)) over (order by idata.entry_date, ind.index_symbol))/lag(ROUND(idata.adj_close,2))
                                over (order by idata.entry_date, ind.index_symbol))*100,2) as percent_change
                                FROM indices ind JOIN indices_data_temp idata ON ind.id = idata.index_id WHERE
                                idata.index_symbol = %s AND idata.entry_date <= %s
                                ORDER BY ind.index_symbol,idata.entry_date DESC;"""

                db_cursor.execute(query,(row[0],row_date[0]))
                indices_data = db_cursor.fetchall()
                row_count = db_cursor.rowcount

                if row_count > 0:
                    indices_data_list.append(indices_data[0])

                    indices_map_data = pd.DataFrame(indices_data_list,columns=columns)
                    indices_map_data['percent_change'] = indices_map_data['percent_change'].astype(float)

                    indices_map_data.sort_values(by=['entry_date'], inplace=True, ascending=False)

                query = "drop table indices_data_temp;"
                db_cursor.execute(query)

            price_change_sentiment =  np.where(indices_map_data[["percent_change"]].mean() > 0, 1, 0)

            indices_map_data.sort_values(by=['entry_date'], inplace=True, ascending=False)
            df_data = indices_map_data[indices_map_data['entry_date'] == row_date[0]]

            df_data_indices = df_data_indices.append({'Record_Date': df_data['entry_date'].iloc[0],
                                     'Indices_Sentiment': price_change_sentiment[0]},ignore_index=True)



        indices_vs_sentiment_data = pd.merge(sentiment_data,df_data_indices[['Record_Date','Indices_Sentiment']],
                 on='Record_Date')

        return indices_vs_sentiment_data

    @classmethod
    def get_indices_vs_sentiment_twitter_plot_data(cls):

        db_conn = DBConnection.get_connection()
        db_cursor = db_conn.cursor()

        df_data_positive = pd.DataFrame(columns=['Record_Date','News_Positive_Sentiment_Count'])
        df_data_negative = pd.DataFrame(columns=['Record_Date','News_Negative_Sentiment_Count'])
        df_data_indices = pd.DataFrame(columns=['Record_Date','Indices_Sentiment'])

        query=""" SELECT TO_DATE(TO_CHAR(tweet_date :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') "record_date",COUNT(tsentiment.nltk_classify)
                    FROM twitter_data_dump tdump JOIN twitter_sentiment tsentiment ON tdump.id = tsentiment.tweet_id
                    WHERE TO_DATE(TO_CHAR(tweet_date :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') >= '2020-03-01' AND tsentiment.nltk_classify = 1
                    AND array_length(regexp_split_to_array(tdump.tweet_message, '\s'),1) > 10
                    AND tdump.screen_id in (SELECT DISTINCT screen_id FROM twitter_account WHERE is_active = true
                    and screen_id in('Investingcom','business','markets','FinancialTimes','stevenmnuchin1','Lagarde',
                    'federalreserve','bankofcanada','bankofengland','RBI','ecb','banquedefrance','tsx_tsxv','bse_sensex',
                    'NSEIndia','S&P 500','Nasdaq','DowJones','NikkeiMarket','GTAI_com','CAC_40_Trading'))
                    GROUP BY record_date ORDER BY record_date ASC  """


        # AND tdump.website in ('businessinsider','economic_times')
        db_cursor.execute(query)
        positive_sentiment_data = db_cursor.fetchall()

        data_list = []
        for row in positive_sentiment_data:
            df_data_positive = df_data_positive.append({'Record_Date': row[0],
                                     'News_Positive_Sentiment_Count': row[1]},ignore_index=True)

        df_data_positive['News_Positive_Sentiment_Count'] = df_data_positive['News_Positive_Sentiment_Count'].astype(int)


        query=""" SELECT TO_DATE(TO_CHAR(tweet_date :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') "record_date",COUNT(tsentiment.nltk_classify)
                    FROM twitter_data_dump tdump JOIN twitter_sentiment tsentiment ON tdump.id = tsentiment.tweet_id
                    WHERE TO_DATE(TO_CHAR(tweet_date :: DATE, 'dd/mm/yyyy'),'dd/mm/yyyy') >= '2020-03-01' AND tsentiment.nltk_classify = 0
                    AND array_length(regexp_split_to_array(tdump.tweet_message, '\s'),1) > 10
                    AND tdump.screen_id in (SELECT DISTINCT screen_id FROM twitter_account WHERE is_active = true)
                    GROUP BY record_date ORDER BY record_date ASC  """

        db_cursor.execute(query)
        negative_sentiment_data = db_cursor.fetchall()

        data_list = []
        for row in negative_sentiment_data:
            df_data_negative = df_data_negative.append({'Record_Date': row[0],
                                     'News_Negative_Sentiment_Count': row[1]},ignore_index=True)

        df_data_negative['News_Negative_Sentiment_Count'] = df_data_negative['News_Negative_Sentiment_Count'].astype(int)

        # merge sentiment data
        sentiment_data = pd.merge(df_data_positive,df_data_negative[['Record_Date','News_Negative_Sentiment_Count']],
                 on='Record_Date')

        sentiment_data['Day_Sentiment'] = np.where(sentiment_data['News_Positive_Sentiment_Count'] >= sentiment_data['News_Negative_Sentiment_Count'], 1, 0)


        # indices data
        query = """ SELECT DISTINCT ind.index_symbol FROM  indices ind JOIN indices_data idata
                             ON ind.id = idata.index_id ORDER BY index_symbol DESC"""

        db_cursor.execute(query)
        unique_indices_list = db_cursor.fetchall()

        columns = ['entry_date','percent_change']

        query = """ select DISTINCT entry_date from indices_data order by entry_date desc; """

        db_cursor.execute(query)
        unique_indices_date = db_cursor.fetchall()

        for row_date in unique_indices_date:

            indices_data_list = []
            for row in unique_indices_list:

                query = """ CREATE TEMPORARY TABLE indices_data_temp
                                (
                                index_id INT,
                                index_name VARCHAR(100) NOT NULL,
                                index_symbol VARCHAR(50) NOT NULL,
                                entry_date DATE,
                                lat VARCHAR(30) NOT NULL,
                                lon VARCHAR(30) NOT NULL,
                                open DECIMAL,
                                adj_close DECIMAL
                                );

                                INSERT INTO indices_data_temp
                                SELECT DISTINCT idata.index_id,ind.country,ind.index_symbol,idata.entry_date,ind.lat,ind.lon,ROUND(idata.open,2) open,ROUND(idata.adj_close,2) adj_close
                                FROM indices ind JOIN indices_data idata ON ind.id = idata.index_id;

                                select idata.entry_date,
                                round(((ROUND(idata.adj_close,2) - lag(ROUND(idata.adj_close,2)) over (order by idata.entry_date, ind.index_symbol))/lag(ROUND(idata.adj_close,2))
                                over (order by idata.entry_date, ind.index_symbol))*100,2) as percent_change
                                FROM indices ind JOIN indices_data_temp idata ON ind.id = idata.index_id WHERE
                                idata.index_symbol = %s AND idata.entry_date <= %s
                                ORDER BY ind.index_symbol,idata.entry_date DESC;"""

                db_cursor.execute(query,(row[0],row_date[0]))
                indices_data = db_cursor.fetchall()
                row_count = db_cursor.rowcount

                if row_count > 0:
                    indices_data_list.append(indices_data[0])

                    indices_map_data = pd.DataFrame(indices_data_list,columns=columns)
                    indices_map_data['percent_change'] = indices_map_data['percent_change'].astype(float)

                    indices_map_data.sort_values(by=['entry_date'], inplace=True, ascending=False)

                query = "drop table indices_data_temp;"
                db_cursor.execute(query)

            # price_change_sentiment =  np.where(indices_map_data[["percent_change"]].mean() > 0, 1, 0)

            seriesObj = indices_map_data.apply(lambda x: True if x['percent_change'] >= 0 else False , axis=1)
            numOfRows = len(seriesObj[seriesObj == True].index)
            numOfRows1 = len(seriesObj[seriesObj == False].index)

            price_change_sentiment = 0
            if numOfRows >= numOfRows1:
                price_change_sentiment = 1

            indices_map_data.sort_values(by=['entry_date'], inplace=True, ascending=False)
            df_data = indices_map_data[indices_map_data['entry_date'] == row_date[0]]

            df_data_indices = df_data_indices.append({'Record_Date': df_data['entry_date'].iloc[0],
                                     'Indices_Sentiment': price_change_sentiment},ignore_index=True)

            # df_data_indices = df_data_indices.append({'Record_Date': indices_map_data['entry_date'][0],
            #                          'Indices_Sentiment': price_change_sentiment[0]},ignore_index=True)

        indices_vs_sentiment_data = pd.merge(sentiment_data,df_data_indices[['Record_Date','Indices_Sentiment']],
                 on='Record_Date')

        return indices_vs_sentiment_data
