from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
from datetime import datetime
import json


# open config.json and read param 
with open('config.json', 'r') as jc :
    data =json.load(jc)
    params = data['params']
    mailsmtp = data['smtpconf']
    
    local_uri = str(params['local_uri'])
    prod_uri = str(params['prod_uri'])

    smtp_mail_server = str(mailsmtp['mail_server'])
    smtp_mail_port = int(mailsmtp['mail_port'])
    smtp_mail_uname = str(mailsmtp['mail_uname'])
    smtp_mail_pwd = str(mailsmtp['mail_pwd'])
    smtp_mail_sender = str(mailsmtp['mail_sender'])


# create the SQLAlchemy() extension
db = SQLAlchemy()

# create the Mail() extension
mail = Mail() # type: ignore

# create a flask app
app = Flask(__name__)

#this will change the uri as per the server type
if params['local_server'] == 'True' :
    # configure the SQLite database, relative to the app instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = local_uri
else :
    # configure the SQLite database, relative to the app instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = prod_uri

 #mail trap smtp credentials
app.config['MAIL_SERVER'] = smtp_mail_server
app.config['MAIL_PORT'] = smtp_mail_port
app.config['MAIL_USERNAME'] = smtp_mail_uname
app.config['MAIL_PASSWORD'] = smtp_mail_pwd
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# Initialize your app with SQLAlchemy
db.init_app(app)

# Initialize your app with Flask Mail
mail.init_app(app) # type: ignore

#contacs table
class Contact(db.Model):

    # id,name,email,mobile,message,date
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=False, nullable=False)
    mobile = db.Column(db.String(15), unique=False, nullable=False)
    message = db.Column(db.String(150), unique=False, nullable=False)
    #date = db.Column(db.String(50), unique=False, nullable=False)


class Subscribe(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    sub_name = db.Column(db.String(50), unique=False, nullable=False)
    sub_email = db.Column(db.String(50), unique=False, nullable=False)

@app.route('/') 

def home() :
    return render_template('index.html')




@app.route('/bmicalc', methods = ['GET','POST']) # type: ignore
def bmicalc() :
    # Bmi calculator    
    if request.method == 'POST'  :
        weight = int(request.form['weight'])
        height = float(request.form['height']) / 100
        bmi = round(weight / height ** 2)
        return render_template('bmicalc.html', result = bmi ) 
    
    return render_template('bmicalc.html')

@app.route('/cv')
def cv() :
    return render_template('cv.html')

@app.route('/blog')

def blog() :
    return render_template('blog.html')


@app.route('/contactus' , methods = ['GET','POST'])

def contact() :

    if request.method == 'POST' :
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contact(name = name ,email = email, mobile = phone, message = message)
        db.session.add(entry)
        db.session.commit()
        

    return render_template('contactus.html')



@app.route('/smtpmail' , methods = [ 'GET','POST']) # type: ignore

def smtpmail() :

    if request.method == 'POST' :
        # get values from form
        mail_name = request.form.get('name')
        mail_email = request.form.get('email')

        entry = Subscribe(sub_name = mail_name , sub_email = mail_email)
        db.session.add(entry)
        db.session.commit()

        msg = Message("Flask Mail Via SMTP", sender = smtp_mail_sender, recipients = [mail_email])
        # The message can contain a body and/or HTML:
        #msg.body = "testing"
        msg.html = '''
                    <!DOCTYPE html>
                        <html>
                            <head>
                                <meta charset="UTF-8">
                                <title>FLask Mail</title>
                                <style>
                                /* Put your CSS styles here */
                                </style>
                            </head>
                            <body>
                                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                                <tr>
                                    <td align="center">
                                    <h1>Welcome to My Website</h1>
                                    <p>Dear User</p>
                                    <p>Thank you for subscribing to our newsletter. We hope you find our content informative and helpful. </p>
                                    <p>Sincerely,</p>
                                    <p>The My Website Team</p>
                                    </td>
                                </tr>
                                </table>
                            </body>
                        </html>'''
        mail.send(msg)

        # f-String is used that convert all other data type into string 
        return render_template('mail.html', success = f"Success !{mail_name} You are now Subscribed." ) 
    
    return render_template('mail.html')




@app.route('/gstcalc' , methods = ['GET' ,'POST']) # type: ignore

def gstcalc():
    if request.method == 'POST' :
        amount = float(request.form['amount'])
        percentage = float(request.form['percentage'])
        gsttype = int(request.form['gsttype'])
        gstamount = 0
        total = 0
        netamount = 0
        if gsttype == 0 :
            # 1 inclusive gst ,0 exclusive gst
            gstamount = round((amount * percentage ) / 100 , 2)
            total = round(amount + gstamount ,2)
            netamount =amount
        else:
            
            gstamount = round(amount - (amount *(100/(100+percentage))), 2)
            netamount = round(amount - gstamount , 2)
            total = round(netamount + gstamount , 2)

        return render_template('gstcalc.html', amount = amount, netamount = netamount ,
                                percentage = percentage ,gstamount = gstamount , total = total)
    
    return render_template('gstcalc.html')



@app.route('/lifeinweeks' , methods = ['GET' , 'POST']) # type: ignore

def lifeinweeks() :
    if request.method == 'POST' :
        
        age = int(request.form['age'])
        name = request.form['name']
        yearleft = 90 - age
        monthsleft = yearleft * 12
        weeksleft = yearleft * 52.14 
        daysleft = yearleft * 365
        return render_template('lifeinweeks.html' ,
                                success = f"Success ! Hello {name},you have{yearleft}years,{monthsleft} months,{daysleft}days left in your 90 years Life" )
    

    return render_template('lifeinweeks.html')


@app.route('/tipcalc' , methods = ['GET' , 'POST']) # type: ignore

def tipcalc():
    if request.method == 'POST' :
        bill_amount = float(request.form['billamount'])
        tip_percentage = float(request.form['tippercentage'])
        no_people = float(request.form['people'])
        tip_amount = bill_amount * tip_percentage / 100 # type: ignore
        bill_with_tip =bill_amount + tip_amount
        per_people_amount = bill_with_tip / no_people
        return render_template('tipcalc.html' ,
                                bill_amount = bill_amount,
                                tip_amount = tip_amount ,
                                bill_with_tip =bill_with_tip ,
                                success =f"Each Person Should pay {per_people_amount}")
    
    return render_template('tipcalc.html')
# debug=True enables the debug mode
app.run(debug=True)