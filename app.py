import re
from multiprocessing import connection

import pymysql
from flask import Flask, request, render_template, session, redirect, jsonify
from utils import query
from utils.getHomeData import getHomeData

app = Flask(__name__)
app.secret_key = "session"

# 登录页面
@app.route('/', methods=['GET'])
def index():
    return redirect('/login')

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        # 将表单数据转换为字典格式
        request.form = dict(request.form)
        # 查询数据库中是否有该用户
        users = query.querys('SELECT * FROM user WHERE email=%s AND password=%s', [request.form['email'], request.form['password']], 'select')
        if len(users):
            session['email'] = request.form['email']
            return redirect('/home')
        else:
            return render_template('error.html', message='邮箱或密码错误')

# 退出登录
@app.route('/loginOut')
def loginOut():
    session.clear()
    return redirect('/login')

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        # 将表单数据转换为字典格式
        request.form = dict(request.form)
        # 判断两次密码是否相同
        if request.form['password'] != request.form['passwordChecked']:
            return render_template('error.html', message='两次密码不符合')
        # 查询数据库中是否已经存在该用户
        users = query.querys('SELECT * FROM user WHERE email=%s', [request.form['email']], 'select')
        if len(users):
            return render_template('error.html', message='该用户已被注册')
        else:
            # 将用户信息插入数据库中
            query.querys('INSERT INTO user(email,password) VALUES (%s,%s)',[request.form['email'], request.form['password']])
            session['email'] = request.form['email']
            return redirect('/login')

# 首页
@app.route('/home', methods=['GET', 'POST'])
def home():
    email = session.get('email')
    sum_applicants, sum_recruits, rate, sum_position = getHomeData()
    return render_template(
        'index.html',
        email=email,
        sum_applicants=sum_applicants,
        sum_recruits=sum_recruits,
        rate=rate,
        sum_position=sum_position
    )

# 职位分析页面
@app.route('/position_a')
def position_a():
    email = session.get('email')
    return render_template('position_a.html', email=email)

# 职位分析页面
@app.route('/position_b')
def position_b():
    email = session.get('email')
    return render_template('position_b.html', email=email)

# 部门分析页面
@app.route('/department_a')
def department_a():
    email = session.get('email')
    return render_template('department_a.html', email=email)

# 部门分析页面
@app.route('/department_b')
def department_b():
    email = session.get('email')
    return render_template('department_b.html', email=email)

# 学历分析页面
@app.route('/degree')
def degree():
    email = session.get('email')
    return render_template('degree.html', email=email)

# 地区分析页面
@app.route('/area')
def area():
    email = session.get('email')
    return render_template('area.html', email=email)

# 专业分析页面
@app.route('/major')
def major():
    email = session.get('email')
    return render_template('major.html', email=email)
#十大热门专业
@app.route('/hot')
def hot():
    email = session.get('email')
    return render_template('hot.html', email=email)

@app.route('/degree_data')
def degree_data():
    email = session.get('email')
    return render_template('degree_data.html', email=email)

# 访问限制
@app.before_request
def before_requre():
    pat = re.compile(r'^/static')
    if re.search(pat, request.path):
        return
    if request.path == "/login":
        return
    if request.path == "/registry":
        return
    email = session.get('email')
    if email:
        return None
    return redirect('/login')

# 数据接口1
@app.route('/chart_data')
def chart_data():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    query = "SELECT * FROM result_gk"
    cursor.execute(query)
    data = cursor.fetchall()
    result = {"area": [], "number_of_position": [], "number_of_recruits": [], "number_of_applicants": []}
    for d in data:
        result["area"].append(d[0])
        result["number_of_position"].append(d[1])
        result["number_of_recruits"].append(d[2])
        result["number_of_applicants"].append(d[3])
    conn.close()
    return jsonify(result)

# 数据接口2
@app.route('/data')
def get_data():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = "SELECT position, number_of_recruits FROM job_position ORDER BY CAST(number_of_recruits AS UNSIGNED) DESC LIMIT 10"
    cursor.execute(sql)
    results = cursor.fetchall()
    data = {'positions': [x[0] for x in results], 'recruits': [x[1] for x in results]}
    conn.close()
    return jsonify(data)

# 数据接口3
@app.route('/data1')
def get_data1():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = "SELECT position, number_of_applicants FROM job_position ORDER BY CAST(number_of_applicants AS UNSIGNED) DESC LIMIT 10"
    cursor.execute(sql)
    results = cursor.fetchall()
    data1 = {'positions': [x[0] for x in results], 'applicants': [x[1] for x in results]}
    conn.close()
    return jsonify(data1)

# 数据接口4
@app.route('/data2')
def get_data2():
    # 连接数据库
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)

    cursor = conn.cursor()
    sql = "SELECT area, COUNT(DISTINCT position) AS position_count FROM job_gk WHERE number_of_applicants = 0 GROUP BY area HAVING COUNT(*) > 0"
    # 执行查询
    cursor.execute(sql)
    # 获取查询结果
    data = cursor.fetchall()
    # 关闭数据库连接
    conn.close()
    # 处理数据，将number_of_applicants为0的数据转化为0
    data = [{'area': item[0], 'count': item[1] if item[1] > 0 else 0} for item in data]
    # 返回JSON格式数据
    return jsonify(data)



@app.route('/jobs')
def get_jobs():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = "SELECT position_code, area, position, degree, major, number_of_recruits FROM job_gk WHERE number_of_applicants=0"
    cursor.execute(sql)
    jobs = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'jobs': jobs})

# 数据接口6
@app.route('/data4')
def get_data4():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = "SELECT department, number_of_recruits FROM job_department ORDER BY CAST(number_of_recruits AS UNSIGNED) DESC LIMIT 10"
    cursor.execute(sql)
    results = cursor.fetchall()
    data4 = {'positions': [x[0] for x in results], 'recruits': [x[1] for x in results]}
    conn.close()
    return jsonify(data4)

# 数据接口7
@app.route('/data5')
def get_data5():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = "SELECT department, number_of_applicants FROM job_department ORDER BY CAST(number_of_applicants AS UNSIGNED) DESC LIMIT 10"
    cursor.execute(sql)
    results = cursor.fetchall()
    data5 = {'positions': [x[0] for x in results], 'applicants': [x[1] for x in results]}
    conn.close()
    return jsonify(data5)

# 数据接口8
@app.route('/data6')
def get_data6():
    # 连接数据库
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)

    cursor = conn.cursor()
    sql = "SELECT area, COUNT(DISTINCT department) AS department_count FROM job_gk WHERE number_of_applicants = 0 GROUP BY area HAVING COUNT(*) > 0"
    # 执行查询
    cursor.execute(sql)
    # 获取查询结果
    data = cursor.fetchall()
    # 关闭数据库连接
    conn.close()
    # 处理数据，将number_of_applicants为0的数据转化为0
    data = [{'area': item[0], 'count': item[1] if item[1] > 0 else 0} for item in data]
    # 返回JSON格式数据
    return jsonify(data)

@app.route('/education_pie')
def education_pie():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = "SELECT degree, COUNT(*) FROM job_gk GROUP BY degree"
    cursor.execute(sql)
    results = cursor.fetchall()
    data = [{'value': result[1], 'name': result[0]} for result in results]
    return jsonify(data)


@app.route('/jobs1')
def get_jobs1():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = "SELECT position_code, area,  department, degree, major, number_of_recruits FROM job_gk WHERE number_of_applicants=0"
    cursor.execute(sql)
    jobs = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'jobs1': jobs})

@app.route('/education_bar')
def education_bar():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = "SELECT degree, SUM(number_of_recruits) AS recruit_count, COUNT(position) AS position_count, COUNT(DISTINCT department) AS department_count FROM job_gk GROUP BY degree  ORDER BY recruit_count DESC"

    cursor.execute(sql)
    results = cursor.fetchall()

    # 将查询结果转换为前端需要的格式
    data = {}
    data['degree'] = [r[0] for r in results]
    data['recruit_count'] = [r[1] for r in results]
    data['position_count'] = [r[2] for r in results]
    data['department_count'] = [r[3] for r in results]

    return jsonify(data)

@app.route('/education_line')
def education_line():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = "SELECT degree, SUM(number_of_applicants) AS applicants_count FROM job_gk GROUP BY degree ORDER BY applicants_count DESC;"
    cursor.execute(sql)
    results = cursor.fetchall()

    # 将查询结果转换为前端需要的格式
    data = {}
    data['degree'] = [r[0] for r in results]
    data['applicants_count'] = [r[1] for r in results]

    return jsonify(data)


@app.route('/hotarea', methods=['GET'])
def hotarea():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = "SELECT area, number_of_applicants  FROM result_gk"
    cursor.execute(sql)
    result = cursor.fetchall()
    datadict = []

    for row in result:
        datadict.append({'name': row[0], 'value': row[1]})

    cursor.close()
    conn.close()

    return jsonify(datadict)

@app.route('/major_a')
def major_a():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = ("SELECT position, SUM(number_of_recruits) AS total_recruits, SUM(number_of_applicants) AS total_applicants FROM job_gk WHERE major LIKE '%不限%' GROUP BY position ORDER BY total_applicants DESC LIMIT 10")
    cursor.execute(sql)
    data = cursor.fetchall()
    positions = []
    recruits = []
    applicants = []
    for row in data:
        positions.append(row[0])
        recruits.append(row[1])
        applicants.append(row[2])

    return jsonify({'positions': positions, 'recruits': recruits, 'applicants': applicants})

@app.route('/major_b')
def major_b():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    cursor.execute("SELECT department, SUM(number_of_recruits) AS total_recruits, SUM(number_of_applicants) AS total_applicants FROM job_gk WHERE major LIKE '%不限%' GROUP BY department ORDER BY total_applicants DESC LIMIT 10")
    data = cursor.fetchall()
    departments = []
    recruits = []
    applicants = []
    for row in data:
        departments.append(row[0])
        recruits.append(row[1])
        applicants.append(row[2])

    return jsonify({'departments': departments, 'recruits': recruits, 'applicants': applicants})

@app.route('/api/major_distribution')
def major_distribution():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = """
        SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(major, '、', n), '、', -1)) AS major, COUNT(*) AS count
        FROM (
            SELECT major, 1 + LENGTH(major) - LENGTH(REPLACE(major, '、', '')) AS n
            FROM job_gk
            WHERE major != '不限' AND major NOT LIKE '%门%'
        ) AS t
        GROUP BY major
        ORDER BY count DESC
        LIMIT 10
    """
    cursor.execute(sql)
    results = cursor.fetchall()
    data = []
    for result in results:
        data.append({'value': result[1], 'name': result[0]})
    return jsonify(data)

@app.route('/major_num')
def get_num():
    conn = pymysql.connect(host='localhost', user='root', password='991109', database='fb', port=3306)
    cursor = conn.cursor()
    sql = '''
    SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(major, '、', n), '、', -1)) AS major, 
    SUM(number_of_recruits) AS total_recruits,
    SUM(number_of_applicants) AS total_applicants
    FROM (
        SELECT major, 1 + LENGTH(major) - LENGTH(REPLACE(major, '、', '')) AS n, number_of_recruits, number_of_applicants
        FROM job_gk
        WHERE major != '不限' AND major NOT LIKE '%门%'
    ) AS t
    GROUP BY major
    ORDER BY total_recruits DESC
    LIMIT 10;
    '''
    cursor.execute(sql)
    data = cursor.fetchall()
    result = []
    for item in data:
        result.append({'major': item[0], 'total_recruits': item[1], 'total_applicants': item[2]})
    return jsonify(result)




if __name__ == "__main__":
    app.run(debug=True)