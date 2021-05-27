from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import smtplib
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content

app = Flask(__name__)
  
app.secret_key = 'a'
 
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'AuPCXvdChb'
app.config['MYSQL_PASSWORD'] = 'bfkBX9cPsw'
app.config['MYSQL_DB'] = 'AuPCXvdChb'
mysql = MySQL(app)

def sendgridmail_reg(user,TEXT):
    sg = sendgrid.SendGridAPIClient('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    from_email = Email("abc@example.com")  # Change to your verified sender
    to_email = To(user)  # Change to your recipient
    subject = "Registration Successful"
    content = Content("text/plain",TEXT)
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()
    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)

def sendgridmail_alert(user,TEXT):
    sg = sendgrid.SendGridAPIClient('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    from_email = Email("abc@example.com")  # Change to your verified sender
    to_email = To(user)  # Change to your recipient
    subject = "Stock Empty Alert"
    
    content = Content("text/plain",TEXT)
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()
    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']

        regex = re.compile('[@_!#$%^&*()<>?/}{~:]')
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user2 WHERE username = % s', (username, ))
        account = cursor.fetchone()
        print(account)
        if account:
            msg = 'Account already exists! Please Login.'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif re.match(r'[0-9]+', username):
            msg = 'Username must contain only characters!'
        elif (len(password) < 8):
            msg = "Your password should be of 8 characters minimum!"
        elif (regex.search(password) == None):
            msg = "Your password must contain a special character!"
        elif not re.match(r'[A-Za-z0-9]+', password):
            msg = "Your password must be a combination of uppercase and lowercase letters along with a number!"
        elif not (password == repassword):
            msg = "Both your passwords should match!"

        else:
            cursor.execute('INSERT INTO user2 VALUES (NULL, % s, % s, % s, % s)', (username, email, password, repassword))
            mysql.connection.commit()
            msg = 'You have successfully registered with us! Please login to use IMS.'
            TEXT1 = "Hello "+username + "!\n\n"+ """Thank you for registering with us! We hope you have a hassle-free experience using IMS.""" 
            TEXT2 = "\n\n"+ """Please do provide your valuable feedback by filling out this form: https://forms.gle/GLUYwwa1oEzt6haK8""" 
            TEXT3 = "\n\n"+ """Best Regards,""" 
            TEXT4 = "\n"+ """IMS Team""" 
            MAINTEXT = TEXT1+TEXT2+TEXT3+TEXT4
            # message  = 'Subject: {}\n\n{}'.format("smartinterns Carrers", TEXT)
            # sendmail(TEXT,email)
            sendgridmail_reg(email,MAINTEXT)
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register1.html', msg = msg)

@app.route('/login',methods = ['GET', 'POST'])
def login():
    global userid
    msg = ''
   
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user2 WHERE username = % s AND password = % s', (username, password))
        account = cursor.fetchone()
        print (account)
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            userid = account[0]
            session['username'] = account[1]
            return redirect(url_for('Index'))
            # return render_template('dashboard.html')
        else:
            msg = 'Incorrect Username or Password!'
    return render_template('login1.html', msg = msg)

# @app.route('/fetch')
# def Index():

#     user_id = session.get('id')
#     cursor = mysql.connection.cursor()
#     cursor.execute("SELECT * FROM inventory2 WHERE user_id = %s", (user_id,))
#     data = cursor.fetchall()
#     print(data)

#     return render_template('index2.html', inventory = data)

@app.route('/fetch')
def Index():
    user = session.get('username')
    print(user)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM user2 u WHERE u.username = %s", (user,))
    a = cursor.fetchone()
    print(a)
    cursor.execute("SELECT * FROM inventory2 i WHERE i.user_id = %s", (a,))
    data = cursor.fetchall()
    print(data)
    
    return render_template('index2.html', inventory = data)


@app.route('/transactions')
def transactions():
    user = session.get('username')
    print(user)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM user2 u WHERE u.username = %s", (user,))
    a = cursor.fetchone()
    print(a)
    cursor.execute("SELECT * FROM transactions t WHERE t.user_id = %s", (a,))
    data = cursor.fetchall()
    print(data)
    
    return render_template('transactions.html', transaction = data)

@app.route('/purchase')
def purchase():
    user = session.get('username')
    print(user)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM user2 u WHERE u.username = %s", (user,))
    r = cursor.fetchone()
    print(r)
    cursor.execute("SELECT * FROM purchase p WHERE p.user_id = %s", (r,))
    data = cursor.fetchall()
    print(data)

    return render_template('purchase.html', purchase = data)

@app.route('/insert', methods = ['POST'])
def insert():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        pname = request.form['pname']
        pprice = request.form['pprice']
        pquantity = request.form['pquantity']
        userid = session.get('id')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO inventory2 (user_id, pname, pprice, pquantity) VALUES (%s, %s, %s, %s)", (userid, pname, pprice, pquantity))
        mysql.connection.commit()
        return redirect(url_for('Index'))

@app.route('/delete', methods = ['GET','POST'])
def delete():
    if request.method == 'POST':
        id_data = request.form['id']
        flash("Record has been Deleted Successfully!")
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM inventory2 WHERE id=%s", (id_data,))
        mysql.connection.commit()

        return redirect(url_for('Index'))

@app.route('/update',methods=['POST','GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        pname = request.form['pname']
        pprice = request.form['pprice']
        pquantity = request.form['pquantity']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE inventory2 SET pname=%s, pprice=%s, pquantity=%s WHERE id=%s", (pname, pprice, pquantity, id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('Index'))

@app.route('/sell',methods=['POST','GET'])
def sell():
    global userid

    if request.method == 'POST':
        id_data = request.form['id']
        vname = request.form['vname']
        vcontact = request.form['vcontact']
        sellquantity = request.form['sellquantity']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM inventory2 where id = %s", (id_data, ))
        transaction = cur.fetchone()
        print(transaction)

        if transaction:
            session['id'] = transaction[0]
            userid = transaction[1]
            newquantity = transaction[4] - int(sellquantity)
            print(newquantity)
            if newquantity == 0:
                cur.execute("SELECT email FROM user2 where id = %s", (userid, ))
                data = cur.fetchone()
                print(data)
                TEXT = "Some of your products are out of Stock. This is a gentle reminder for you to buy some new items to fill up your shelves!"
                TEXT1 = "\n\n"+"Best Regards,"
                TEXT2 = "\n"+"IMS Team"
                text = TEXT+TEXT1+TEXT2
                sendgridmail_alert(data, text)
            cur.execute("UPDATE inventory2 SET pquantity=%s WHERE id=%s", (newquantity, session['id']))
            cur.execute("INSERT INTO transactions (user_id, vname, vcontact, pname, pquantity) VALUES (%s, %s, %s, %s, %s)", (userid, vname, vcontact, transaction[2], sellquantity))
            flash("Quantity Sold Successfully!")
            
            cur.execute("SELECT * FROM inventory2 WHERE user_id = %s", (transaction[1],))
            data = cur.fetchall()
            mysql.connection.commit()
            print(data)

        return render_template('index2.html', inventory = data)

@app.route('/buy',methods=['POST','GET'])
def buy():
    global userid

    if request.method == 'POST':
        id_data = request.form['id']
        vname = request.form['vname']
        vcontact = request.form['vcontact']
        buyquantity = request.form['buyquantity']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM inventory2 where id = %s", (id_data, ))
        transaction = cur.fetchone()
        print(transaction)

        if transaction:
            session['id'] = transaction[0]
            userid = transaction[1]
            newquantity = transaction[4] + int(buyquantity)
            print(newquantity)
            # user_id = session.get('id')
            cur.execute("UPDATE inventory2 SET pquantity=%s WHERE id=%s", (newquantity, session['id']))
            cur.execute("INSERT INTO purchase (user_id, vname, vcontact, pname, pquantity) VALUES (%s, %s, %s, %s, %s)", (userid, vname, vcontact, transaction[2], buyquantity))
            flash("Quantity Purchased Successfully!")
            
            cur.execute("SELECT * FROM inventory2 WHERE user_id = %s", (transaction[1],))
            data = cur.fetchall()
            mysql.connection.commit()
            print(data)

        return render_template('index2.html', inventory = data)

@app.route('/aboutus')
def abouts():
    return render_template('aboutus.html')

@app.route('/profile')
def profile():
    user = session.get('username')
    print(user)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user2 u WHERE u.username = %s", (user,))
    r = cursor.fetchall()
    print(r)

    return render_template('profile.html', profile = r)

@app.route('/profileupdate',methods=['POST','GET'])
def profileupdate():
    msg = ''
    if request.method == 'POST':
        user = session.get('username')
        print(user)
        # id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE user2 SET username=%s, email=%s WHERE username=%s", (name, email, user))
        # flash("Data Updated Successfully")
        mysql.connection.commit()
        msg = "Profile data updated Successfully!"
    # return redirect(url_for('profile'))
    return render_template('profileupdate.html', msg = msg)

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('home.html')

if __name__ == '__main__':
   app.run(host='0.0.0.0',debug = True, port = 8080)    
