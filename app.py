from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
from waitress import serve
import os,json
from modules.DatabaseManager import DatabaseManager
from modules.EmailManager import EmailManager
from threading import Thread as dusraDimaag
from hashlib import sha512
import time, uuid
from io import BytesIO
from flask_caching import Cache
#<<<-----DatabaseConfiguration---------->>>
with open("config.json", 'r') as config_file:
    jsonContent = json.load(config_file)
    config_file.close()
databaseCridential=jsonContent["mysql"][0]
emailCridential=jsonContent["Email"][0]
db=DatabaseManager(**databaseCridential)
EmailAgent=EmailManager(**emailCridential)
if not db.check_database_exists():
    db.create_database()
db.disconnect()
print(emailCridential)
#<<<-----SaveRegistrationData---------->>>
registration_table = 'registered_users'
columnsInReg = [
    'id INT AUTO_INCREMENT PRIMARY KEY',
    'fullname VARCHAR(255)',
    'email VARCHAR(255)',
    'password VARCHAR(255)',
    'mobilenumber VARCHAR(20)',
    'alternatemobile VARCHAR(20)',
    'aadharnumber VARCHAR(20)',
    'dateofbirth DATE',
    'pannumber VARCHAR(20)',
    'userphoto LONGBLOB',
    'aadharimagefile LONGBLOB',
    'panimagefile LONGBLOB'
]
banckDetailsTable = 'bank_details_table'
columnsInBank = [
'id INT AUTO_INCREMENT PRIMARY KEY',
'idinregtable INT',
'accountnumber VARCHAR(30)',
'ifc VARCHAR(30)',
'amount VARCHAR(255)',
'payout VARCHAR(20)',
'bankdetailimage LONGBLOB'
]
emailOTPtable = 'temp_otp_email'
columnsInEmailOTPtable = [
    'id INT AUTO_INCREMENT PRIMARY KEY',
    'email VARCHAR(255)',
    'otp VARCHAR(255)',
]
sessionDataTable = 'session_data_table'
columnsInSessionDataTable = [
    'id INT AUTO_INCREMENT PRIMARY KEY',
    'idinregtable INT',
    'email VARCHAR(255)',
    'token VARCHAR(255)'
]
# Create the table if it doesn't exist
db.connect()
if not db.check_table_exists(registration_table):
    db.create_table(registration_table, columnsInReg)
    print(f"Table '{registration_table}' created successfully.")
else:
    print(f"Table '{registration_table}' already exists.")

if not db.check_table_exists(banckDetailsTable):
    db.create_table(banckDetailsTable, columnsInBank)
    print(f"Table '{banckDetailsTable}' created successfully.")
else:
    print(f"Table '{banckDetailsTable}' already exists.")

if not db.check_table_exists(emailOTPtable):
    db.create_table(emailOTPtable, columnsInEmailOTPtable)
    print(f"Table '{emailOTPtable}' created successfully.")
else:
    print(f"Table '{emailOTPtable}' already exists.")

if not db.check_table_exists(sessionDataTable):
    db.create_table(sessionDataTable, columnsInSessionDataTable)
    print(f"Table '{sessionDataTable}' created successfully.")
else:
    db.delete_table(sessionDataTable)
    db.create_table(sessionDataTable, columnsInSessionDataTable)
    print(f"Table '{sessionDataTable}' created successfully.")

db.disconnect()
#<<<-----APP-------->>>
app = Flask(__name__)
CORS(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
#<<<-----Routes------------->>>
@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')

@app.route('/registerpage', methods=['GET'])
def registerPage():
    return render_template('Register.html')

@app.route('/bankDetails', methods=['GET'])
def bankDetails():
    try:
        sessionToken = request.args.get('session_token')
        print("get sessinfo from client: " + sessionToken)
    except Exception:
        return jsonify({"status": "failure", "message": "Invalid Session request of session Expired!."}), 500
    db.connect()
    try:
        sessionData = db.get_value_row('session_data_table', 'token', sessionToken)[0][3]
        print("\n\n\n\n ", sessionData)
    except Exception:
        sessionData = None
    db.disconnect()
    if sessionData is not None:
        return render_template('bank.html')
    else:
        return jsonify({"status": "failure", "message": "Invalid Session request of session Expired!."}), 500

@app.route('/finishPage', methods=['GET'])
def finishPage():
    return render_template('finish.html')

def scheduleClearOTPofEmail(email, timelasp):
    print("deleting thread started")
    time.sleep(timelasp)
    db.connect()
    try:
        db.delete_data(emailOTPtable, 'email', str(email))
    except Exception:
        pass
    db.disconnect()
    print("deleting thread ended")
@app.route('/sendOTP', methods=['GET', 'POST'])
def sendOTP():
    global pidsForOtpCleanerService
    try:
        receiverEmail = request.form.get('email')
        # print(receiverEmail)
        if receiverEmail.find('"'):
            receiverEmail = receiverEmail.replace('"', '')
        # print(receiverEmail)
        resp = EmailAgent.sendEmailVerificationOTP(str(receiverEmail))
        if resp[0]:
            encryptedOTP = resp[1]
            coloumn_names = ['email', 'otp']
            values = (receiverEmail, encryptedOTP)
            db.connect()
            try:
                getPreviousEmails = db.get_value(emailOTPtable, 'email')[0]
                for e in getPreviousEmails:
                    if e == receiverEmail:
                        try:
                            db.delete_data(emailOTPtable, 'email', str(receiverEmail))
                        except Exception:
                            pass
            except Exception:
                pass
            if db.add_data(emailOTPtable, coloumn_names, values):
                db.disconnect()
                runner = dusraDimaag(target=scheduleClearOTPofEmail, args=(receiverEmail, 300))
                runner.start()
                return jsonify({"status": "success"}), 201
            else:
                db.disconnect()
                return jsonify({"status": "failure"}), 500
        else:
            return jsonify({"status": "failure"}), 500
    except Exception:
        return jsonify({"status": "error"}), 500
@app.route('/verifyOTP', methods=['GET','POST'])
def verify_otp():
    try:
        receiverEmail = request.form.get('email')
        otp = request.form.get('otp')
        encryptedOTP = sha512(str(otp).encode('utf-8')).hexdigest()
        db.connect()
        emailsInOTPEmailTable = db.get_value(emailOTPtable, 'email')[0]
        for e in emailsInOTPEmailTable:
            if e == receiverEmail:
                otpForThisEmail = db.get_value_row(emailOTPtable, 'email', receiverEmail)[0][2]
                if otpForThisEmail == encryptedOTP:
                    try:
                        db.delete_data(emailOTPtable, 'email', str(receiverEmail))
                    except Exception:
                        pass
                    db.disconnect()
                    return jsonify({"status": "success"}), 201
                else:
                    db.disconnect()
                    return jsonify({"status": "failure"}), 500
        db.disconnect()
        return jsonify({"status": "failure"}), 500
    except Exception:
        return jsonify({"status": "error"}), 500

@app.route('/submitregistereddata', methods=['POST'])
def submitregistereddata():
    try:
        fullname = request.form.get('fullname')
        email = request.form.get('useremail')
        password = request.form.get('password')
        mobilenumber = request.form.get('mobilenumber')
        alternatemobile = request.form.get('alternatemobile')
        aadharnumber = request.form.get('aadharnumber')
        dateofbirth = request.form.get('dateofbirth')
        pannumber = request.form.get('pannumber')
        userphoto = request.files.get('userphoto')
        aadharimage = request.files.get('aadharimagefile')
        panimage = request.files.get('panimagefile')
        userphoto_data = userphoto.read() if userphoto else None
        aadharimage_data = aadharimage.read() if aadharimage else None
        panimage_data = panimage.read() if panimage else None
        column_names = [
            'fullname', 'email', 'password', 'mobilenumber', 'alternatemobile',
            'aadharnumber', 'dateofbirth', 'pannumber', 'userphoto',
            'aadharimagefile', 'panimagefile'
        ]
        values = (
            fullname, email, password, mobilenumber, alternatemobile, 
            aadharnumber, dateofbirth, pannumber, userphoto_data,
            aadharimage_data, panimage_data
        )
        db.connect()
        try:
            predata = db.get_value_row(registration_table, 'email', email)[0]
            idOfRegistration = db.get_value_row(registration_table, 'email', email)
        except Exception:
            predata = None
        if predata is not None:
            db.disconnect()
            return jsonify({"status": "failure", "message": "User already Registered!"}), 500
        if db.add_data(registration_table, column_names, values):
            idOfRegistration = db.get_value_row(registration_table, 'aadharnumber', aadharnumber)[0]
            db.disconnect()
            print(idOfRegistration[0])
            sessionToken = str(uuid.uuid4().hex)
            session_column = [
                'idinregtable', 'email', 'token'
            ]
            session_values = (
                idOfRegistration[0], email, sessionToken
            )
            db.connect()
            if db.add_data(sessionDataTable, session_column, session_values):
                print("\n\n\n\nSession token added")
                db.disconnect()
                return jsonify({"status": "success", "id": f"{idOfRegistration[0]}", "session_token": f"{sessionToken}", "message": "Data inserted successfully."}), 201
            else:
                print("\n\n\nSession token add error")
                db.disconnect()
                return jsonify({"status": "ServerError", "message": "Registration successfull but session expired!"}), 500
        else:
            db.disconnect()
            return jsonify({"status": "failure", "message": "Failed to insert data."}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route("/getDashboard", methods=["GET"])
def getDashboard():
    return render_template("dashboard.html")
@app.route("/getProfilePage", methods=["GET"])
def getProfilePage():
    return render_template("profile.html")
@app.route('/getDashboardDetails', methods=['GET'])
def getDashboardDetails():
    try:
        registrationId = request.args.get('id')
        sessionToken = request.args.get('session_token')
        if registrationId and sessionToken:
            db.connect()
            sessionData = db.get_value_row(sessionDataTable, 'idinregtable', registrationId)
            if sessionData:
                try:
                    sessionTokenInDB = sessionData[0][3]
                    if sessionTokenInDB == sessionToken:
                        UD = db.get_value_row(registration_table, 'id', registrationId)[0]
                        db.disconnect()
                        if UD:
                            return jsonify({"status": "success", "id": f"{UD[0]}", "full_name": f"{UD[1]}", "email": f"{UD[2]}", "mobile": f"{UD[4]}", "alternate_mobile": f"{UD[5]}", "aadhar_number": f"{UD[6]}", "date_of_birth": f"{UD[7]}", "pan_number": f"{UD[8]}"})
                        else:
                            return jsonify({"status": "failure", "message": "User not found."}), 404
                    else:
                        db.disconnect()
                        return jsonify({"status": "failure", "message": "Session expired."}), 419
                except Exception:
                    db.disconnect()
                    return jsonify({"status": "failure", "message": "An error occurred while fetching user data."}), 500
            else:
                db.disconnect()
                return jsonify({"status": "failure", "message": "Session not found."}), 404
        else:
            return jsonify({"status": "failure", "message": "Missing required parameters."}), 400
    except Exception as e:
        # print("Exception raised")
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/submitbankdetails', methods=['POST'])
def submitbankdata(): # in this also i have to authenticate using session token later.
    try:
        registrationId = request.form.get('registrationId')
        payout = request.form.get('payout')
        ifc = request.form.get('ifc')
        amount = request.form.get('amount')
        accountnumber = request.form.get('accountnumber')
        bankdetailimage = request.files.get('bankdetailimage')
        bankdetail_data = bankdetailimage.read() if bankdetailimage else None
        column_names = [
            'idinregtable', 'accountnumber', 'ifc', 'amount', 'payout', 'bankdetailimage'
        ]
        values = (
            registrationId, accountnumber, ifc, amount, payout, bankdetail_data
        )
        db.connect()
        if db.add_data(banckDetailsTable, column_names, values):
            db.disconnect()
            print("successful")
            return jsonify({"status": "success", "message": "Data inserted successfully."}), 201
        else:
            db.disconnect()
            print("Oh no something went wrong")
            return jsonify({"status": "failure", "message": "Failed to insert data."}), 500
    except Exception as e:
        print("Exception raised")
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/getloginpage', methods=['GET'])
def getloginpage():
    return render_template('login.html')
@app.route('/getprofilepicture', methods=['GET'])
@cache.cached(timeout=3000, query_string=True)
def getprofilepicture():
    try:
        registrationId = request.args.get('id')
        sessionToken = request.args.get('session_token')
        if registrationId and sessionToken:
            db.connect()
            sessionData = db.get_value_row(sessionDataTable, 'idinregtable', registrationId)
            if sessionData:
                try:
                    sessionTokenInDB = sessionData[0][3]
                    if sessionTokenInDB == sessionToken:
                        UD = db.get_value_row(registration_table, 'id', registrationId)[0]
                        db.disconnect()
                        if UD:
                            return send_file(BytesIO(UD[9]), mimetype='image/jpeg')
                        else:
                            return jsonify({"status": "failure", "message": "User not found."}), 404
                    else:
                        db.disconnect()
                        return jsonify({"status": "failure", "message": "Session expired."}), 404
                except Exception:
                    db.disconnect()
                    return jsonify({"status": "failure", "message": "An error occurred while fetching user data."}), 500
            else:
                db.disconnect()
                return jsonify({"status": "failure", "message": "Session not found."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/getaadharimage', methods=['GET'])
@cache.cached(timeout=3000, query_string=True)
def getaadharimage():
    try:
        registrationId = request.args.get('id')
        sessionToken = request.args.get('session_token')
        if registrationId and sessionToken:
            db.connect()
            sessionData = db.get_value_row(sessionDataTable, 'idinregtable', registrationId)
            if sessionData:
                try:
                    sessionTokenInDB = sessionData[0][3]
                    if sessionTokenInDB == sessionToken:
                        UD = db.get_value_row(registration_table, 'id', registrationId)[0]
                        db.disconnect()
                        if UD:
                            return send_file(BytesIO(UD[10]), mimetype='image/jpeg')
                        else:
                            return jsonify({"status": "failure", "message": "User not found."}), 404
                    else:
                        db.disconnect()
                        return jsonify({"status": "failure", "message": "Session expired."}), 404
                except Exception:
                    db.disconnect()
                    return jsonify({"status": "failure", "message": "An error occurred while fetching user data."}), 500
            else:
                db.disconnect()
                return jsonify({"status": "failure", "message": "Session not found."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/getpanimage', methods=['GET'])
@cache.cached(timeout=3000, query_string=True)
def getpanimage():
    try:
        registrationId = request.args.get('id')
        sessionToken = request.args.get('session_token')
        if registrationId and sessionToken:
            db.connect()
            sessionData = db.get_value_row(sessionDataTable, 'idinregtable', registrationId)
            if sessionData:
                try:
                    sessionTokenInDB = sessionData[0][3]
                    if sessionTokenInDB == sessionToken:
                        UD = db.get_value_row(registration_table, 'id', registrationId)[0]
                        db.disconnect()
                        if UD:
                            return send_file(BytesIO(UD[11]), mimetype='image/jpeg')
                        else:
                            return jsonify({"status": "failure", "message": "User not found."}), 404
                    else:
                        db.disconnect()
                        return jsonify({"status": "failure", "message": "Session expired."}), 404
                except Exception:
                    db.disconnect()
                    return jsonify({"status": "failure", "message": "An error occurred while fetching user data."}), 500
            else:
                db.disconnect()
                return jsonify({"status": "failure", "message": "Session not found."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/getpassbookimage', methods=['GET'])
@cache.cached(timeout=3000, query_string=True)
def getpassbookimage():
    try:
        registrationId = request.args.get('id')
        sessionToken = request.args.get('session_token')
        if registrationId and sessionToken:
            db.connect()
            sessionData = db.get_value_row(sessionDataTable, 'idinregtable', registrationId)
            if sessionData:
                try:
                    sessionTokenInDB = sessionData[0][3]
                    print("pass")
                    if sessionTokenInDB == sessionToken:
                        UD = db.get_value_row(banckDetailsTable, 'idinregtable', registrationId)[0]
                        print("pass2")
                        db.disconnect()
                        if UD:
                            return send_file(BytesIO(UD[6]), mimetype='image/jpeg')
                        else:
                            return jsonify({"status": "failure", "message": "User not found."}), 404
                    else:
                        db.disconnect()
                        return jsonify({"status": "failure", "message": "Session expired."}), 404
                except Exception:
                    db.disconnect()
                    return jsonify({"status": "failure", "message": "An error occurred while fetching user data."}), 500
            else:
                db.disconnect()
                return jsonify({"status": "failure", "message": "Session not found."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/login', methods=['POST'])
def login():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        db.connect()
        if db.get_value_row(registration_table, 'email', email)[0][3] == password:
            idOfRegistration = db.get_value_row(registration_table, 'email', email)[0]
            sessionToken = str(uuid.uuid4().hex)
            session_column = [
                'idinregtable', 'email', 'token'
            ]
            session_values = (
                idOfRegistration[0], email, sessionToken
            )
            if db.add_data(sessionDataTable, session_column, session_values):
                db.disconnect()
                return jsonify({"status": "success", "id": f"{idOfRegistration[0]}", "session_token": f"{sessionToken}"}), 201
        else:
            db.disconnect()
            return jsonify({"status": "failure"}), 500
    except Exception:
        return jsonify({"status": "error"}), 500
print(f"Running server on: http://127.0.0.1:8080")
print("OK")
# serve(app=app, host='127.0.0.1', port=5000)
# app.run(port=8080)
app.run(host='127.0.0.1', port=8080)
