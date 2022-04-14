#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
from werkzeug.security import check_password_hash, generate_password_hash

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, jsonify, session, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "vhc2109"
DB_PASSWORD = "2008"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/internships', methods=['GET', 'POST'])
def internships():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """
  if request.method == "POST":
    cname="Apple"
    cursor = g.conn.execute("SELECT * FROM Post_Intern WHERE lower(cname)=%s", (request.form['cname'].lower(), ))
    names = []
    for result in cursor.fetchall():
        names.append(result)
    cursor.close()

    #
    context = dict(data = names)
    return render_template("internships.html", **context)
  #
  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT * FROM Post_Intern WHERE aid IS NOT NULL")
  names = []
  for result in cursor:
    names.append(result)
  cursor.close()

  #
  context = dict(data = names)
  return render_template("internships.html", **context)

@app.route('/')
def index():
    cursor = g.conn.execute("SELECT * FROM Post_FT WHERE aid IS NOT NULL")
    names = []
    for result in cursor:
      names.append(result)
    cursor.close()

    #
    context = dict(data = names)
    return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print(name)
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  g.conn.execute(text(cmd), name1 = name, name2 = name);
  return redirect('/')

@app.route('/post/<id>')
def post(id):    
  cursor = g.conn.execute("SELECT * FROM Post_FT WHERE pid=%s", (id,))
  return jsonify(cursor.fetchone())

@app.route('/comments/<id>')
def comments(id):
  cursor = g.conn.execute("SELECT * FROM Comment WHERE pid=%s", (id,))
  return jsonify(cursor.fetchall())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        user = g.conn.execute(
            'SELECT * FROM Users WHERE username = ?', (username,)
        ).fetchone()
        if user is None:
            return render_template('login.html', dsk="", input="", color="red", errorText="Incorrect User", show = True)
        elif not check_password_hash(user['password'], password):
            return render_template('login.html', dsk="", input="", color="red", errorText="Incorrect Password", show = True)
        session.clear()
        session['user_id'] = username
        return redirect(url_for('index.dashboard'))
    return render_template('login.html', dsk="", input="", color="", errorText="", show = False)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('cs4111-Project1.index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        name = request.form['name']
        yoe = request.form['yoe']
        gender = request.form['gender']
        education = request.form['education']

        try:
            cursor = g.conn.execute(
                            "INSERT INTO Users (email, password, name, gender, yoe, education) VALUES (%s, %s, %s, %s, ?, ?, ?, ?)",
                            (email, password, name, gender, yoe, education),
            )
            g.conn.commit()
        except Exception as e:
            print(e)
            return render_template('signup.html', dsk="", input="", color="red", errorText="User already exists", show = True)

        return render_template('signup.html', dsk="", input="", color="green", errorText="Successfully created", show = True)
    return render_template('signup.html', dsk="", input="", color="", errorText="", show = False)

@app.route('/admin', methods=['GET', 'POST'])
def admin():

  if request.method == 'POST':
    print("FORM: ", request.form['pid'])
    pid = request.form['pid']
    cursor = g.conn.execute(
"""UPDATE Post_Intern
SET aid = 1
WHERE pid = %s
""", (pid,))
    cursor = g.conn.execute("SELECT * FROM Post_Intern WHERE aid is NULL")
    names = []
    for result in cursor:
      names.append(result)
    cursor.close()

    context = dict(data = names)
    return render_template("admin.html", **context)

  cursor = g.conn.execute("SELECT * FROM Post_Intern WHERE aid IS NULL")
  names = []
  for result in cursor:
    names.append(result)
  cursor.close()

  context = dict(data = names)
  return render_template("admin.html", **context)


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on: ", HOST, "port: ", PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
