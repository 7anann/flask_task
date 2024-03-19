from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy


from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token)

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = "secret-key"


jwt = JWTManager(app)

DATABASE_URI = "sqlite:///testcases.db"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

db = SQLAlchemy(app)

class TestCases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    test_asset = db.Column(db.String, nullable=True)
    dateCreated = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"Test Case('{self.id}', '{self.Title}')"

class ExecResults(db.Model):
    res_id = db.Column(db.Integer, primary_key=True)
    testcase_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=False)
    result = db.Column(db.String, nullable=False)
    exec_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    testcase = db.relationship('TestCases')

class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # user_data = request.form
        id = request.form["id"]
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        new_user = user(username=username, email=email, id=id, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return 'There was an error while adding the user'

    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    users = user.query.all()
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        for userr in users:
            if userr.username == username and userr.password == password:
                #return redirect(url_for('mainMenu'))
                ret = {
                    'access_token': create_access_token(identity=username),
                    'refresh_token': create_refresh_token(identity=username)
                }
                return jsonify(ret)

    return render_template('login.html')

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200


@app.route('/testcases', methods=['GET'])
#@jwt_required()
def get_testcases():
    if request.method == 'GET':
        testcases = TestCases.query.all()
        return render_template('tasks.html', testcases=testcases)

@app.route('/test', methods=['GET','POST'])
#@jwt_required()
def get_specific_testcase():
     if request.method == 'POST':
        testcase_id = request.form['id']

        return redirect(url_for('show_testcase_details',testcase_id=testcase_id))

     else:
        return render_template('single_task.html')

@app.route('/taskdetails/<int:testcase_id>', methods=['GET'])
#@jwt_required()
def show_testcase_details(testcase_id=None):
    try:
        if testcase_id is None:
            return redirect(url_for('get_specific_testcase'))

        testcase_id = int(testcase_id)
        get_testcase = TestCases.query.get(testcase_id)

        if not get_testcase:
            return 'There was a problem'
        return render_template('show_details.html',testcases=get_testcase)
    except TypeError:
        return 'Test case id is invalid integer'


@app.route('/add', methods=['GET','POST'])
#@jwt_required()
def add():
    if request.method == 'POST':
        id = request.form['id']
        title = request.form['Title']
        desc = request.form['description']
        test_asset = request.form['test_asset']
        new_testcase = TestCases(id=id, Title=title, description=desc, test_asset=test_asset)

        try:
            db.session.add(new_testcase)
            db.session.commit()
            return redirect('/testcases')
        except:
            return 'There was an error while adding the test case'
    else:
        return render_template("add.html")

@app.route('/delete', methods=['POST','GET'])
#@jwt_required()
def delete():
    if request.method == 'POST':
        idd = request.form['id']
        testcase_del = TestCases.query.get(idd)

        db.session.delete(testcase_del)
        db.session.commit()
        return redirect('/testcases')

    else:
        return render_template('delete.html')

@app.route('/update', methods=['POST','GET'])
#@jwt_required()
def update():
    if request.method == 'POST':
        idd = request.form['id']
        testcase_upd = TestCases.query.get(idd)
        testcase_upd.Title = request.form['Title']
        testcase_upd.description = request.form['description']
        testcase_upd.test_asset = request.form['test_asset']

        db.session.commit()
        return redirect('/testcases')

    else:
        return render_template('update.html')

#------------------------------------------------------------------

@app.route('/showresults', methods=['GET'])
#@jwt_required()
def show_results():
    if request.method == 'GET':
        results = ExecResults.query.all()
        return render_template('results.html', results=results)

@app.route('/addexec', methods=['GET','POST'])
#@jwt_required()
def add_execution_result():
    if request.method == 'POST':
        test_case_id = request.form['testcase_id']
        res = request.form['result']
        test_asset = request.form['test_asset']

        test_case = TestCases.query.get(test_case_id)

        if test_case.test_asset != test_asset:
            return 'Test asset does not exist'

        new_exec_res = ExecResults(testcase_id=test_case_id,result=res)

        try:
            db.session.add(new_exec_res)
            db.session.commit()
            return redirect('/showresults')
        except:
            return 'There was an error while adding the execution result'
    else:
        return render_template("addexec.html")

@app.route('/execres', methods=['GET','POST'])
#@jwt_required()
def get_execution_results():
    try:

        if request.method == 'POST':
            test_asset = request.form['test_asset']

            return redirect(url_for('show_result_details', test_asset=test_asset))

        else:
            return render_template('single_asset.html')


    except:
        return 'There was an error retrieving execution results'

@app.route('/resultdetails/<test_asset>', methods=['GET'])
#@jwt_required()
def show_result_details(test_asset=None):
    try:
        if test_asset is None:
            return redirect(url_for('get_specific_testcase'))

        get_test_asset = (
            db.session.query(ExecResults, TestCases).join(TestCases,
                             ExecResults.testcase_id == TestCases.id).filter(TestCases.test_asset == test_asset).all()

        )
        print(get_execution_results)
        if not get_test_asset:
            return 'There was a problem'
        return render_template('show_result_details.html',testresults=get_test_asset)
    except TypeError:
        return 'Test asset id is invalid'



db.create_all()
app.run(debug=True)