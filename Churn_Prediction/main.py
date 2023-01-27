# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 14:36:11 2022

@author: yashu
"""

from flask import Flask, render_template, request, session, flash, redirect, url_for
import pymongo
import numpy as np
import pickle

app = Flask(__name__)
app.secret_key = 'HelloWeAreBlackBulls!'

#database connection
client = pymongo.MongoClient("localhost",27017)
db = client.project


#to register the users
@app.route("/register", methods = ['GET', 'POST'])
def register():
    session.pop('_flashes', None)
    if request.method == 'POST':
        uname = request.form["uname"]
        uemail = request.form["email"]
        urole = request.form["userrole"]
        password = request.form["pass"]
        if(len(list(db.users.find({"email":uemail}))) > 0):
            flash("User Already Exists")
            return render_template("register.html", uname = session['uname'], role = session['urole'])
        else:
            db.users.insert_one({"name":uname,"email":uemail,"userrole":urole, "password":password})
            return redirect(url_for('dashboard'))
    if 'loggedin' in session and session['urole'] == 'Admin':
        return render_template("register.html", uname = session['uname'], role = session['urole'])
    return redirect(url_for('login'))

#to validate the login
@app.route("/validate", methods = ['GET', 'POST'])
def validate():
    if request.method == 'POST':
        uemail = request.form["email"]
        password = request.form["password"]
        df = db.users.find_one({"email":uemail,"password":password})
        if df is not None:
            session['loggedin'] = True
            session['uname'] = df["name"]
            session['urole'] = df["userrole"]
            return redirect(url_for('dashboard'))
        else :
            flash("User Not Found")
            return redirect(url_for('login'))
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/logout')
def logout() :
	session.pop('uname', None)
	session.pop('loggedin', None)
	session.pop('_flashes', None)
	session.pop('urole', None)
	return redirect(url_for('login'))

@app.route('/adddata', methods = ['GET', 'POST'])
def adddata() :
    if request.method == 'POST':
        vintage = request.form["vintage"]
        age = request.form["age"]
        gender = request.form["gender"]
        dependents = request.form["dependents"]
        occupation = request.form["occupation"]
        city = request.form["city"]
        customer_nw_category = request.form["customer_nw_category"]
        branch_code = request.form["branch_code"]
        days_since_last_transaction = request.form["days_since_last_transaction"]
        current_balance = request.form["current_balance"]
        previous_month_end_balance = request.form["previous_month_end_balance"]
        average_monthly_balance_prevQ = request.form["average_monthly_balance_prevQ"]
        average_monthly_balance_prevQ2 = request.form["average_monthly_balance_prevQ2"]
        current_month_credit = request.form["current_month_credit"]
        previous_month_credit = request.form["previous_month_credit"]
        current_month_debit = request.form["current_month_debit"]
        previous_month_debit = request.form["previous_month_debit"]
        current_month_balance = request.form["current_month_balance"]
        previous_month_balance = request.form["previous_month_balance"]
        churn = request.form["churn"]
        db.churn_data.insert_one({
            "vintage":vintage,
            "age":age,
            "gender":gender,
            "dependents":dependents,
            "occupation":occupation,
            "city":city,
            "customer_nw_category":customer_nw_category,
            "branch_code":branch_code,
            "days_since_last_transaction":days_since_last_transaction,
            "current_balance":current_balance,
            "previous_month_end_balance":previous_month_end_balance,
            "average_monthly_balance_prevQ":average_monthly_balance_prevQ,
            "average_monthly_balance_prevQ2":average_monthly_balance_prevQ2,
            "current_month_credit":current_month_credit,
            "previous_month_credit":previous_month_credit,
            "current_month_debit":current_month_debit,
            "previous_month_debit":previous_month_debit,
            "current_month_balance":current_month_balance,
            "previous_month_balance":previous_month_balance,
            "churn":churn
            })
        return redirect(url_for('dashboard'))
    if 'loggedin' in session:
        return render_template("add_data.html", uname = session['uname'], role = session['urole'])
    return redirect(url_for('login'))

@app.route('/predict', methods = ['GET', 'POST'])
def predict():
    session.pop('_flashes', None)
    if request.method == 'POST':
        vintage = request.form["vintage"]
        occupation = request.form["occupation"]
        if occupation == "retired":
            occupation_retired = 1
            occupation_salaried = 0
            occupation_self_employed = 0
            occupation_student = 0
        elif occupation == "salaried":
            occupation_retired = 0
            occupation_salaried = 1
            occupation_self_employed = 0
            occupation_student = 0
        elif occupation == "self_employed":
            occupation_retired = 0
            occupation_salaried = 0
            occupation_self_employed = 1
            occupation_student = 0
        elif occupation == "student":
            occupation_retired = 0
            occupation_salaried = 0
            occupation_self_employed = 0
            occupation_student = 1
        current_balance_y = request.form["current_balance"]
        previous_month_end_balance_y = request.form["previous_month_end_balance"]
        current_month_debit_y = request.form["current_month_debit"]
        previous_month_debit_y = request.form["previous_month_debit"]
        a=np.array([current_month_debit_y, previous_month_debit_y, current_balance_y, previous_month_end_balance_y, vintage, occupation_retired, occupation_salaried, occupation_self_employed, occupation_student])
        k=a.reshape(1,-1)
        with open("Y://ADT Project/static/assets/model/model1.pkl", 'rb') as f: 
            model = pickle.load(f)
        churn = model.predict(k)
        if int(churn) == 1:
            flash("Customer may leave the bank. Do Something!!!!")
        elif int(churn) == 0:
            flash("Hurray!!! Customer is going to stay with the bank")
        return render_template("predict.html", uname = session['uname'], role = session['urole'], churn = int(churn))
    if 'loggedin' in session:
        return render_template("predict.html", uname = session['uname'], role = session['urole'], churn = -1)
    return redirect(url_for('login'))

#to load the dashboard
@app.route("/dashboard")
def dashboard(): 
    if 'loggedin' in session :
        return render_template("index.html", uname = session['uname'], role = session['urole'])
    return redirect(url_for('login'))
    
#to load the login page at the start
@app.route("/")
def login():
    if 'loggedin' in session :
        return redirect(url_for('dashboard'))
    return render_template('login.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug = True)