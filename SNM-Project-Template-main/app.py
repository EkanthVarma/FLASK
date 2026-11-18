from config import Config,emailTemplates
import mysql.connector as sql
import random
import smtplib
from email.message import EmailMessage
from flask import Flask,render_template,redirect,url_for,request,session,flash,send_file
import bcrypt
from werkzeug.utils import secure_filename
import os
import sys

#create an upload folder if not exists
if not os.path.exists('upload'):
    os.mkdir('upload') #it will create a folder..
#Setting up a secure way to generate and verify timed
#tokens in Flask app

from itsdangerous import URLSafeTimedSerializer,BadSignature,TimedSerializer

app = Flask(__name__)
app.secret_key = "Ekanth@95"

DBConfig = Config()
from_email = DBConfig.from_email
email_app_password = DBConfig.email_app_password

def generateHash(text):
    btext = text.encode('utf-8') 
    cipher_text = bcrypt.hashpw(btext,bcrypt.gensalt(4))
    return cipher_text.decode('utf-8')
    #print(cipher_text)
    #bcrypt.hashpw(btext)
#print(generateHash("ekanth"))
    

#We will first make connections with DB 
def getConnectionWithDB():
    db_host = DBConfig.db_host
    db_port = DBConfig.db_port
    db_user = DBConfig.db_user
    db_password = DBConfig.db_password
    db_name = DBConfig.db_name

    try:
        Connection = sql.connect(
            host = db_host,
            port = db_port,
            user = db_user,
            password = db_password,
            database = db_name
        )
        return Connection
    except:
        return "Connection Failed"
#Inseert the data into the table 
def insertUserRecord(user_data):
    """Inserting the user records"""
    name = user_data['name']
    email = user_data['email']
    password_harsh = user_data['password_harsh']
    connection = getConnectionWithDB()
    if connection == "Connection Failed":
        return False
    else:
        try: 
            cursor = connection.cursor()
            cursor.execute(
            "INSERT INTO users (name,email,password_harsh) values(%s,%s,%s)",(name,email,password_harsh))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except:
             print("Data cannot be inserted ")
             return False


#Now let us define the data 
# data = {
#     'name':"Ekanth Varma",
#     'email':'ekanthvarma2005@gmail.com',
#     'password_hash':'1a2s2d4c'
# }

def readUserRecords():
    
    connection = getConnectionWithDB()
    if connection == "Connection Failed":
          return False
    else:
        cursor = connection.cursor()
        cursor.execute("Select * from users")
        data1 = cursor.fetchall()
        records = []
        for record in data1:
               temp = {}
               #print(record)
               temp['id'] = record[0]
               temp['name'] = record[1]
               temp['email'] = record[2]
               temp['password_harsh'] = record[3]
               temp['is_verified'] = record[4]
               temp['created_at'] = record[5]
               records.append(temp)
        cursor.close()
        connection.close()
        return records
#print(readUserRecords())
def readUserRecordByEmail(user_data):
    email = user_data['email']
    connection = getConnectionWithDB()    
    if connection == 'Connection Failed':
         return False
    else:
        try:
            cursor = connection.cursor()
            cursor.execute("Select * from users where email=%s",(email,))
            data1 = cursor.fetchone()
            #print(data1)
            record = {
                "id":data1[0],
                "name":data1[1],
                "email":data1[2],
                "password_harsh":data1[3],
                "is_verified": data1[4],
                "created_at": data1[5]
            }
            return record
        except:
            cursor.close()
            connection.close()
            return "No Record"


def readUserRecordbyId(user_data):
    id = user_data['id']
    connection = getConnectionWithDB()    
    if connection == 'Connection Failed':
        return False
    else:
        cursor = connection.cursor()
        cursor.execute("Select * from users where id=%s",(id,))
        data1 = cursor.fetchone()
        try:
            record = {
                'id':data1[0],
                "name":data1[1],
                "email":data1[2],
                "password_harsh":data1[3],
                "is_verified": data1[4],
                "created_at": data1[5]
            }
            return record
        except:
                cursor.close()
                connection.close()
                return "No Record"
        

#print(readUserRecordbyId(user_data))
#print(readUserRecordByEmail(user_data))

def updateNamebyIDorEmail(user_data):
    query_filter = ""
    try:
        id = user_data['id'] 
        query_filter = 'id'
    except:
        email = user_data['email']
        query_filter = "email"
    new_name = user_data['new_name']
    connection = getConnectionWithDB()
    if connection == "Connection Failed":
        return False
    else:
        cursor = connection.cursor()
        if query_filter == "id":
            query = "UPDATE users SET name = %s WHERE id = %s"
            values = (new_name,id)
        elif query_filter == "email":
            query = "UPDATE users SET name = %s WHERE email = %s"
            values = (new_name,email)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return True

def updatePasswordByIdorEmail(user_data):
    query_filter = ""
    try:
        id = user_data['id']
        query_filter = 'id'
    except:
        email = user_data['email']
        query_filter = "email"
    new_password = user_data['new_password']
    connection = getConnectionWithDB()
    if connection == 'Connection Failed':
        return False
    else:
        cursor = connection.cursor()
        if query_filter == "id":
            query = "UPDATE users SET  password_harsh = %s WHERE id = %s"
            values = (new_password,id)
        elif query_filter == "email":
            query = "UPDATE users SET password_harsh = %s WHERE email = %s"
            values = (new_password,email)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return True


def updateVerifiedByIdorEmail(user_data):
    query_filter = ""
    try:
        id = user_data['id']
        query_filter = 'id'
    except:
        email = user_data['email']
        query_filter = 'email'
    new_verified = user_data['new_verified']
    connection = getConnectionWithDB()
    if connection == 'Connection Failed':
        return False
    else:
        cursor = connection.cursor()
        if query_filter == "id":
            query = "UPDATE users SET is_verified = %s WHERE id = %s"
            values = (new_verified,id)
        elif query_filter == "email":
            query = "UPDATE users SET is_verified = %s WHERE email = %s"
            values = (new_verified,email)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return True
    

def generateOTP():
    OTP = random.randint(1000,9999)
    return OTP

def sendOTPviaemail(to_email,otp):
    message = EmailMessage()
    message['Subject'] = "OTP --> Notification"
    message['From'] = from_email
    message['To'] = to_email
    message.set_content(
        f"Your OTP is {otp}"
    )
    with smtplib.SMTP("smtp.gmail.com",587) as server:
        server.starttls()
        server.login(from_email,email_app_password)
        server.send_message(message)
    return True

def SendEmail(subject:str,to_email:str,body:str):
    message = EmailMessage()
    message['Subject'] = subject
    message['From']=from_email
    message['To'] = to_email
    message.set_content(body)
    with smtplib.SMTP("smtp.gmail.com",587) as server:
        server.starttls()
        server.login(from_email,email_app_password)
        server.send_message(message)
    return True

def validateData(user_data):
    errors = []
    name=user_data['name']
    email=user_data['email']
    password=user_data['password']
    confirm_password=user_data['confirm_password']
    if name is None or len(name)<2:
        errors.append("Invalid Name")
    if email is None or len(email)<5:
        errors.append("Invalid Email")
    if password is None or len(password)<5:
        errors.append("Invalid Password")
    if password != confirm_password:
        errors.append("Password Mismatch")
    return errors

def verifyDuplicateEmail(user_data):
    #email = user_data['email']
    record = readUserRecordByEmail(user_data)
    if record == "No Record":
        return False #duplicate ledhu
    else:
        return True #duplicate undi
    

user_data = {"id":2,
             "name":"",
             "email":"ekanthvarma2005@gmail.com",
             "password":"12345",
             "confirm_password":"123",
             "verified":True}
#print(validateData(user_data))

#print(updateVerifiedByIdorEmail(user_data))
#print(updatePasswordByIdorEmail(user_data))
#print(updateNamebyIDorEmail(user_data))
#print(generateOTP())

serializer = URLSafeTimedSerializer(app.secret_key)
def resetPasswordTokenGenerate(email):
    token = serializer.dumps(
        email,
        salt="reset-password"
    )
    return token
def validateToken(token):
    try:
        data = serializer.loads(
            token,
            salt="reset-password",
            max_age = 300
        )
        return data
    except BadSignature:
        return "Invalid"
    except TimedSerializer: #if token timeout
        return "Timeout"


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register',methods = ['GET','POST'])
def register():
    global OTP
    if (request.method =="GET"):
        return render_template('register.html')
    elif (request.method=="POST"):
        print("FORM DATA:", request.form)
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password  = request.form['confirm_password']
        user_data = {
            "name":name,
            "email":email,
            "password":password,
            "confirm_password":confirm_password
        }
        errors = validateData(user_data)
        if len(errors)>0:
            return render_template('register.html',
                               errors=errors)
        else:
            is_duplicate = verifyDuplicateEmail(user_data)
            if is_duplicate == False: #duplicate ledu
                session['otp'] = generateOTP()
                password_harsh = generateHash(user_data['password'])
                name = user_data['name']
                email = user_data['email']
                status = insertUserRecord({
                    'name':name,
                    'email':email,
                    'password_harsh':password_harsh
                })
                #status of insertion
                if status == True:
                    session['name'] = email
                    OTP = session['otp']
                    sendOTPviaemail(email,OTP)
                    return redirect('/verify')
                    #return render_template('register.html',
                                  #res="Registration Successfully Completed"
                                  #)
                else:
                    return render_template('register.html',
                                           err="Registration Failed")
            else: #duplicate undi
                return render_template('register.html',
                                       err="Account already exists")
                
@app.route("/forgot_password",methods=['GET','POST'])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")
    if request.method == "POST":
        email = request.form.get("email",None)
        #check whether the email exists in db or not
        data = {'email':email}
        record = readUserRecordByEmail(user_data=data)
        if 'id' in record:
            #send mail generation of token
            token = resetPasswordTokenGenerate(
                email=email)
            #reset password url
            reset_url = url_for('reset_password',
                                token=token,
                                _external=True)
            email_status = SendEmail(
                subject = "Reset Password - SNS",
                to_email=email,
                body = emailTemplates.send_reset_password_template(
                    username=record['name'],
                    url=reset_url,
                    time=5
                ))
            if email_status:
                return render_template("forgot_password.html",
                                       msg="Email has been sent")
            else:
                return render_template("forgot_password.html",
                                       error = "Unable to send email")
        else:
            return render_template("forgot_password.html",
                                   error="Enter a Valid email")

@app.route('/reset-password/<string:token>',
           methods=['GET','POST'])
def reset_password(token):
    token_status= validateToken(token=token)
    if token_status=="Invalid":
        return render_template('forgot_password.html',
                               error="Invalid URL")
    elif token_status=="Timeout":
        return render_template('forgot_password.html',
                               error="URL Expired")
    email = token_status
    if request.method == "GET":
        return render_template('reset_password.html',
                               token=token)
    #POST request
    if request.method == "POST":
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password'
                                            )
        if new_password == confirm_password:
            #generate hash password
            password_harsh = generateHash(text = new_password)
            #update the password in the database
            data = {'email':email,
                    'new_password':password_harsh}
            update = updatePasswordByIdorEmail(user_data=data)
            if update:
                #redirect to login page
                return redirect('/login')
            else:
                return render_template('reset_password.html')
        else:
            return render_template('reset_password.html',
                                   error="Password mismatch")

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        email = request.form['email']
        password= request.form['password']
        #we have to check account existed or not
        user_data = {'email':email}
        record = readUserRecordByEmail(user_data=user_data)
        #print("Login Data:",record)
        if record:
            #if data exists
            if record['is_verified'] == 1:
                login_status = bcrypt.checkpw(password.encode('utf-8'),
                                              record['password_harsh'].encode('utf-8')
                                              )
                #print(login_status)
                if login_status:
                    #create a session,inside that we need to store email
                    session['email'] = email
                    session['id'] = record['id']
                    session['name'] = record['name']
                    return redirect('/dashboard')
                else:
                    return redirect('/login')
            else:
                return redirect('/login')
        else:
            return redirect('/login')
        
#total notes count
#total files count
def getFilesAndNotesCount(user_id):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor()
            get_notes_count = """SELECT COUNT(*) FROM NOTES 
                             WHERE USER_ID = %s;"""
            cursor.execute(get_notes_count,(user_id,))
            notes_count=cursor.fetchone()[0]
            get_files_count="""select count(*) from file_data
                            where user_id=%s;"""
            cursor.execute(get_files_count,(user_id,))
            files_count = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            return notes_count,files_count
    except Exception as e:
        return False,f'Exception raised in count:{e}' 
    
def recentNotes(user_id):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor(dictionary=True)
            get_recent_notes = """SELECT * FROM NOTES WHERE USER_ID = %s ORDER BY updated_at DESC LIMIT 3;"""
            cursor.execute(get_recent_notes,(user_id,))
            recent_notes = cursor.fetchall()
            cursor.close()
            connection.close()
            return True,recent_notes
    except Exception as e:
        return False,f'Exception raised in recentNotes:{e}'
    
    
@app.route('/dashboard')
def dashboard():
    #if the user data is not in the session redirect to login page
    if "id" not in session:
        return redirect("/login")
    userid = session['id']
    notes_count,files_count = getFilesAndNotesCount(userid)
    _,recent_notes = recentNotes(userid)
    print(recent_notes)
    return render_template('dashboard.html',
                           username=session['name'],
                           total_notes = notes_count,
                           total_files = files_count,
                           notes = recent_notes)
    
#profile route
@app.route('/user/profile',methods=['GET'])
def profile():
    if "id" not in session:
        redirect('/login')
    name= session['name']
    email= session['email']
    return render_template("profile.html",email=email,
                           name= name)
    

@app.route('/verify',methods=['GET','POST'])
def verify():
    global OTP
    if request.method == "GET":
        return render_template('verify.html')
    elif request.method == "POST":
        otp = request.form['otp']
        otp = int(otp)
        if otp == session['otp']:
            is_verify = True
            updateVerifiedByIdorEmail({'email':session['name'],'new_verified':is_verify})
            return redirect('/login')
        else:
            return render_template('verify.html',err="Invalid OTP")
        
#----------------------------------------
#          Notes routes
#----------------------------------------

def getNotesByUserId(user_id):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database connection Failed"
        else:
            cursor = connection.cursor(dictionary=True)
            get_notes_by_id="""SELECT * FROM NOTES WHERE
            USER_ID = %s;"""
            cursor.execute(get_notes_by_id,(user_id,))
            notes = cursor.fetchall()
            connection.commit()
            cursor.close()
            connection.close()
            return True,notes
    except Exception as e:
        return False,f'Exception raised in add notes:{e}'

@app.route('/notes',methods=['GET','POST'])
def mynotes():
    if "id" not in session:
        return redirect('/login')
    if request.method == "GET":
        #get user notes from the database
        id = session['id']
        #print(id)
        status,notes = getNotesByUserId(user_id=id)
        #print(notes)
        if status == True:
            return render_template("notes.html",
                                   notes = notes)
        else:
            return render_template('notes.html',err=notes)
    if request.method == "POST":
        search = request.form.get('searchnotes')
        id = session['id']
        status,notes = getNotesByUserId(user_id=id)
        if status == True:
            #filter the notes based on the search
            filtered_notes = []
            for note in notes:
                if search.lower() in note['title'].lower() or search.lower() in note['content'].lower():
                    filtered_notes.append(note)
            return render_template("notes.html",
                                   notes=filtered_notes)
        else:
            return render_template('notes.html',err=notes)
        
#insert notes records in table
def addNotesRecord(user_id:int,title:str,content:str):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database connection Failed"
        else:
            cursor = connection.cursor()
            add_notes_query = """ INSERT INTO NOTES(user_id,title,content) values(%s,%s,%s)"""
            cursor.execute(add_notes_query,(user_id,title,content))
            connection.commit()
            cursor.close()
            connection.close()
            return True,"Notes Saved"
    except Exception as e:
        return False,f'Exception raised in add notes:{e}'
    
#add notes route
@app.route('/notes/addnotes',methods=['GET','POST'])
def add_notes():
    if "id" not in session:
        return redirect('/login')
    #GET request
    if request.method=="GET":
        return render_template('addnotes.html')
    #POST request
    if request.method=="POST":
        title=request.form.get('Title',"No Title")
        content=request.form.get('content',"No Content")
        #store in database
        status,msg=addNotesRecord(
            user_id=session['id'],
            title=title,
            content=content
        )
        if status==True:
            #redirect to notes dashboard
            return render_template('notes.html',msg=msg)
        else:
            return render_template('notes.html',err=msg)

#get notes by id
def getNotesById(notes_id):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor(dictionary=True)
            get_notes_by_id = """SELECT title,content FROM notes where id =%s;"""
            cursor.execute(get_notes_by_id,(notes_id,))
            notes = cursor.fetchone()
            cursor.close()
            connection.close()
            return True,notes
    except Exception as e:
        return False,f'Exception raised in View Notes:{e}'
    
#view notes
@app.route('/notes/view/<int:note_id>')
def view_notes(note_id):
    #get data from database based on notesid
    status,notes = getNotesById(notes_id=note_id)
    if status == True:
        title = notes['title']
        content = notes['content']
        return render_template('viewnotes.html',title=title,content=content)
    else:
        return render_template('notes.html',err=notes)

    
def updateNotesByID(notes_id:int,title:str,content:str):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor()
            update_notes_by_id = """UPDATE notes SET title=%s,content=%s where id=%s;"""
            cursor.execute(update_notes_by_id,(title,content,notes_id))
            connection.commit()
            cursor.close()
            connection.close()
            return True,"Notes Updated"
    except Exception as e:
        return False,f'Exception raised in update Notes:{e}'  
    
@app.route('/notes/edit/<int:note_id>',methods=['GET','POST'])
def edit_notes(note_id):
    if request.method == "GET":
        status,notes = getNotesById(notes_id=note_id)
        if status == True:
            return render_template('updatenotes.html',
                                   title=notes['title'],
                                   content=notes['content'],
                                   notes_id=note_id)
        else:
            return render_template('notes.html',err=notes)
    if request.method == "POST":
        title = request.form.get('title')
        content = request.form.get('content')
        #print(title,content)
        status,msg = updateNotesByID(
            title = title,content=content,notes_id=note_id)
        _,notes = getNotesByUserId(user_id=session['id'])
        if status == True:
            return render_template('notes.html',msg=msg,notes=notes)
        else:
            return render_template('notes.html',err=msg,notes=notes)   
        
def deleteNotesById(notes_id):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor()
            delete_notes_by_id = """delete from notes where id=%s;"""
            cursor.execute(delete_notes_by_id,(notes_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return True,"Notes Deleted"
    except Exception as e:
            return False,f'Exception raised in delete Notes:{e}'

#delete notes route
@app.route('/notes/delete/<int:note_id>',methods=['GET','POST'])
def delete_notes(note_id):
    #delete notes from database based on the note_id
    status,msg = deleteNotesById(notes_id=note_id)
    _,notes = getNotesByUserId(user_id=session['id'])
    if status == True:
        return render_template('notes.html',msg=msg,notes=notes)
    else:
        return render_template('notes.html',err=msg,notes=notes)

#-------------------------------
#          Files routes
#-------------------------------
#fetch the files 
def GetFilesbyUserId(userid):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor(dictionary=True)
            #dictionary = True enables filename to be printed
            #in files page as it fetches fileid and storedname
            get_file_by_userid = """select * from file_data
            where user_id=%s;"""
            cursor.execute(get_file_by_userid,(userid,))
            files=cursor.fetchall()
            cursor.close()
            connection.close()
            return True,files
    except Exception as e:
        return False,f'Exception raised in Files:{e}'

@app.route('/files',methods=['GET','POST'])
def myfiles():
    if "id" not in session:
        return redirect('/login')
    if request.method == "GET":
        userid=session['id']
        #get all the files
        status,files = GetFilesbyUserId(userid=userid)
        print(files)
        print(status)
        if status:
            return render_template('files.html',
                                   files=files)
        else:
            msg = files
            flash(msg,"err")
            return render_template('files.html')
    if request.method == "POST":
        search = request.form.get('searchfiles')
        userid = session['id']
        status,files = GetFilesbyUserId(userid=userid)
        if status == True:
            #filter the files based on the search
            filtered_files = []
            for file in files:
                if search.lower() in file['original_name'].lower():
                    filtered_files.append(file)
            return render_template("files.html",
                                   files=filtered_files)
        else:
            return render_template('files.html',err=files)
    
#check file exist in allowed types
def checkFileAllowed(filename):
    allow_types = ['pdf','doc','jpeg','jpg','png','svg','csv',
                   'xml','txt']
    if '.' in filename and filename.split('.')[1].lower() in allow_types:
        return True
    else:
        return False
    
#check duplicate file in the database
def checkFileDuplicate(userid,filename):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor()
            check_file_duplicate = """select * from file_data
            where stored_name = %s and user_id=%s;"""
            cursor.execute(check_file_duplicate,(filename,
                                                 userid))
            record = cursor.fetchone()
            cursor.close()
            connection.close()
            if record:
                return False,"Duplicate file is present"
            else:
                return True, "Not a Duplicate file"
    except Exception as e:
        return False,f"Exception raised in file: {e}"

#insert files into table
def UploadFileInDB(userid,filename,stored_name,type,size,path):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor()
            insert_filedata_query= """insert into file_data
            (user_id,original_name,stored_name,mime_type,
            size_bytes,storage_path) values(%s,%s,%s,%s,%s,%s);"""
            cursor.execute(insert_filedata_query,
                           (userid,filename,stored_name,
                            type,size,path))
            connection.commit()
            cursor.close()
            connection.close()
            return True,"File Uploaded"
    except Exception as e:
        return False,f'Exceptiom raised in File upload:{e}'

#get file metadata by file_id
def getFileByFileId(fileid):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor(dictionary=True)
            get_file_by_user_id = """select * from file_data
            where id = %s;"""
            cursor.execute(get_file_by_user_id,(fileid,))
            file=cursor.fetchone()
            cursor.close()
            connection.close()
            return True,file
    except Exception as e:
        return False,f'Exception raised in View files:{e}'

#upload file route
@app.route('/files/upload',methods=['GET','POST'])
def uploadFile():
    if "id" not in session:
        return redirect('/login')
    if request.method == "GET":
        return render_template('uploadFile.html')
    #post request
    if request.method == "POST":
        #get file from form
        file = request.files.get('file')
        if file and file.filename != "":
            #check file in allowed types
            filename = file.filename
            if checkFileAllowed(filename=filename):
                #check the valid allowed types of files
                filename_secure=secure_filename(filename)
                #check the file in allowed types
                status,msg = checkFileDuplicate(
                    userid=session['id'],
                    filename= filename_secure
                )
                if status == True:
                    #save the file
                    upload_path = os.path.join('upload',
                                               filename_secure)
                    file.save(upload_path) 
                    #get the file information 
                    file_size = os.path.getsize(upload_path)
                    file_type = os.path.splitext(filename_secure)[1].lower().lstrip('.')
                    #path stored in the DB 
                    filepath = f'/upload/{filename_secure}'
                    #insert file metadata in database
                    status,msg = UploadFileInDB(userid=session['id'],
                                                filename=filename,
                                                stored_name=filename_secure,
                                                type=file_type,
                                                size=file_size,
                                                path=filepath)
                    if status==True:
                        flash(msg,"msg")
                        return redirect('/files')
                    else:
                        flash(msg,"err")
                        return redirect('/files')
                else:
                    flash(msg,"err")
                    return redirect('/files')
            else:
                flash("File type not allowed","err")
                return redirect('/files')
            #render_template -->returns HTML directly to currentURL
            #redirect --> instructs the browser to make a new requesr to 
            #a different URL
        else:
            flash("File not uploaded","err")
            return redirect('/files')
        
#get file metadata by file id
def getFileByFileId(fileid):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor(dictionary=True)
            get_file_by_userid = """select * from file_data
                                where id = %s;"""
            cursor.execute(get_file_by_userid,(fileid,))
            file=cursor.fetchone()
            cursor.close()
            connection.close()
            return True,file
    except Exception as e:
        return False,f'Exception rasied in View File:{e}'

#delete file 
#get file metadata by file id
def deleteFileByFileId(fileid):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor()
            delete_file_by_userid = """delete from file_data
                                where id = %s;"""
            cursor.execute(delete_file_by_userid,(fileid,))
            connection.commit()
            cursor.close()
            connection.close()
            return True,"File Deleted Successfully"
    except Exception as e:
        return False,f'Exception raised in View File:{e}'

import mimetypes
#view file route
@app.route('/files/view/<file_id>')
def viewFile(file_id):
    if "id" not in session:
        return redirect('/login')
    if request.method == "GET":
        #get the file by file_id
        status,file = getFileByFileId(fileid=file_id)
        if status == True:
            secure_filename = file['stored_name']
            mime_type,_ = mimetypes.guess_type(secure_filename)
            return send_file(
                f'upload/{secure_filename}',
                mimetype=mime_type,
                as_attachment=False
            )
        else:
            flash(file,'err')
            return redirect('/files')   

#download file route
@app.route('/files/download/<file_id>')
def downloadFile(file_id):
    if "id" not in session:
        return redirect('/login')
    if request.method == "GET":
        #get file by file_id
        status,file = getFileByFileId(fileid=file_id)
        if status == True:
            secure_filename = file['stored_name']
            mime_type, _ = mimetypes.guess_type(
                secure_filename)
            return send_file(
                f'upload/{secure_filename}',
                mimetype=mime_type,
                as_attachment=True
            )
        else:
            flash(file,"err")
            return redirect('/files')

#delete file route
@app.route('/files/delete/<file_id>')
def deleteFile(file_id):
    if "id" not in session:
        return redirect('/login')
    if request.method == "GET":
            #get file by file_id
            status,msg = deleteFileByFileId(fileid=file_id)
            if status == True:
                flash(msg,"msg")
                return redirect('/files')
            else:
                flash(msg,"err")
                return redirect('/files')

#-------------------------------
#         Logout route
#-------------------------------

@app.route("/logout",methods=['GET'])
def logout():
    #if id in session
    session.pop('id',None)
    session.pop('name',None)
    session.pop('email',None)
    return redirect('/login')
    
if (__name__ == "__main__"):
    app.run(host="0.0.0.0",
            port=5100,
            debug=True)
    
#Registration Flow:
#User --> register.html <--> Registration Form --> 
# POST <-->Python  -->Collecting Data -->Validating -> 
# Verifying -->Password to Password Hash <-->MYSQL Table

#HTML <-> Python <-> MYSQL
#Registration FLow
#User has to click on Get Started
#Register page
#Name,Email,Password,Confirm Password and submit
#verifyDuplicateEmail() --> if account not exists
#generate OTP
#send email with otp
#redirect to verify.html
#enter the otp receiveed on email
#if the otp matches with the session otp
#it will redirect to login
#if they are not matching,it redirects with a message


#@app.route('/register',methods = ['GET','POST'])
#def register():
#    if request.method == "GET":
#       renderHTMLPage()
#    elif request.method == "POST":
#        collectUserData()
#        validateUserData()
#        displayErrors()
#        status = verifyAccountExist()
#        if status:
#            insertRecord()
#        else:
#            displayErrorMessage()