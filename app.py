from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort,url_for,jsonify,Response,make_response,current_app
import os
import psycopg2
import re
from flask import Flask
from flask_bcrypt import Bcrypt

# start - import user define model
from users_model import User
from common_data_model import CommonData
from setting_model import SettingModel
from indices_model import IndicesModel
from index_model import IndexPageModel
from index_india_model import IndexIndiaPageModel
from report_twitter_model import ReportModel
from report_news_model import ReportNewsModel
from flask_pager import Pager
# end

# report package
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly
import plotly.graph_objs as go
import plotly.express as px
# end report package

import itertools
import random
import time

# normailze package
import scipy
from sklearn import preprocessing

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(42)
app.config['PAGE_SIZE'] = 6
app.config['VISIBLE_PAGE_COUNT'] = 10


@app.route("/")
def index():

    session['logged_in'] = True
    if session.get('logged_in'):
        # get map data
        indices_data = IndexPageModel.get_indices_data()
        return render_template('index.html',indices_data=indices_data)
    else:
        return render_template('login.html')


@app.route("/index_India")
def index_India():
    session['logged_in'] = True
    if session.get('logged_in'):
        indices_data = IndexIndiaPageModel.get_indices_data()
        return render_template('index_india.html',indices_data=indices_data)
    else:
        return render_template('login.html')


@app.route('/twitter_daily_sentiment_plot', methods=['GET', 'POST'])
def twitter_daily_sentiment_plot():

    feature = request.args['selected']
    graphJSON= create_twitter_daily_sentiment_plot(feature, "twitter")

    return graphJSON


def create_twitter_daily_sentiment_plot(feature, data_type):

    if feature == 'Bar':

        labels,values,colors =  get_sentiment_historical_data(data_type,1) # positive

        colors.append('#28a745')
        trace1 = go.Bar(
            x=labels,
            y=values,
            name='Positive',
            marker=dict(
                color='rgb(40,167,69)',
                line=dict(
                    color='rgb(8,48,107)'),
            )
        )

        labels,values,colors =  get_sentiment_historical_data(data_type,0) # negative
        trace2 = go.Bar(
            x=labels,
            y=values,
            name='Negative',
            marker=dict(
                color='rgb(220,53,69)',
                line=dict(
                    color='rgb(8,48,107)'),

            )

        )
        data = [trace1, trace2]

    else:
        N = 1000
        random_x = np.random.randn(N)
        random_y = np.random.randn(N)

        # Create a trace
        data = [go.Scatter(
            x = random_x,
            y = random_y,
            mode = 'markers'
        )]


    layout = go.Layout(
        xaxis=dict(tickangle=-45),
        barmode='group',
        legend_orientation="h",
        legend=dict(x=.4, y=1.2)
    )

    fig = go.Figure(data=data, layout=layout)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/news_daily_sentiment_plot', methods=['GET', 'POST'])
def news_daily_sentiment_plot():

    feature = request.args['selected']
    graphJSON= create_news_daily_sentiment_plot(feature, "news")

    return graphJSON


def create_news_daily_sentiment_plot(feature, data_type):

    if feature == 'Bar':

        labels,values,colors =  get_sentiment_historical_data(data_type,1) # positive

        colors.append('#28a745')
        trace1 = go.Bar(
            x=labels,
            y=values,
            name='Positive',
            marker=dict(
                color='rgb(40,167,69)',
                line=dict(
                    color='rgb(8,48,107)'),
            )
        )

        labels,values,colors =  get_sentiment_historical_data(data_type,0) # negative
        trace2 = go.Bar(
            x=labels,
            y=values,
            name='Negative',
            marker=dict(
                color='rgb(220,53,69)',
                line=dict(
                    color='rgb(8,48,107)'),

            )

        )
        data = [trace1, trace2]

    else:
        N = 1000
        random_x = np.random.randn(N)
        random_y = np.random.randn(N)

        # Create a trace
        data = [go.Scatter(
            x = random_x,
            y = random_y,
            mode = 'markers'
        )]


    layout = go.Layout(
        xaxis=dict(tickangle=-45),
        barmode='group',
        legend_orientation="h",
        legend=dict(x=.4, y=1.2)
    )

    fig = go.Figure(data=data, layout=layout)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def get_sentiment_historical_data(data_type,sentiment_type=0):

    labels = []
    values = []
    colors = []

    if data_type == "twitter":
        records  = IndexPageModel.get_twitter_plot_data(sentiment_type)

        for item in records:
            labels.append(item[0])
            values.append(item[1])

    elif data_type == "news":
        records  = IndexPageModel.get_news_plot_data(sentiment_type)

        for item in records:
            labels.append(item[0])
            values.append(item[1])

    return labels,values,colors

@app.route('/get_india_indices_vs_sentiment_plot', methods=['GET', 'POST'])
def get_india_indices_vs_sentiment_plot():

    feature = request.args['selected']
    graphJSON = create_indices_vs_sentiment_plot('Bar','india')

    return graphJSON


@app.route('/get_indices_vs_sentiment_plot', methods=['GET', 'POST'])
def get_indices_vs_sentiment_plot():

    feature = request.args['selected']
    graphJSON = create_indices_vs_sentiment_plot('Bar','world')

    return graphJSON

def create_indices_vs_sentiment_plot(feature,region):

    if feature == 'Bar':

        labels,values,colors,sentiment_data =  get_indices_vs_sentiment_plot_data("News_Day_Sentiment",region)

        colors.append('#28a745')
        trace1 = go.Scatter(
            x=labels,
            y=values,
            name='Daily Sentiment',
            mode='lines+markers',
            # mode='markers',
            # hoverinfo='name',
            hovertext=sentiment_data,
            opacity=1,
            line=dict(
                shape='hv',
                width=1,
            ),
            marker=dict(
                size=10,
                color='#17a2b8',
                line=dict(
                    color='rgb(8,48,107)'),
            )
        )

        labels,values,colors,sentiment_data =  get_indices_vs_sentiment_plot_data("Indices_Sentiment",region)
        trace2 = go.Scatter(
            x=labels,
            y=values,
            name='Composite Indices Move',
            mode='markers',
            opacity=0.3,
            line=dict(
                shape='hv',
                width=6,
                dash='dash'
            ),
            marker=dict(
                size=25,
                color='rgb(220,53,69)',
                line=dict(
                    width=2,
                    color='red'
                )
            )
        )
        data = [trace1, trace2]


    layout = go.Layout(
        xaxis=dict(tickangle=-45),
        barmode='group',
        legend_orientation="h",
        legend=dict(x=.4, y=1.2)
    )

    fig = go.Figure(data=data, layout=layout)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def get_indices_vs_sentiment_plot_data(data_type,region):

    labels = []
    values = []
    colors = []
    sentiment_data = []

    if region == "world":
        records  = IndexPageModel.get_indices_vs_sentiment_plot_data()
    elif region == "india":
        records  = IndexIndiaPageModel.get_indices_vs_sentiment_plot_data() 

    if data_type == "News_Day_Sentiment":

        for row in records.itertuples(index=False):
            labels.append(row.Record_Date)
            values.append(row.Day_Sentiment)
            sentiment_data.append("(+"+str(row.News_Positive_Sentiment_Count) + ",-" + str(row.News_Negative_Sentiment_Count) +")")


    elif data_type == "Indices_Sentiment":

        for row in records.itertuples(index=False):
            labels.append(row.Record_Date)
            values.append(row.Indices_Sentiment)

    return labels,values,colors,sentiment_data


@app.route('/get_indices_vs_twitter_sentiment_plot', methods=['GET', 'POST'])
def get_indices_vs_twitter_sentiment_plot():

    feature = request.args['selected']
    graphJSON = create_indices_vs_twitter_sentiment_plot('Bar')

    return graphJSON

def create_indices_vs_twitter_sentiment_plot(feature):

    if feature == 'Bar':

        labels,values,colors,sentiment_data =  get_indices_vs_twitter_sentiment_plot_data("Twitter_Day_Sentiment")

        colors.append('#28a745')
        trace1 = go.Scatter(
            x=labels,
            y=values,
            name='Twitter Daily Sentiment',
            mode='lines+markers',
            # mode='markers',
            # hoverinfo='name',
            hovertext=sentiment_data,
            opacity=1,
            line=dict(
                shape='hv',
                width=1,
            ),
            marker=dict(
                size=10,
                color='#17a2b8',
                line=dict(
                    color='rgb(8,48,107)'),
            )
        )

        labels,values,colors,sentiment_data =  get_indices_vs_twitter_sentiment_plot_data("Indices_Sentiment")
        trace2 = go.Scatter(
            x=labels,
            y=values,
            name='Composite Indices Move',
            mode='markers',
            opacity=0.3,
            line=dict(
                shape='hv',
                width=6,
                dash='dash'
            ),
            marker=dict(
                size=25,
                color='rgb(220,53,69)',
                line=dict(
                    width=2,
                    color='red'
                )
            )
        )
        data = [trace1, trace2]


    layout = go.Layout(
        xaxis=dict(tickangle=-45),
        barmode='group',
        legend_orientation="h",
        legend=dict(x=.4, y=1.2)
    )

    fig = go.Figure(data=data, layout=layout)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def get_indices_vs_twitter_sentiment_plot_data(data_type):

    labels = []
    values = []
    colors = []
    sentiment_data = []

    records  = IndexPageModel.get_indices_vs_sentiment_twitter_plot_data()
    # records  = IndexPageModel.get_indices_vs_sentiment_plot_data_v1()

    if data_type == "Twitter_Day_Sentiment":

        for row in records.itertuples(index=False):
            labels.append(row.Record_Date)
            values.append(row.Day_Sentiment)
            sentiment_data.append("(+"+str(row.News_Positive_Sentiment_Count) + ",-" + str(row.News_Negative_Sentiment_Count) +")")


    elif data_type == "Indices_Sentiment":

        for row in records.itertuples(index=False):
            labels.append(row.Record_Date)
            values.append(row.Indices_Sentiment)

    return labels,values,colors,sentiment_data


@app.route("/contact", methods=['GET', 'POST'])
def contact():

    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'message' in request.form:

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        message = request.form['message']

        result = CommonData(first_name,last_name,email,message).save_user_message()

        if result <= 0:
            msg = 'Error occurred, please try again.'
            return render_template("contact.html", msg=msg)
        else:
            msg = 'Thank you for your message we will contact you shortly.'
            return render_template("contact.html", msg=msg)

    return render_template("contact.html")


@app.route("/about")
def about():
    return render_template("about.html")



@app.route("/login", methods=['GET', 'POST'])
def login():

    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']

        # verify user
        account = User.verify_user(email, password)

        if account:
            # Create session data
            session['logged_in'] = True
            session['user_name'] = account[1]
            session['user_id'] = account[4]
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            return render_template("login.html", msg=msg)

    return render_template("login.html", msg='')


@app.route("/signup", methods=['GET', 'POST'])
def signup():

    msg = ''
    if request.method == 'POST' and 'first_name' in request.form and 'email' in request.form and 'password' in request.form:

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        result = User(first_name,last_name,email,password).create_account()

        if result <= 0:
            msg = 'Registration failed, please try again.'
            return render_template("signup.html", msg=msg)
        else:
            return redirect(url_for('login'))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    session.pop('user_name', None)
    session.pop('user_id', None)
    # session.pop('twitter_filter_type',None)
    return redirect(url_for('login'))


@app.route("/profile")
def profile():
    session['logged_in'] = True
    if session.get('logged_in'):

        user_details = User.get_user_details(session.get('user_id'))

        return render_template('profile.html', user_details=user_details)

    else:
        return redirect(url_for('login'))


# report routing

# tweets insight report and plot
def get_plot_data(feature,type=0):

    sentiment_type_id = 2
    if session.get('twitter_filter_type'):
        sentiment_type_id = session.get('twitter_filter_type')

    labels = []
    values = []
    colors = []

    if feature == "Pie":

        records  = ReportModel.get_twitter_pie_plot_data(sentiment_type_id,session.get('user_id'))

        for item in records:
            labels.append(item[0])
            values.append(item[1])

        for item in labels:
            if item == 'Positive':
                colors.append('#28a745')
            elif item == 'Negative':
                colors.append('#dc3545')
            else:
                colors.append('#E1396C')

        return labels,values,colors

    elif feature == "Bar":
        records  = ReportModel.get_twitter_bar_plot_data(sentiment_type_id,session.get('user_id'),type)

        for item in records:
            labels.append(item[0])
            values.append(item[1])

        return labels,values,colors

def create_twitter_plot(feature):

    if feature == 'Bar':

        labels,values,colors =  get_plot_data(feature,1) # positive

        colors.append('#28a745')
        trace1 = go.Bar(
            x=labels,
            y=values,
            name='Positive',
            marker=dict(
                color='rgb(40,167,69)',
                line=dict(
                    color='rgb(8,48,107)'),
            )
        )

        labels,values,colors =  get_plot_data(feature,0) # negative
        trace2 = go.Bar(
            x=labels,
            y=values,
            name='Negative',
            marker=dict(
                color='rgb(220,53,69)',
                line=dict(
                    color='rgb(8,48,107)'),
            )
        )
        data = [trace1, trace2]

        layout = go.Layout(
            barmode='group',
        )

        fig = go.Figure(data=data, layout=layout)

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON

    elif feature == 'Pie':

        labels,values,colors =  get_plot_data(feature)

        data = [
                go.Pie(labels=labels, values=values,
                marker=dict(colors=colors))
            ]

        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON
    else:
        N = 1000
        random_x = np.random.randn(N)
        random_y = np.random.randn(N)

        # Create a trace
        data = [go.Scatter(
            x = random_x,
            y = random_y,
            mode = 'markers'
        )]


        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON

@app.route("/twitter_report_index", methods=['GET', 'POST'])
def twitter_report_index():

    session['logged_in'] = True

    if session.get('logged_in'):
        # 0- negative, 1- postive, 2 - neutral
        sentiment_type_id = 1

        if request.method == 'POST' and 'click_button_id' in request.form:
            sentiment_type_id = request.form['click_button_id']
            session['twitter_filter_type'] = sentiment_type_id

        if session.get('twitter_filter_type'):
            sentiment_type_id = session.get('twitter_filter_type')

        page = int(request.args.get('page', 1))
        count =  ReportModel.get_twitter_article_count(sentiment_type_id,session.get('user_id'))[0][0]


        if count == 0:
            msg = 'No records found.'
            return render_template('reports/twitter_report_index.html',msg=msg)
        else:
            bar = create_twitter_plot("Pie")

            data = range(count)
            pager = Pager(page, count)
            pages = pager.get_pages()
            offset = (page - 1) * current_app.config['PAGE_SIZE']
            limit = current_app.config['PAGE_SIZE']
            twitter_news_records = ReportModel.get_twitter_article(limit,offset,sentiment_type_id,session.get('user_id'))
            return render_template('reports/twitter_report_index.html', pages=pages,
                    twitter_news_records=twitter_news_records, plot=bar)

    else:
        return redirect(url_for('login'))

@app.route("/twitter_report_update")
def twitter_report_update():
    session['logged_in'] = True
    if session.get('logged_in'):
        last_record_id = request.args.get("last_record_id")

        sentiment_type_id = 2

        if session.get('twitter_filter_type'):
            sentiment_type_id = session.get('twitter_filter_type')

        latest_twitter_records = ReportModel.get_latest_twitter_article(last_record_id,sentiment_type_id,session.get('user_id'))
        return jsonify(json_list=latest_twitter_records)
    else:
        return redirect(url_for('login'))

@app.route('/twitter_plot', methods=['GET', 'POST'])
def change_twitter_features():

    feature = request.args['selected']
    graphJSON= create_twitter_plot(feature)

    return graphJSON

# end insight report and plot

# start insight news report and plot

@app.route("/news_report_index", methods=['GET', 'POST'])
def news_report_index():
    session['logged_in'] = True
    if session.get('logged_in'):
        # 0- negative, 1- postive, 2 - neutral
        sentiment_type_id = 2

        if request.method == 'POST' and 'click_button_id' in request.form:
            sentiment_type_id = request.form['click_button_id']
            session['news_filter_type'] = sentiment_type_id

        if session.get('news_filter_type'):
            sentiment_type_id = session.get('news_filter_type')

        page = int(request.args.get('page', 1))
        count = ReportNewsModel.get_news_article_count(sentiment_type_id,session.get('user_id'))[0][0]

        if count == 0:
            msg = 'No records found.'
            return render_template('reports/news_report_index.html',msg=msg)
        else:
            bar = create_news_plot("Pie")

            data = range(count)
            pager = Pager(page, count)
            pages = pager.get_pages()
            offset = (page - 1) * current_app.config['PAGE_SIZE']
            limit = current_app.config['PAGE_SIZE']

            news_records =  ReportNewsModel.get_news_article(limit,offset,sentiment_type_id,session.get('user_id'))
            return render_template('reports/news_report_index.html', pages=pages,
                    news_records=news_records, plot=bar)

    else:
        return redirect(url_for('login'))

@app.route("/news_report_update")
def news_report_update():
    session['logged_in'] = True
    if session.get('logged_in'):
        last_record_id = request.args.get("last_record_id")

        sentiment_type_id = 2

        if session.get('news_filter_type'):
            sentiment_type_id = session.get('news_filter_type')

        latest_news_records = ReportNewsModel.get_latest_news_article(last_record_id,sentiment_type_id,session.get('user_id'))
        return jsonify(json_list=latest_news_records)
    else:
        return redirect(url_for('login'))

@app.route('/news_plot_change', methods=['GET', 'POST'])
def change_news_features():

    feature = request.args['selected']
    graphJSON= create_news_plot(feature)

    return graphJSON

def get_news_plot_data(feature,type=0):

    sentiment_type_id = 2
    if session.get('news_filter_type'):
        sentiment_type_id = session.get('news_filter_type')

    labels = []
    values = []
    colors = []

    if feature == "Pie":

        records  = ReportNewsModel.get_news_pie_plot_data(sentiment_type_id,session.get('user_id'))

        for item in records:
            labels.append(item[0])
            values.append(item[1])

        for item in labels:
            if item == 'Positive':
                colors.append('#28a745')
            elif item == 'Negative':
                colors.append('#dc3545')
            else:
                colors.append('#E1396C')

        return labels,values,colors

    elif feature == "Bar":
        records  = ReportNewsModel.get_news_bar_plot_data(sentiment_type_id,session.get('user_id'),type)

        for item in records:
            labels.append(item[0])
            values.append(item[1])

        return labels,values,colors

def create_news_plot(feature):

    if feature == 'Bar':
        labels,values,colors =  get_news_plot_data(feature,1) # positive

        colors.append('#28a745')
        trace1 = go.Bar(
            x=labels,
            y=values,
            name='Positive',
            marker=dict(
                color='rgb(40,167,69)',
                line=dict(
                    color='rgb(8,48,107)'),
            )
        )

        labels,values,colors =  get_news_plot_data(feature,0) # negative
        trace2 = go.Bar(
            x=labels,
            y=values,
            name='Negative',
            marker=dict(
                color='rgb(220,53,69)',
                line=dict(
                    color='rgb(8,48,107)'),
            )
        )
        data = [trace1,trace2]

    elif feature == 'Pie':

        labels,values,colors =  get_news_plot_data(feature)

        data = [
                go.Pie(labels=labels, values=values,
                marker=dict(colors=colors))
            ]
    else:
        N = 1000
        random_x = np.random.randn(N)
        random_y = np.random.randn(N)

        # Create a trace
        data = [go.Scatter(
            x = random_x,
            y = random_y,
            mode = 'markers'
        )]


    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

# end insight news report

# start Indices plot

@app.route("/indices")
def indices():
    session['logged_in'] = True
    if session.get('logged_in'):
        bar = create_indices_plot("Scatter")
        # get unique indices
        records_list = IndicesModel.get_indices()

        # get pre selected indices list
        selected_indices = User.get_user_session_data(session.get('user_id'),"selected_indices")
        selected_indices_list = ""
        if selected_indices is not None and len(selected_indices) > 0:
            selected_indices_list = selected_indices[0]

        return render_template('reports/indices.html',plot=bar,
                    unique_indices=records_list, selected_indices_list = selected_indices_list)
    else:
        return redirect(url_for('login'))

def get_indices_data(feature):

    labels = []
    values = []
    # colors = []

    if feature == "Line" or feature == "Scatter" or feature == "Line_Bar" or feature == "Bar" :

        df_indices_data  = IndicesModel.get_indices_plot_data(session.get('user_id'))

        return df_indices_data

@app.route('/indices_plot', methods=['GET', 'POST'])
def change_indices_type():

    selected_indices = request.args['selected_indices']
    plot_type = request.args['plot_type']
    User.set_user_session_data(session.get('user_id'),"selected_indices",selected_indices)
    graphJSON = create_indices_plot(plot_type)

    return graphJSON

@app.route('/filter_indices_plot', methods=['GET', 'POST'])
def change_indices_plot():

    feature = request.args['selected']
    graphJSON = create_indices_plot(feature)

    return graphJSON

def create_indices_plot(feature):

    # Create figure
    fig = go.Figure()

    if feature == "Line":

        labels = []
        indices = []
        color = ""

        df_indices_data = get_indices_data(feature)

        for index, row in df_indices_data.iterrows():
            indices.append(row["index_symbol"])

        unique_indices = list(set(indices))

        data_df = pd.DataFrame()
        column_name = []
        for item in unique_indices:
            filter_df = df_indices_data[df_indices_data['index_symbol']==item]
            filter_df.sort_values(by=['entry_date'], inplace=True)
            filter_df = filter_df[['adj_close']]
            col_name = "adj_close_"+item
            column_name.append(col_name)
            data_df[col_name] = filter_df['adj_close'].values

        scaler = preprocessing.MinMaxScaler()
        scaled_df = scaler.fit_transform(data_df)
        scaled_df = pd.DataFrame(scaled_df, columns=column_name)

        i = 1
        for item in unique_indices:
            filter_df = df_indices_data[df_indices_data['index_symbol']==item]
            col_name = "adj_close_"+item
            values = scaled_df[col_name].tolist()

            labels.clear()

            for ind in filter_df.index:
                labels.append(filter_df['entry_date'][ind])

            if i == 1:
                color = "#673ab7"
            elif i == 2:
                color = "#E91E63"
            elif i == 3:
                color = "#795548"
            elif i == 4:
                color = "#607d8b"
            elif i == 5:
                color = "#2196F3"

            fig.add_trace(
                go.Scatter(
                    x=labels,
                    y=values,
                    name=item,
                    text=values,
            ))

            i += 1

        # Set title
        fig.update_layout(
            # title_text="Time series with range slider and selectors"
            dragmode="zoom",
            hovermode="x",
            legend=dict(traceorder="reversed"),
            # height=600,
            template="plotly_white",
            margin=dict(
                t=50,
                b=30
            ),
            legend_title='<b> Indices </b>'
        )

    elif feature == "Scatter":

        df_indices_data = get_indices_data(feature)

        label_1,label_2,label_3,label_4,label_5,label_6 = ([] for i in range(6))
        value_1,value_2,value_3,value_4,value_5,value_6 = ([] for i in range(6))
        indices = []

        # Normalize a dataset by dividing each data point by a constant, such as the standard deviation of the data
        data_norm_by_std = [number/scipy.std(df_indices_data["adj_close"]) for number in df_indices_data["adj_close"]]

        # add new normalize column
        df_indices_data['adj_close_std'] = data_norm_by_std

        # get unique indices list
        for index, row in df_indices_data.iterrows():
            indices.append(row["index_symbol"])

        unique_indices = list(set(indices))

        i = 1
        # Create figure
        # fig = go.Figure()

        for item in unique_indices:
            filter_df = df_indices_data[df_indices_data['index_symbol']==item]
            filter_df.sort_values(by=['entry_date'], ascending=True)

            if i == 1:
                for ind in filter_df.index:
                    label_1.append(filter_df['entry_date'][ind])
                    value_1.append(filter_df['adj_close'][ind])

                # Add traces
                fig.add_trace(go.Scatter(
                        x=label_1,
                        y=value_1,
                        name=item,
                        text=value_1,
                        yaxis="y",
                ))

            elif i == 2:
                for ind in filter_df.index:
                    label_2.append(filter_df['entry_date'][ind])
                    value_2.append(filter_df['adj_close'][ind])

                # Add traces
                fig.add_trace(go.Scatter(
                        x=label_2,
                        y=value_2,
                        name=item,
                        text=value_2,
                        yaxis="y2",
                ))
            elif i == 3:
                for ind in filter_df.index:
                    label_3.append(filter_df['entry_date'][ind])
                    value_3.append(filter_df['adj_close'][ind])

                # Add traces
                fig.add_trace(go.Scatter(
                        x=label_3,
                        y=value_3,
                        name=item,
                        text=value_3,
                        yaxis="y3",
                ))
            elif i == 4:
                for ind in filter_df.index:
                    label_4.append(filter_df['entry_date'][ind])
                    value_4.append(filter_df['adj_close'][ind])

                # Add traces
                fig.add_trace(go.Scatter(
                        x=label_4,
                        y=value_4,
                        name=item,
                        text=value_4,
                        yaxis="y4",
                ))

            i +=1

        # fig.add_trace(go.Scatter(
        #     x=["2013-01-29", "2013-02-26", "2013-04-19", "2013-07-02", "2013-08-27",
        #        "2013-10-22",
        #        "2014-01-20", "2014-04-09", "2014-05-05", "2014-07-01", "2014-09-30",
        #        "2015-02-09",
        #        "2015-04-13", "2015-06-08", "2016-02-25"],
        #     y=["6.9", "7.5", "7.3", "7.3", "6.9", "7.1", "8", "7.8", "7.4", "7.9", "7.9", "7.6",
        #        "7.2", "7.2", "8.0"],
        #     name="var3",
        #     text=["6.9", "7.5", "7.3", "7.3", "6.9", "7.1", "8", "7.8", "7.4", "7.9", "7.9",
        #           "7.6",
        #           "7.2", "7.2", "8.0"],
        #     yaxis="y4",
        # ))

        # fig.add_trace(go.Scatter(
        #     x=["2013-02-26", "2013-07-02", "2013-09-26", "2013-10-22", "2013-12-04",
        #        "2014-01-02",
        #        "2014-01-20", "2014-05-05", "2014-07-01", "2015-02-09", "2015-05-05"],
        #     y=["290", "1078", "263", "407", "660", "740", "33", "374", "95", "734", "3000"],
        #     name="var4",
        #     text=["290", "1078", "263", "407", "660", "740", "33", "374", "95", "734", "3000"],
        #     yaxis="y5",
        # ))

        # style all the traces
        fig.update_traces(
            hoverinfo="name+x+text",
            line={"width": 0.5},
            marker={"size": 8},
            mode="lines+markers",
            showlegend=True
        )

        # Update axes
        fig.update_layout(
            yaxis=dict(
                anchor="x",
                autorange=True,
                domain=[0, 0.2],
                linecolor="#673ab7",
                mirror=True,
                # range=[-60.0858369099, 28.4406294707],
                showline=True,
                # side="right",
                tickfont={"color": "#673ab7"},
                tickmode="auto",
                ticks="",
                titlefont={"color": "#673ab7"},
                type="linear",
                zeroline=False
            ),
            yaxis2=dict(
                anchor="x",
                autorange=True,
                domain=[0.2, 0.4],
                linecolor="#E91E63",
                mirror=True,
                # range=[29.3787777032, 100.621222297],
                showline=True,
                side="right",
                tickfont={"color": "#E91E63"},
                tickmode="auto",
                ticks="",
                titlefont={"color": "#E91E63"},
                type="linear",
                zeroline=False
            ),
            yaxis3=dict(
                anchor="x",
                autorange=True,
                domain=[0.4, 0.6],
                linecolor="#795548",
                mirror=True,
                # range=[-3.73690396239, 22.2369039624],
                showline=True,
                # side="right",
                tickfont={"color": "#795548"},
                tickmode="auto",
                # ticks="",
                # title="",
                titlefont={"color": "#795548"},
                type="linear",
                zeroline=False
            ),
            yaxis4=dict(
                anchor="x",
                autorange=True,
                domain=[0.6, 0.8],
                linecolor="#607d8b",
                mirror=True,
                # # range=[6.63368032236, 8.26631967764],
                # showline=True,
                # side="right",
                # tickfont={"color": "#607d8b"},
                # tickmode="auto",
                # ticks="",
                # title="",
                # titlefont={"color": "#607d8b"},
                # type="linear",
                # zeroline=False
            ),
            # yaxis5=dict(
            #     anchor="x",
            #     autorange=True,
            #     domain=[0.8, 1],
            #     linecolor="#2196F3",
            #     mirror=True,
            #     range=[-685.336803224, 3718.33680322],
            #     showline=True,
            #     side="right",
            #     tickfont={"color": "#2196F3"},
            #     tickmode="auto",
            #     ticks="",
            #     title="mg/Kg",
            #     titlefont={"color": "#2196F3"},
            #     type="linear",
            #     zeroline=False
            # )
        )

        # Update layout
        fig.update_layout(
            dragmode="zoom",
            hovermode="x",
            legend=dict(traceorder="reversed"),
            # height=600,
            template="plotly_white",
            margin=dict(
                t=50,
                b=30
            ),
            legend_title='<b> Indices </b>'
        )
    elif feature == "Line_Bar":

        labels = []
        indices = []
        color = ""

        df_indices_data = get_indices_data(feature)

        for index, row in df_indices_data.iterrows():
            indices.append(row["index_symbol"])

        unique_indices = list(set(indices))

        data_df = pd.DataFrame()
        column_name = []

        for item in unique_indices:
            filter_df = df_indices_data[df_indices_data['index_symbol']==item]
            filter_df = filter_df[['adj_close']]
            col_name = "adj_close_"+item
            column_name.append(col_name)
            data_df[col_name] = filter_df['adj_close'].values

        scaler = preprocessing.MinMaxScaler()
        scaled_df = scaler.fit_transform(data_df)
        scaled_df = pd.DataFrame(scaled_df, columns=column_name)

        i = 1
        for item in unique_indices:
            filter_df = df_indices_data[df_indices_data['index_symbol']==item]
            col_name = "adj_close_"+item
            values = scaled_df[col_name].tolist()

            labels.clear()

            for ind in filter_df.index:
                labels.append(filter_df['entry_date'][ind])

            if i == 1:
                color = "#673ab7"
            elif i == 2:
                color = "#E91E63"
            elif i == 3:
                color = "#795548"
            elif i == 4:
                color = "#607d8b"
            elif i == 5:
                color = "#2196F3"

            fig.add_trace(go.Bar(
                 x=labels,
                 y=values,
                 name=item,
                 marker=dict(
                     color=color,
                     line=dict(
                         color=color),
                 )
            ))
            fig.add_trace(
                go.Scatter(
                    x=labels,
                    y=values,
                    name=item,
                    text=values,
            ))

            i += 1

        # Set title
        fig.update_layout(
            # title_text="Time series with range slider and selectors"
            dragmode="zoom",
            hovermode="x",
            legend=dict(traceorder="reversed"),
            # height=600,
            template="plotly_white",
            margin=dict(
                t=50,
                b=30
            ),
            legend_title='<b> Indices </b>'
        )
    elif feature == "Bar":

        labels = []
        indices = []
        color = ""

        df_indices_data = get_indices_data(feature)

        for index, row in df_indices_data.iterrows():
            indices.append(row["index_symbol"])

        unique_indices = list(set(indices))

        data_df = pd.DataFrame()
        column_name = []

        for item in unique_indices:
            filter_df = df_indices_data[df_indices_data['index_symbol']==item]
            filter_df = filter_df[['adj_close']]
            col_name = "adj_close_"+item
            column_name.append(col_name)
            data_df[col_name] = filter_df['adj_close'].values

        scaler = preprocessing.MinMaxScaler()
        scaled_df = scaler.fit_transform(data_df)
        scaled_df = pd.DataFrame(scaled_df, columns=column_name)

        i = 1
        for item in unique_indices:
            filter_df = df_indices_data[df_indices_data['index_symbol']==item]
            col_name = "adj_close_"+item
            values = scaled_df[col_name].tolist()

            labels.clear()
            for ind in filter_df.index:
                labels.append(filter_df['entry_date'][ind])

            if i == 1:
                color = "#673ab7"
            elif i == 2:
                color = "#E91E63"
            elif i == 3:
                color = "#795548"
            elif i == 4:
                color = "#607d8b"
            elif i == 5:
                color = "#2196F3"

            fig.add_trace(go.Bar(
                 x=labels,
                 y=values,
                 name=item,
                 marker=dict(
                     color=color,
                     line=dict(
                         color=color),
                 )
            ))

            i += 1

        # Set title
        fig.update_layout(
            # title_text="Time series with range slider and selectors"
            dragmode="zoom",
            hovermode="x",
            legend=dict(traceorder="reversed"),
            # height=600,
            template="plotly_white",
            margin=dict(
                t=50,
                b=30
            ),
            legend_title='<b> Indices </b>'
        )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
# end indices plot


@app.route("/test")
def test():
    bar = create_news_plot("Line")
    return render_template('test.html',plot=bar)

@app.route("/test1")
def test1():
    return render_template('test1.html')


# Setting page

@app.route("/twitter_box")
def twitter_box():
    session['logged_in'] = True
    if session.get('logged_in'):

        # twitter
        twitter_records = SettingModel.get_twitter_account(session.get('user_id'))

        return render_template('setting/_twitter_box.html', twitter_records=twitter_records)
    else:
        return redirect(url_for('login'))

@app.route("/add_twitter_account", methods=['GET', 'POST'])
def add_twitter_account():
    session['logged_in'] = True
    if session.get('logged_in'):

        msg = ''
        if request.method == 'POST' and 'twitter_account' in request.form:

            screen_id = request.form['twitter_account']

            result =  SettingModel.add_twitter_account(screen_id)

            if result <= 0:
                msg = 'Error occured, please try again.'
                return render_template("setting/_twitter_box.html", msg=msg)
            else:
                return redirect(url_for('twitter_box'))

        return redirect(url_for('twitter_box'))

    else:
        return redirect(url_for('login'))

@app.route("/map_user_twitter_list", methods=['GET', 'POST'])
def map_user_twitter_list():
    session['logged_in'] = True
    if session.get('logged_in'):

        selected_twitter_account = request.form.getlist("twitter_screen_id")

        if len(selected_twitter_account) > 0:

            result =  SettingModel.map_twitter_account(selected_twitter_account,session.get('user_id'))

            if result <= 0:
                msg = 'Error occured, please try again.'
                return render_template("setting/_twitter_box.html", msg=msg)
            else:
                return redirect(url_for('twitter_box'))
        elif len(selected_twitter_account) <= 0:
            result =  SettingModel.map_twitter_account(selected_twitter_account,session.get('user_id'))
        else:
            msg = 'Select list of twitter account to track.'
            return render_template("setting/_twitter_box.html", msg=msg)

        return redirect(url_for('twitter_box'))
    else:
        return redirect(url_for('login'))

# website template route

@app.route("/news_site_box")
def news_site_box():
    session['logged_in'] = True
    if session.get('logged_in'):

        # news
        news_web_records = SettingModel.get_website_urls(session.get('user_id'))
        monitor_webiste_records = SettingModel.get_monitor_newssite(session.get('user_id'))

        return render_template('setting/_news_site_box.html', news_web_records=news_web_records,
            monitor_webiste_records = monitor_webiste_records)
    else:
        return redirect(url_for('login'))

@app.route("/add_website_url", methods=['GET', 'POST'])
def add_website_url():
    session['logged_in'] = True
    if session.get('logged_in'):

        msg = ''
        if request.method == 'POST' and 'website_url' in request.form:

            website_url = request.form['website_url']

            result =  SettingModel.add_website_url(website_url,session.get('user_id'))

            if result <= 0:
                msg = 'Error occured, please try again.'
                return render_template("setting/_news_site_box.html", msg=msg)
            else:
                return redirect(url_for('news_site_box'))

        return redirect(url_for('news_site_box'))

    else:
        return redirect(url_for('login'))

@app.route("/map_user_website_list", methods=['GET', 'POST'])
def map_user_website_list():
    session['logged_in'] = True
    if session.get('logged_in'):

        selected_website_url = request.form.getlist("webiste_url_id")

        if len(selected_website_url) > 0:

            result =  SettingModel.map_user_website(selected_website_url,session.get('user_id'))

            if result <= 0:
                msg = 'Error occured, please try again.'
                return render_template("setting/_news_site_box.html", msg=msg)
            else:
                return redirect(url_for('news_site_box'))
        elif len(selected_website_url) <= 0:
            result =  SettingModel.map_user_website(selected_website_url,session.get('user_id'))
        else:
            msg = 'Select check box to update list.'
            return render_template("setting/_news_site_box.html", msg=msg)

        return redirect(url_for('news_site_box'))
    else:
        return redirect(url_for('login'))

@app.route("/update_monitor_site_list", methods=['GET', 'POST'])
def update_monitor_site_list():
    session['logged_in'] = True
    if session.get('logged_in'):

        selected_website = request.form.getlist("monitor_website_id")

        if len(selected_website) > 0:

            result =  SettingModel.update_monitor_site_list(selected_website)

            if result <= 0:
                msg = 'Error occured, please try again.'
                return render_template("setting/_news_site_box.html", msg=msg)
            else:
                return redirect(url_for('news_site_box'))
        else:
            msg = 'Select check box to delete from tracking list.'
            return render_template("setting/_news_site_box.html", msg=msg)

        return redirect(url_for('news_site_box'))
    else:
        return redirect(url_for('login'))

# companies watch list

@app.route("/companies_watched_box", methods=['GET', 'POST'])
def companies_watched_box():
    session['logged_in'] = True
    if session.get('logged_in'):

        # news
        data_records = SettingModel.get_map_user_companies_list(session.get('user_id'))

        return render_template('setting/_companies_watched_box.html', data_records=data_records)
    else:
        return redirect(url_for('login'))

@app.route("/add_companies_watched_box", methods=['GET', 'POST'])
def add_companies_watched_box():
    session['logged_in'] = True
    if session.get('logged_in'):

        msg = ''
        if request.method == 'POST' and 'autocomplete' in request.form:

            search_company = request.form['autocomplete']
            search_criteria = request.form['search_criteria']

            result =  SettingModel.add_user_companies_watch_list(search_company,search_criteria,session.get('user_id'))

            if result <= 0:
                msg = 'Error occured, please try again.'
                return render_template("setting/_companies_watched_box.html", msg=msg)
            else:
                return redirect(url_for('companies_watched_box'))

        return redirect(url_for('companies_watched_box'))
    else:
        return redirect(url_for('login'))

@app.route("/update_companies_watched_box", methods=['GET', 'POST'])
def update_companies_watched_box():
    session['logged_in'] = True
    if session.get('logged_in'):

        selected_list = request.form.getlist("monitor_companies_id")

        if len(selected_list) > 0:
            result =  SettingModel.update_user_companies_watch_list(selected_list)

            if result <= 0:
                msg = 'Error occured, please try again.'
                return render_template("setting.html", msg=msg)
            else:
                return redirect(url_for('companies_watched_box'))
        # elif len(selected_list) <= 0:
        #     result =  SettingModel.update_user_companies_watch_list(selected_list)
        else:
            msg = 'Select check box to delete from tracking list.'
            return render_template("setting/_companies_watched_box.html", msg=msg)

        return redirect(url_for('companies_watched_box'))
    else:
        return redirect(url_for('login'))

@app.route('/autocomplete',methods=['GET'])
def autocomplete():
    session['logged_in'] = True
    if session.get('logged_in'):

        # read data from database
        lookup_records = SettingModel.get_autocomplete_records()

        search = request.args.get('autocomplete')
        results = list(itertools.chain.from_iterable(lookup_records))
        return jsonify(json_list=results)

    else:
        return redirect(url_for('login'))


# @app.route("/load_twitter_articles")
# def load_twitter_articles():
#     """ Route to return the posts """
#
#     # time.sleep(0.2)  # Used to simulate delay
#
#     if request.args:
#         counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
#
#         data_records = ReportModel.get_twitter_article(counter+quantity)
#
#         if counter == 0:
#             print(f"Returning posts 0 to {quantity}")
#             # Slice 0 -> quantity from the db
#             res = make_response(jsonify(data_records[0: quantity]), 200)
#
#         elif counter == len(data_records):
#             print("No more posts")
#             res = make_response(jsonify({}), 200)
#
#         else:
#             print(f"Returning posts {counter} to {counter + quantity}")
#             # Slice counter -> quantity from the db
#             res = make_response(jsonify(data_records[counter: counter + quantity]), 200)
#
#     return res


# @app.route("/twitter_index")
# def twitter_index():
#     twitter_report()




if __name__ == "__main__":
    # app.secret_key = os.urandom(12)
    app.run(debug=True)
