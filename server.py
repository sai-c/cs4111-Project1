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
from openpyxl import load_workbook
from werkzeug.security import check_password_hash, generate_password_hash

import os
from sqlalchemy import *
from sqlalchemy import exc
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, jsonify, session, url_for
from psycopg2.errors import UniqueViolation, CheckViolation


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

@app.route('/companies', methods=['GET', 'POST'])
def companies():
  if request.method == "POST":
    cname = request.form['cname']
    cursor = g.conn.execute("SELECT * FROM Company WHERE name=%s", (cname))
    results = list(cursor)[0]
    cursor.close()

    cursor = g.conn.execute("""
      SELECT Benefit.title AS title, Benefit.description AS description FROM Benefit JOIN (
      SELECT * FROM
      Company JOIN Uses_Benefit ON Company.name=Uses_Benefit.name
      WHERE Company.name=%s
      ) AS C ON Benefit.title=C.title
      """, (cname))
    context = dict(company = results, benefits = list(cursor))
    return render_template("company.html", **context)
  cursor = g.conn.execute("SELECT * FROM Company")
  names = []
  for result in cursor:
    names.append(result)
  cursor.close()
  context = dict(data = names)
  return render_template("companies.html", **context)

@app.route('/specializations', methods=['GET', 'POST'])
def specializations():
  cursor = g.conn.execute("SELECT * FROM Specialization")
  names = []
  for result in cursor:
    names.append(result)
  cursor.close()
  context = dict(data = names)
  return render_template("specializations.html", **context)



@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    if 'user_id' not in session.keys():
      return redirect(url_for('login'))
    
    if 'comment' in request.form.keys():
      content = request.form['comment']
      cursor = g.conn.execute(
                      "INSERT INTO Comment (cid, email, pid, timestamp, content) VALUES (DEFAULT, %s, %s, now(), %s)",
                      (session['user_id'], request.form['pid'], content),
      )
      cursor = g.conn.execute("SELECT * FROM Post_FT WHERE aid IS NOT NULL")
      names = []
      for result in cursor:
        names.append(result)
      cursor.close()
      context = dict(data = names)
      return render_template("index.html", **context, logged_in=True)
    # filtering posts
    else:
      loc = ''
      exp = '' 
      gdr = '' 
      edu = ''
      if 'group1' in request.form.keys():
        loc = request.form['group1']
      if 'group2' in request.form.keys():  
        exp = request.form['group2']
      if 'group3' in request.form.keys():  
        gdr = request.form['group3']
      if 'group4' in request.form.keys():  
        edu = request.form['group4']

      print(f"loc: {loc}\nexp: {exp}\ngdr: {gdr}\nedu: {edu}\n")
      q = """SELECT * FROM Post_FT JOIN Users ON Post_FT.email = Users.email 
      WHERE aid IS NOT NULL
      """
      tup = ()
      if loc:
        q += " AND Post_FT.city = %s"
        tup += (loc,)
      
      if exp:

        if exp == "New Grad":
          low = 0
          high = 1
        
        if exp == "Mid Level":
          low = 2
          high = 4
        
        if exp == "Senior Level":
          low = 5
          high = 10

        q += " AND Users.yoe BETWEEN %s AND %s"
        tup += (low, high,)

      if gdr:
        q += " AND Users.gender = %s"
        tup += (gdr, )

      if edu:
        if edu == "Bachelors":
          first = "BS"
          second = "BA"

        if edu == "Masters":
          first = "MA"
          second = "MS"

        if edu == "Doctorate":
          first = "PhD"
          second = "PhD"

        q += " AND (Users.education = %s OR Users.education = %s)"
        tup += (first, second,)

      cursor = g.conn.execute(q, tup)
      names = []
      for result in cursor:
        names.append(result)
      cursor.close()
      context = dict(data = names)
      return render_template("index.html", **context, logged_in=True)

  cursor = g.conn.execute("SELECT * FROM Post_FT WHERE aid IS NOT NULL")
  names = []
  for result in cursor:
    names.append(result)
  cursor.close()

  #
  context = dict(data = names)
  if 'user_id' in session.keys():
    return render_template("index.html", **context, logged_in=True)
  else:
    return render_template("index.html", **context, logged_in=False)


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
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
      if request.form['form-type'] == "ft":
        email = session['user_id']
        role = request.form['role']
        title = request.form['title']
        level = request.form['level']
        type = request.form['type']
        city = request.form['city']
        state = request.form['state']
        base = request.form['base']
        stock = request.form['stock']
        bonus = request.form['bonus']
        description = request.form['description']
        specialization = request.form['specialization']
        company = request.form['company']

        level2 = g.conn.execute(
          "SELECT * FROM Level WHERE title=%s AND level=%s AND role=%s AND type=%s",
          (title, level, role, type)
        )
        if len(list(level2)) == 0:
          level2 = g.conn.execute(
            "INSERT INTO Level VALUES (DEFAULT, %s, %s, %s, %s)",
            (role, title, level, type)
          )

        lid = g.conn.execute(
          "SELECT id FROM Level WHERE title=%s AND level=%s AND role=%s AND type=%s",
          (title, level, role, type)
        )
        lid = list(lid)[0][0]
        addcompany = g.conn.execute(
            "INSERT INTO Company VALUES (%s, NULL, NULL, %s, %s) ON CONFLICT DO NOTHING",
            (company, city, state)
        )
        linking = g.conn.execute(
                          "INSERT INTO Uses_Level VALUES (%s, %s) ON CONFLICT DO NOTHING",
                          (company, lid),
        )
        post = g.conn.execute("""INSERT INTO Post_FT(pid, aid, email, lid, city, state, base, stock, bonus, sname, cname, timestamp, description)
VALUES(DEFAULT, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), %s);""",
                          (session['user_id'], lid, city, state, base, stock, bonus, specialization, company, description),
        )

      if request.form['form-type'] == "intern":
        email = session['user_id']
        city = request.form['city']
        state = request.form['state']
        hourly = request.form['base']
        bonus = request.form['bonus']
        description = request.form['description']
        company = request.form['company']

        addcompany = g.conn.execute(
            "INSERT INTO Company VALUES (%s, NULL, NULL, %s, %s) ON CONFLICT DO NOTHING",
            (company, city, state)
        )
        post = g.conn.execute("""INSERT INTO Post_Intern(pid, aid, email, city, state, hourly, bonus, cname, timestamp, description)
VALUES(DEFAULT, NULL, %s, %s, %s, %s, %s, %s, now(), %s);""",
                          (session['user_id'], city, state, hourly, bonus, company, description),
        )



      specs = g.conn.execute("SELECT DISTINCT name FROM Specialization").fetchall()
      specs = [x[0] for x in specs]

      return render_template('add.html', dsk="", input="", color="green", errorText="Successfully created", show = True, specs = specs)
    specs = g.conn.execute("SELECT DISTINCT name FROM Specialization").fetchall()
    specs = [x[0] for x in specs]
    companies = list(g.conn.execute("SELECT DISTINCT name FROM Company"))
    companies = [x[0] for x in companies]
    print(companies)
    return render_template('add.html', dsk="", input="", color="", errorText="", show = False, specs=specs, companies=companies)


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
        email = request.form['email']
        password = request.form['password']
        user = g.conn.execute(
            "SELECT * FROM Users WHERE email = %s", (email,)
        ).fetchone()
        if user is None:
            return render_template('login.html', dsk="", input="", color="red", errorText="Incorrect User", show = True)
        elif not check_password_hash(user['password'], password):
            return render_template('login.html', dsk="", input="", color="red", errorText="Incorrect Password", show = True)
        session.clear()
        session['user_id'] = email
        return redirect(url_for('index'))
    return render_template('login.html', dsk="", input="", color="", errorText="", show = False)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

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
                          "INSERT INTO Users (email, password, name, gender, yoe, education) VALUES (%s, %s, %s, %s, %s, %s)",
                          (email, password, name, gender, yoe, education),
          )
        except exc.IntegrityError as e:
          if isinstance(e.orig, UniqueViolation):
            return render_template('signup.html', dsk="", input="", color="red", errorText="User already exists", show = True)
          if isinstance(e.orig, CheckViolation):
            return render_template('signup.html', dsk="", input="", color="red", errorText="Invalid input", show = True)

        return render_template('signup.html', dsk="", input="", color="green", errorText="Successfully created", show = True)
    return render_template('signup.html', dsk="", input="", color="", errorText="", show = False)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
  if request.method == 'POST':
    if request.form['type'] == "intern":
        aid = g.conn.execute("SELECT aid FROM Admin WHERE email = %s", (session['user_id'] ,)).fetchone()[0]
        print("FORM: ", request.form['pid'])
        pid = request.form['pid']
        cursor = g.conn.execute(
    """UPDATE Post_Intern
    SET aid = %s
    WHERE pid = %s
    """, (aid, pid,))

    if request.form['type'] == "ft":
        aid = g.conn.execute("SELECT aid FROM Admin WHERE email = %s", (session['user_id'] ,)).fetchone()[0]
        print("FORM: ", request.form['pid'])
        pid = request.form['pid']
        cursor = g.conn.execute(
    """UPDATE Post_FT
    SET aid = %s
    WHERE pid = %s
    """, (aid, pid,))


    cursor = g.conn.execute("SELECT * FROM Post_FT WHERE aid is NULL")
    ft_data = list(cursor)
    cursor.close()

    cursor = g.conn.execute("SELECT * FROM Post_Intern WHERE aid is NULL")
    intern_data = list(cursor)
    cursor.close()

    context = dict(ft_data = ft_data, intern_data = intern_data)
    return render_template("admin.html", **context)


    
  if 'user_id' not in session.keys():
    return "Not Logged In"
  cursor = g.conn.execute("SELECT * FROM Admin WHERE email=%s", (session['user_id'] ,))
  if len(cursor.fetchall()) == 0:
    return "Not Admin"
  cursor = g.conn.execute("SELECT * FROM Post_FT WHERE aid is NULL")
  ft_data = list(cursor)
  cursor.close()

  cursor = g.conn.execute("SELECT * FROM Post_Intern WHERE aid is NULL")
  intern_data = list(cursor)
  cursor.close()

  context = dict(ft_data = ft_data, intern_data = intern_data)
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


  app.secret_key = 'test'
  run()

