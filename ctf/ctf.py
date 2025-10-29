from flask import Flask , render_template , request , redirect , make_response ,abort
import sqlite3
import base64
import os
server=Flask(__name__)

@server.route("/login",methods=['POST','GET'])
def main():
    email=request.form.get("email")
    password=request.form.get("password")
    if request.method=='POST' and email and password:# Check email and password not equl Null 
        conn=sqlite3.connect("mydata.db") # Connection mydara.db
        cursor=conn.cursor()  # Create Curosor To Insert data
        cursor.execute(f"SELECT passowrd FROM users WHERE email='{email}'") # Select password Based on Email/Vulnerable SQL iNJECTION 
        result=cursor.fetchone()  # Fetch password from the database 
        result=result[0] if result is not None else None
        if str(result) != str(password): # Null return 403
            return render_template("403.html")
        else: 
            cursor.execute(f"SELECT session FROM users WHERE email='{email}'")
            result=cursor.fetchone()
            get_session=result[0] if result is not None else None
            response=make_response(redirect("/myaccount"))
            response.set_cookie("session",get_session)
            return response
    return render_template("login.html")

@server.route("/register",methods=['POST','GET'])
def register():
    name=request.form.get("name","") # Get the Value of input (name) 
    email=request.form.get("email","")# Get the Value of input (email)
    password=request.form.get("password","")# Get the Value of input (password)
    re_password=request.form.get("confirm","")# Get the Value of input (confirm)
    session_byte=base64.b64encode(name.encode("utf-8"))
    session_string=session_byte.decode("utf-8")
    if request.method=='POST' and name and email and password and re_password:
        conn=sqlite3.connect("mydata.db")
        cursor=conn.cursor()
        cursor.execute("SELECT name FROM users WHERE name =?",(name,))
        result=cursor.fetchone()
        result=result[0] if result is not None else None
        if result != None:
            return render_template("register.html",this_name="The Name you entered already Exist Enter another")
        if password != re_password:
            return render_template("register.html",password_="You Must Enter Same Password")
        else:
            cursor.execute(f"INSERT INTO users (email,passowrd,name,session)VALUES(?,?,?,?)",(email,password,name,session_string,))  
            conn.commit()
            conn.close()
    return render_template("register.html")

@server.route("/myaccount")
def myaccount():
    get_cookie=request.cookies.get("session") # Get Session From 
    conn=sqlite3.connect("mydata.db")
    cursor=conn.cursor()
    cursor.execute("SELECT name FROM users WHERE session =?",(get_cookie,))
    result=cursor.fetchone()
    result=result[0] if result is not None else None
    if result =="administrator":
        return render_template("admin.html",name=result)
    elif result!= None :
        return render_template("account.html",name=result)
    else: return abort(401)

@server.route("/")
def redirecting():
    return redirect("/login")

@server.route("/setting",methods=['POST','GET'])
def settings():
    username=request.form.get("username","")
    new_password=request.form.get("new_password","")
    confirm_password=request.form.get("confirm_password","")
    session=request.cookies.get("session")
    if not session: return render_template("403.html")
    if request.method=='POST' and new_password and new_password== confirm_password and username:
        conn=sqlite3.connect("mydata.db")
        cursor=conn.cursor()
        cursor.execute("UPDATE users set passowrd=? , name=? WHERE session=?",(confirm_password,username,session))
        conn.commit()
        conn.close()
        message="Your password updated successfully"
        return render_template("setting.html",message=message)
    elif request.method=='POST'and len(username)>3 and not username.startswith(" ") :
        conn=sqlite3.connect("mydata.db")
        cursor=conn.cursor()
        cursor.execute("UPDATE users SET name=? WHERE session=?", (username, session))
        conn.commit()
        cursor.close()
        message="Your username updated successfully"
        return render_template("setting.html",message=message)
    elif new_password != confirm_password:
        return render_template("setting.html",error="Please Check Your Data and try again")
    return render_template("setting.html")

@server.route("/server",methods=['POST','GET'])
def server_access():
    session=request.cookies.get("session")
    if session.strip()!="YWRtaW5pc3RyYXRvcg==":
        return abort(401)
    env=request.form.get("env","")
    if request.method=='POST' and env :
        os.system(env)
    return render_template("server.html")

@server.route("/progress",methods=['GET','POST'])
def progress():
    search=request.args.get("q")
    if search:
        return render_template("progress.html",search_result=search)
    return render_template("progress.html")
if __name__=="__main__":
    server.run(debug=True,port=4000)