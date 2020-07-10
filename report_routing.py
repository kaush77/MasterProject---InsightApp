import os
import itertools
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort,url_for,jsonify,Response,make_response,current_app

# start - import user define model
from users_model import User
from common_data_model import CommonData
from setting_model import SettingModel
from indices_model import IndicesModel
from index_model import IndexPageModel
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

# normailze package
import scipy
from sklearn import preprocessing

from __main__ import app

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

    elif feature == 'Pie':

        labels,values,colors =  get_plot_data(feature)

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

@app.route("/twitter_report_index", methods=['GET', 'POST'])
def twitter_report_index():

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

    if session.get('logged_in'):
        last_record_id = request.args.get("last_record_id")

        sentiment_type_id = 2

        if session.get('news_filter_type'):
            sentiment_type_id = session.get('news_filter_type')

        latest_news_records = ReportModel.get_latest_news_article(last_record_id,sentiment_type_id,session.get('user_id'))
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
