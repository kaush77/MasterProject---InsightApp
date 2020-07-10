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
# end

from __main__ import app


# Setting page

@app.route("/twitter_box")
def twitter_box():
    if session.get('logged_in'):

        # twitter
        twitter_records = SettingModel.get_twitter_account(session.get('user_id'))

        return render_template('setting/_twitter_box.html', twitter_records=twitter_records)
    else:
        return redirect(url_for('login'))

@app.route("/add_twitter_account", methods=['GET', 'POST'])
def add_twitter_account():

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
    if session.get('logged_in'):

        # news
        data_records = SettingModel.get_map_user_companies_list(session.get('user_id'))

        return render_template('setting/_companies_watched_box.html', data_records=data_records)
    else:
        return redirect(url_for('login'))

@app.route("/add_companies_watched_box", methods=['GET', 'POST'])
def add_companies_watched_box():

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

    if session.get('logged_in'):

        selected_list = request.form.getlist("monitor_companies_id")

        if len(selected_list) > 0:

            result =  SettingModel.update_user_companies_watch_list(selected_list)

            if result <= 0:
                msg = 'Error occured, please try again.'
                return render_template("setting.html", msg=msg)
            else:
                return redirect(url_for('companies_watched_box'))
        elif len(selected_list) <= 0:
            result =  SettingModel.update_user_companies_watch_list(selected_list)
        else:
            msg = 'Select check box to delete from tracking list.'
            return render_template("setting/_companies_watched_box.html", msg=msg)

        return redirect(url_for('companies_watched_box'))
    else:
        return redirect(url_for('login'))

@app.route('/autocomplete',methods=['GET'])
def autocomplete():
    if session.get('logged_in'):

        # read data from database
        lookup_records = SettingModel.get_autocomplete_records()

        search = request.args.get('autocomplete')
        results = list(itertools.chain.from_iterable(lookup_records))
        return jsonify(json_list=results)

    else:
        return redirect(url_for('login'))
