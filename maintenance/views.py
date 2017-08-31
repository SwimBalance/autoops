from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .tools.ostools import Task
from django.db import connection;

connection.close()
from .tools.dbtools import dictfetchall
import datetime
from django.urls import reverse
from .tools.ansibletools import AnsibleAPI
import threading
import multiprocessing
import time
import uuid


# 给页面增加验证功能装饰器,如果浏览器cookies中没有用户信息，返回主页面
def login_auth(f):
    def decorator(*args):
        userinfo = args[0].COOKIES.get('loginname')
        print('userinfo=', userinfo)
        if userinfo is not None:
            return f(*args)
        else:
            print(reverse('APP:login'))
            return HttpResponseRedirect(reverse('APP:login'))
            # return HttpResponseRedirect(reverse("login"))
            # return render(args[0], 'maintenance/index.html')

    return decorator


# 显示登录主页
@csrf_exempt
def login(request):
    if request.method == 'POST':
        print("post method!")
        username = request.POST.get('userid', '')
        password = request.POST.get('password', '')
        print("==xxxx==")
        print(username, password)
        print("==xxxx==")
        cursor = connection.cursor()
        sqlsatement = "SELECT password,groups FROM accinfo WHERE username=%r" % username.upper()
        # print(sqlsatement)
        cursor.execute(sqlsatement)
        dpass = cursor.fetchone()
        group = dpass[1]
        print("message=", dpass, "dpass1=", dpass[1])
        if dpass is None:
            return HttpResponseRedirect(reverse('APP:login'))
        else:
            dpass = dpass[0]
            print(dpass)
            if password == dpass:
                print("Authentication Success!")
                # return HttpResponse("Hello, world. You're at the login index.")
                response = HttpResponseRedirect(reverse('APP:index'))
                # 使用cookie存储用户登录的信息
                response.set_cookie('loginname', username)
                response.set_cookie('group', group)
                response.set_cookie('logintime', datetime.datetime.now())
                return response
            else:
                print("Authentication Failed!")
            return HttpResponseRedirect(reverse('APP:login'))
    else:
        print("get method")
    return render(request, 'maintenance/login.html')


# 登录成功后，跳转到index页面
# @login_auth
def index(request):
    currentuser = request.COOKIES.get('loginname')
    return render(request, 'maintenance/index.html', {'user': currentuser})


#####################################################
#            服务启停功能实现=====START             #
#####################################################
# 服务启停功能：公共函数
# 将任务执行记录到日志表audit_log中
def record_operation(taskinfo):
    with connection.cursor() as cursor:
        sqlstatement1 = "insert into audit_log (oper_user, oper_command, oper_message) VALUES ('%s', '%s', '%s')" % (
            taskinfo['oper'], taskinfo['cmd'], taskinfo['resulut'])
        cursor.execute(sqlstatement1)


# 每个任务执行完成后，更新数据库中的数据(服务的状态信息，每类软件对应各自的表【xxxdata表】)
def updatestatus(taskinfo):
    with connection.cursor() as cursor:
        sqlstatement2 = ''
        if 'apache' in taskinfo['action']:
            sqlstatement2 = "update apachedata set status = %d where id = %r" % (
                int(taskinfo['resulut']), taskinfo['id'])
        elif 'nginx' in taskinfo['action']:
            sqlstatement2 = "update nginxdata set status = %d where id = %r" % (
                int(taskinfo['resulut']), taskinfo['id'])
        elif 'tomcat' in taskinfo['action']:
            sqlstatement2 = "update tomcatdata set status = %d where id = %r" % (
                int(taskinfo['resulut']), taskinfo['id'])
        elif 'oracle' in taskinfo['action']:
            sqlstatement2 = "update oracledata set status = %d where id = %r" % (
                int(taskinfo['resulut']), taskinfo['id'])
        elif 'mysql' in taskinfo['action']:
            sqlstatement2 = "update mysqldata set status = %d where id = %r" % (
                int(taskinfo['resulut']), taskinfo['id'])
        cursor.execute(sqlstatement2)


# 服务启停功能
# ###功能介绍#####
# 功能1：前端调用loadxxxData(加载数据、翻页等功能)的响应函数：get_xxx_data(get_tomcat_data)
# 功能2：前端serarchxxx响应函数：search_xxxx(search_tomcat...)
# 功能3：前端opt_xxx(前端点击检查、启动、停止按钮时)响应函数：opt_xxx
# ###业务流程####
# 针对服务器的操作:
# 1.首先通过前台获得ID 和 操作
# 2.通过ID 丰富信息
# 3.形成完整的操作SQL
# 4.执行SQL，返回结果
# 5.将操作信息及结果写入操作记录表，并将结果返回前台
# 6.前台收到信息更新现在运行状态
# 服务启停功能：tomcat
def get_tomcat_data(request):
    # 定义每个页面最大显示的数据行数
    maxline = 9
    with connection.cursor() as cursor:
        page_number = int(request.GET.get('page'))
        # 数据查询的起点
        startpos = (page_number - 1) * maxline
        cursor.execute(
            'select id, machine, tomcathome, ipaddress, description, status,startwait,stopwait,checkwait '
            'from tomcatdata LIMIT %d, %d;' % (startpos, maxline))
        results = dictfetchall(cursor)
        cursor.execute('SELECT COUNT(*) FROM tomcatdata')
        total = cursor.fetchall()[0][0]
    data = {'page': page_number, 'total': total, 'results': results}
    return JsonResponse(data)


def get_taskinfo(tomcat_id, tomcat_action, oper):
    command = ''
    # userinfo = ''
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT id, tomcatport, tomcathome, ipaddress, startwait, stopwait '
            'FROM tomcatdata WHERE id = %s' % tomcat_id
        )
        tomcater = dictfetchall(cursor)[0]
        serverip = tomcater['ipaddress']
        res = cursor.execute(
            "SELECT user1,password1 FROM machine_pwd WHERE ipaddress = '%s'" % serverip
        )
        if res:
            userinfo = dictfetchall(cursor)[0]
        else:
            userinfo = {'user1': 'other', 'password1': 'other'}
    if tomcat_action == 'check_tomcat':
        tomcat_home = tomcater['tomcathome']
        tomcat_port = tomcater['tomcatport']
        command = 'sh /operation/tomcat/checktomcat.sh %s %s ' % (tomcat_home, tomcat_port)
    elif tomcat_action == 'start_tomcat':
        # 需要传入三个参数 home目录/端口号/启动超时时长
        tomcat_home = tomcater['tomcathome']
        tomcat_port = tomcater['tomcatport']
        start_wait = tomcater['startwait']
        # sh_dir = '/operation/tomcat/starttomcat.sh'
        command = 'sh /operation/tomcat/starttomcat.sh %s %s %s ' % (tomcat_home, tomcat_port, start_wait)
    elif tomcat_action == 'stop_tomcat':
        # 需要传入三个参数 home目录/端口号/启动超时时长
        tomcat_home = tomcater['tomcathome']
        tomcat_port = tomcater['tomcatport']
        stop_wait = tomcater['stopwait']
        # sh_dir = '/operation/tomcat/starttomcat.sh'
        command = 'sh /operation/tomcat/stoptomcat.sh %s %s %s ' % (tomcat_home, tomcat_port, stop_wait)
    task_info = {
        'id': tomcat_id,
        'action': tomcat_action,
        'oper': oper,
        'ip': tomcater['ipaddress'],
        'user': userinfo['user1'],
        'pwd': userinfo['password1'],
        'cmd': command,
        'result': ''
    }
    return task_info


def opt_tomcat(request):
    # 获得前台信息
    tomcat_id = request.GET.get('id')
    tomcat_action = request.GET.get('action')
    oper = request.COOKIES.get('loginname')
    # 根据ID和action 获得任务信息，并形成完整的操作SQL，都存入taskinfo中
    taskinfo = get_taskinfo(tomcat_id, tomcat_action, oper)
    # 传入taskinfo，执行SQL操作，返回目标服务器控制台的结果
    mytask = Task(taskinfo)
    result = mytask.execute()
    # print("result=",result)
    if result.isdigit():
        taskinfo['resulut'] = result
    else:
        taskinfo['resulut'] = '102'
    # 将操作记录写入记录表中，同时更新tomcatdata表中的状态字段
    # genrecords_updatestatus(taskinfo)
    # 将操作记录写入记录表中
    record_operation(taskinfo)
    # 更新apachedata表中的状态字段
    updatestatus(taskinfo)
    # 将结果传到前台
    message = {
        '101': 'Tomcat正常运行.',
        '102': 'Tomcat异常,请人工检查.',
        '103': 'Tomcat服务关闭.',
        '104': 'Tomcat启动超时.',
        '105': 'Tomcat关闭超时.',
    }
    return JsonResponse({
        'status': taskinfo['resulut'],
        'message': message[taskinfo['resulut']],
    })


def search_tomcat(request):
    search_val = request.GET.get('data')
    sqlsatement = "select id, machine, tomcathome, ipaddress, description,status,startwait,stopwait,checkwait " \
                  "from tomcatdata WHERE ipaddress= '%s' OR machine= '%s'" % (search_val, search_val)
    with connection.cursor() as cursor:
        cursor.execute(sqlsatement)
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})


# 服务启停功能：oracle
def get_oracle_data(request):
    # 定义每个页面最大显示的数据行数
    maxline = 9
    with connection.cursor() as cursor:
        page_number = int(request.GET.get('page'))
        # 数据查询的起点
        startpos = (page_number - 1) * maxline
        cursor.execute(
            'select id, machine, ipaddress,sid,startwait,stopwait,status,checkwait from oracledata LIMIT %d, %d;' % (
                startpos, maxline))
        results = dictfetchall(cursor)
        cursor.execute('SELECT COUNT(*) FROM oracledata')
        total = cursor.fetchall()[0][0]
    data = {'page': page_number, 'total': total, 'results': results}
    return JsonResponse(data)


def get_taskinfo_oracle(oracle_id, oracle_action, oper):
    command = ''
    # userinfo = ''
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT id, ipaddress, sid, machine, startwait, stopwait FROM oracledata WHERE id = %s' % oracle_id
        )
        oracler = dictfetchall(cursor)[0]
        serverip = oracler['ipaddress']
        res = cursor.execute(
            "SELECT user1,password1 FROM machine_pwd WHERE ipaddress = '%s'" % serverip
        )
        if res:
            userinfo = dictfetchall(cursor)[0]
        else:
            userinfo = {'user1': 'other', 'password1': 'other'}
    if oracle_action == 'check_oracle':
        command = 'sh /operation/oracle/checkoracle.sh'
    elif oracle_action == 'start_oracle':
        # 需要传入1个参数   启动数据库超时时长
        start_wait = oracler['startwait']
        command = 'sh /operation/oracle/startoracle.sh %s ' % start_wait
    elif oracle_action == 'stop_oracle':
        # 需要传入1个参数   关闭数据库超时时长
        stop_wait = oracler['stopwait']
        command = 'sh /operation/oracle/stoporacle.sh %s' % stop_wait
    task_info = {
        'id': oracle_id,
        'action': oracle_action,
        'oper': oper,
        'ip': oracler['ipaddress'],
        'user': userinfo['user1'],
        'pwd': userinfo['password1'],
        'cmd': command,
        'result': ''
    }
    return task_info


def opt_oracle(request):
    # 获得前台信息
    oracle_id = request.GET.get('id')
    oracle_action = request.GET.get('action')
    oper = request.COOKIES.get('loginname')
    # 根据ID和action 获得任务信息，并形成完整的操作SQL，都存入taskinfo中
    taskinfo = get_taskinfo_oracle(oracle_id, oracle_action, oper)
    # 传入taskinfo，执行SQL操作，返回目标服务器控制台的结果
    mytask = Task(taskinfo)
    result = mytask.execute()
    print(result)
    if result.isdigit():
        taskinfo['resulut'] = result
    else:
        taskinfo['resulut'] = '202'
        # 将操作记录写入记录表中，同时更新tomcatdata表中的状态字段
    # 将操作记录写入记录表中
    record_operation(taskinfo)
    # 更新apachedata表中的状态字段
    updatestatus(taskinfo)
    # 将结果传到前台
    message = {
        '201': 'Oracle数据库正常运行.',
        '202': 'Oracle数据库状态异常,请人工检查.',
        '203': 'Oracle数据库处于关闭状态.',
    }
    return JsonResponse({
        'status': taskinfo['resulut'],
        'message': message[taskinfo['resulut']],
    })


def search_oracle(request):
    search_val = request.GET.get('data')
    sqlsatement = "select id, machine, ipaddress,sid,startwait,stopwait,status,checkwait " \
                  "from oracledata WHERE ipaddress= '%s' OR machine= '%s'" % (search_val, search_val)
    with connection.cursor() as cursor:
        cursor.execute(sqlsatement)
        results = dictfetchall(cursor)
    data = {'results': results}
    return JsonResponse(data)


# 服务启停功能：apache
def get_apache_data(request):
    # 定义每个页面最大显示的数据行数
    maxline = 9
    with connection.cursor() as cursor:
        page_number = int(request.GET.get('page'))
        # 数据查询的起点
        startpos = (page_number - 1) * maxline
        cursor.execute(
            'select id, machine, apachehome, ipaddress, description, status,startwait,stopwait,checkwait '
            'from apachedata LIMIT %d, %d;' % (startpos, maxline))
        results = dictfetchall(cursor)
        cursor.execute('SELECT COUNT(*) FROM apachedata')
        total = cursor.fetchall()[0][0]
    data = {'page': page_number, 'total': total, 'results': results}
    return JsonResponse(data)


def get_apache_taskinfo(apache_id, apache_action, oper):
    command = ''
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT id, apachehome, ipaddress, startwait, stopwait FROM apachedata WHERE id = %s' % apache_id
        )
        apacher = dictfetchall(cursor)[0]
        serverip = apacher['ipaddress']
        res = cursor.execute(
            "SELECT user1,password1 FROM machine_pwd WHERE ipaddress = '%s'" % serverip
        )
        if res:
            userinfo = dictfetchall(cursor)[0]
        else:
            userinfo = {'user1': 'other', 'password1': 'other'}
    if apache_action == 'check_apache':
        apache_home = apacher['apachehome']
        command = 'sh /operation/apache/checkapache.sh %s  ' % apache_home
    elif apache_action == 'start_apache':
        # 需要传入两个参数 home目录/启动超时时长
        apache_home = apacher['apachehome']
        start_wait = apacher['startwait']
        command = 'sh /operation/apache/startapache.sh %s %s' % (apache_home, start_wait)
    elif apache_action == 'stop_apache':
        # 需要传入三个参数 home目录/启动超时时长
        apache_home = apacher['apachehome']
        stop_wait = apacher['stopwait']
        command = 'sh /operation/apache/stopapache.sh %s %s ' % (apache_home, stop_wait)
    task_info = {
        'id': apache_id,
        'action': apache_action,
        'oper': oper,
        'ip': apacher['ipaddress'],
        'user': userinfo['user1'],
        'pwd': userinfo['password1'],
        'cmd': command,
        'result': ''
    }
    return task_info


def opt_apache(request):
    # 获得前台信息
    apache_id = request.GET.get('id')
    apache_action = request.GET.get('action')
    oper = request.COOKIES.get('loginname')
    # 根据ID和action 获得任务信息，并形成完整的操作SQL，都存入taskinfo中
    taskinfo = get_apache_taskinfo(apache_id, apache_action, oper)
    # 传入taskinfo，执行SQL操作，返回目标服务器控制台的结果
    mytask = Task(taskinfo)
    result = mytask.execute()
    # print("result=",result)
    if result.isdigit():
        taskinfo['resulut'] = result
    else:
        taskinfo['resulut'] = '402'
    # 将操作记录写入记录表中
    record_operation(taskinfo)
    # 更新apachedata表中的状态字段
    updatestatus(taskinfo)
    # 将结果传到前台
    message = {
        '401': 'Apache正常运行.',
        '402': 'Apache异常,请人工检查.',
        '403': 'Apache服务关闭.',
    }
    return JsonResponse({
        'status': taskinfo['resulut'],
        'message': message[taskinfo['resulut']],
    })


def search_apache(request):
    search_val = request.GET.get('data')
    sqlsatement = "select id, machine, apachehome, ipaddress, description, status,startwait," \
                  "stopwait,checkwait from apachedata WHERE ipaddress= '%s' OR machine= '%s'" \
                  % (search_val, search_val)
    with connection.cursor() as cursor:
        cursor.execute(sqlsatement)
        results = dictfetchall(cursor)
    data = {'results': results}
    return JsonResponse(data)


# 服务启停功能：nginx
def get_nginx_data(request):
    # 定义每个页面最大显示的数据行数
    maxline = 9
    with connection.cursor() as cursor:
        page_number = int(request.GET.get('page'))
        # 数据查询的起点
        startpos = (page_number - 1) * maxline
        cursor.execute(
            'select id, machine, ipaddress, description, status,startwait,stopwait,checkwait '
            'from nginxdata LIMIT %d, %d;' % (startpos, maxline))
        results = dictfetchall(cursor)
        cursor.execute('SELECT COUNT(*) FROM nginxdata')
        total = cursor.fetchall()[0][0]
    data = {'page': page_number, 'total': total, 'results': results}
    return JsonResponse(data)


def get_nginx_taskinfo(nginx_id, nginx_action, oper):
    command = ''
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT id, ipaddress, startwait, stopwait FROM nginxdata WHERE id = %s' % nginx_id
        )
        nginxr = dictfetchall(cursor)[0]
        serverip = nginxr['ipaddress']
        res = cursor.execute(
            "SELECT user1,password1 FROM machine_pwd WHERE ipaddress = '%s'" % serverip
        )
        if res:
            userinfo = dictfetchall(cursor)[0]
        else:
            userinfo = {'user1': 'other', 'password1': 'other'}
    if nginx_action == 'check_nginx':
        command = 'sh /operation/nginx/checknginx.sh '
    elif nginx_action == 'start_nginx':
        start_wait = nginxr['startwait']
        command = 'sh /operation/nginx/startnginx.sh %s' % start_wait
    elif nginx_action == 'stop_nginx':
        stop_wait = nginxr['stopwait']
        command = 'sh /operation/nginx/stopnginx.sh %s' % stop_wait
    task_info = {
        'id': nginx_id,
        'action': nginx_action,
        'oper': oper,
        'ip': nginxr['ipaddress'],
        'user': userinfo['user1'],
        'pwd': userinfo['password1'],
        'cmd': command,
        'result': ''
    }
    return task_info


def opt_nginx(request):
    # 获得前台信息
    nginx_id = request.GET.get('id')
    nginx_action = request.GET.get('action')
    oper = request.COOKIES.get('loginname')
    # 根据ID和action 获得任务信息，并形成完整的操作SQL，都存入taskinfo中
    taskinfo = get_nginx_taskinfo(nginx_id, nginx_action, oper)
    # 传入taskinfo，执行SQL操作，返回目标服务器控制台的结果
    mytask = Task(taskinfo)
    result = mytask.execute()
    # print("result=",result)
    if result.isdigit():
        taskinfo['resulut'] = result
    else:
        taskinfo['resulut'] = '502'
    # 将操作记录写入记录表中
    record_operation(taskinfo)
    # 更新nginxdata表中的状态字段
    updatestatus(taskinfo)
    # 将结果传到前台
    message = {
        '501': 'Nginx正常运行.',
        '502': 'Nginx异常,请人工检查.',
        '503': 'Nginx服务关闭.',
    }
    return JsonResponse({
        'status': taskinfo['resulut'],
        'message': message[taskinfo['resulut']],
    })


def search_nginx(request):
    search_val = request.GET.get('data')
    sqlsatement = "select id, machine, ipaddress, description, status,startwait,stopwait,checkwait " \
                  "from nginxdata WHERE ipaddress= '%s' OR machine= '%s'" % (search_val, search_val)
    with connection.cursor() as cursor:
        cursor.execute(sqlsatement)
        results = dictfetchall(cursor)
    data = {'results': results}
    return JsonResponse(data)


# 服务启停功能：mysql
def get_mysql_data(request):
    # 定义每个页面最大显示的数据行数
    maxline = 9
    with connection.cursor() as cursor:
        page_number = int(request.GET.get('page'))
        # 数据查询的起点
        startpos = (page_number - 1) * maxline
        cursor.execute(
            'select id, machine, mysqlport, ipaddress, description, hostname,checktime,status,startwait,stopwait'
            ' from mysqldata LIMIT %d, %d;' % (startpos, maxline))
        results = dictfetchall(cursor)
        cursor.execute('SELECT COUNT(*) FROM mysqldata')
        total = cursor.fetchall()[0][0]
    data = {'page': page_number, 'total': total, 'results': results}
    return JsonResponse(data)


def get_mysql_taskinfo(mysql_id, mysql_action, oper):
    command = ''
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT id, ipaddress, startwait, stopwait FROM mysqldata WHERE id = %s' % mysql_id
        )
        mysqlr = dictfetchall(cursor)[0]
        serverip = mysqlr['ipaddress']
        res = cursor.execute(
            "SELECT user1,password1 FROM machine_pwd WHERE ipaddress = '%s'" % serverip
        )
        if res:
            userinfo = dictfetchall(cursor)[0]
        else:
            userinfo = {'user1': 'other', 'password1': 'other'}
    if mysql_action == 'check_mysql':
        command = 'sh /operation/mysql/checkmysql.sh '
    elif mysql_action == 'start_mysql':
        start_wait = mysqlr['startwait']
        command = 'sh /operation/mysql/startmysql.sh %s' % start_wait
    elif mysql_action == 'stop_mysql':
        stop_wait = mysqlr['stopwait']
        command = 'sh /operation/mysql/stopmysql.sh %s' % stop_wait
    task_info = {
        'id': mysql_id,
        'action': mysql_action,
        'oper': oper,
        'ip': mysqlr['ipaddress'],
        'user': userinfo['user1'],
        'pwd': userinfo['password1'],
        'cmd': command,
        'result': ''
    }
    return task_info


def opt_mysql(request):
    # 获得前台信息
    mysql_id = request.GET.get('id')
    mysql_action = request.GET.get('action')
    oper = request.COOKIES.get('loginname')
    # 根据ID和action 获得任务信息，并形成完整的操作SQL，都存入taskinfo中
    taskinfo = get_mysql_taskinfo(mysql_id, mysql_action, oper)
    # 传入taskinfo，执行SQL操作，返回目标服务器控制台的结果
    mytask = Task(taskinfo)
    result = mytask.execute()
    # print("result=",result)
    if result.isdigit():
        taskinfo['resulut'] = result
    else:
        taskinfo['resulut'] = '302'
    # 将操作记录写入记录表中
    record_operation(taskinfo)
    # 更新nginxdata表中的状态字段
    updatestatus(taskinfo)
    # 将结果传到前台
    message = {
        '301': 'Mysql正常运行.',
        '302': 'Mysql异常,请人工检查.',
        '303': 'Mysql服务关闭.',
        '304': 'Mysql启动超时',
        '305': 'Mysql关闭超时',
    }
    return JsonResponse({
        'status': taskinfo['resulut'],
        'message': message[taskinfo['resulut']],
    })


def search_mysql(request):
    search_val = request.GET.get('data')
    sqlsatement = "select id, machine, ipaddress, description,mysqlport,status,startwait,stopwait,checktime " \
                  "from mysqldata WHERE ipaddress= '%s' OR machine= '%s'" % (search_val, search_val)
    with connection.cursor() as cursor:
        cursor.execute(sqlsatement)
        results = dictfetchall(cursor)
    data = {'results': results}
    return JsonResponse(data)


#####################################################
#            服务启停功能实现=====END               #
#####################################################
#####################################################
#            报表功能实现=====START                 #
#####################################################

# 展示auditlog列表
def get_auditlog_data(request):
    # 定义每个页面最大显示的数据行数
    maxline = 13
    with connection.cursor() as cursor:
        page_number = int(request.GET.get('page'))
        # 数据查询的起点
        startpos = (page_number - 1) * maxline
        cursor.execute(
            'select audit_log.oper_user, audit_log.machine, audit_log.IP, audit_log.command, '
            'statuscode.description, audit_log.oper_time '
            'from audit_log '
            'RIGHT JOIN statuscode ON audit_log.oper_message=statuscode.returncode LIMIT %d, %d;' % (
                startpos, maxline))
        results = dictfetchall(cursor)
        cursor.execute('SELECT COUNT(*) FROM audit_log')
        total = cursor.fetchall()[0][0]
    data = {'page': page_number, 'total': total, 'results': results}
    return JsonResponse(data)


def search_auditlog(request):
    return None


#####################################################
#            报表功能实现=====END                  #
#####################################################
#####################################################
#            系统管理=====START                     #
#####################################################
# 实现用户信息增加、修改、删除功能
# 系统管理：用户信息维护：展示系统中用户的信息
def get_user_data(request):
    # 定义每个页面最大显示的数据行数
    maxline = 9
    with connection.cursor() as cursor:
        page_number = int(request.GET.get('page'))
        # 数据查询的起点
        startpos = (page_number - 1) * maxline
        cursor.execute(
            'select id,username,password, email, privilege,groups,regtime from accinfo LIMIT %d, %d;' % (
                startpos, maxline))
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})


# 系统管理：用户信息维护：根据前端请求，删除某一个用户
def opdeluser(request):
    # 获取前端传过来的用户名称
    # message = ''
    username = request.GET.get('id')
    oper = request.COOKIES.get('loginname')
    # print("username from ajax:"+username+",username from cookiess:"+oper)
    if username == oper:
        message = '不能删除自己，请联系管理员'
    else:
        with connection.cursor() as cursor:
            # 查询当前用户组，如果不是admin组，提示该用户没有权限
            sqlstatement1 = "select groups from accinfo where username= '%s'" % oper
            # print(sqlstatement1)
            cursor.execute(sqlstatement1)
            data = dictfetchall(cursor)[0]['groups']
            # print(data)
            if data != 'admin':
                message = '您没有删除用户的权限，请联系管理员'
                print(message)
            else:
                sqlstatement2 = "delete from accinfo where username='%s'" % username
                # print(sqlstatement2)
                cursor.execute(sqlstatement2)
                message = '用户已经删除'
                # print(message)
    return JsonResponse(message, safe=False, json_dumps_params={'ensure_ascii': False})


# 系统管理：用户信息维护：修改用户信息
def modify_user_data(request):
    userid = request.GET.get('userid')
    sqlsatement = "select id,username,password, email, privilege,groups from accinfo WHERE username= '%s'" % userid
    with connection.cursor() as cursor:
        cursor.execute(sqlsatement)
        data = cursor.fetchone()
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})


# 系统管理：用户信息维护：保存用户信息
def save_user_data(request):
    user_username = request.GET.get('username')
    user_password = request.GET.get('password')
    user_email = request.GET.get('email')
    user_privilege = request.GET.get('privilege')
    user_group = request.GET.get('group')
    # print(user_username+user_password+user_email+user_privilege+user_group)
    sqlsatement = "update accinfo set username='%s',password='%s',email='%s',privilege=%s," \
                  "groups='%s' WHERE username='%s'" \
                  % (user_username, user_password, user_email, user_privilege, user_group, user_username)
    with connection.cursor() as cursor:
        cursor.execute(sqlsatement)
        return JsonResponse('保存成功', safe=False, json_dumps_params={'ensure_ascii': False})


# 系统管理：用户信息维护：添加用户信息
def add_user_data(request):
    user_username = request.GET.get('username')
    user_password = request.GET.get('password')
    user_email = request.GET.get('email')
    user_privilege = request.GET.get('privilege')
    user_group = request.GET.get('group')
    # print(user_username + user_password + user_email + user_privilege + user_group)
    # print('******************************')
    sqlsatement = "insert into accinfo(username,password,email,privilege,groups) VALUES ('%s','%s','%s',%s,'%s')" % (
        user_username, user_password, user_email, user_privilege, user_group)
    with connection.cursor() as cursor:
        cursor.execute(sqlsatement)
    return JsonResponse('添加成功', safe=False, json_dumps_params={'ensure_ascii': False})


#####################################################
#            系统管理=====END                      #
#####################################################
#####################################################
#            常用工具=====START                     #
#####################################################
# 系统健康检查功能
# 获取系统名称清单
def get_system_list(request):
    current_username = request.COOKIES.get('loginname')
    current_group = request.COOKIES.get('group')
    # print('group=',current_group,current_username)
    if current_group == 'admin':
        current_username = current_username + "'" + ' or ' + "'" + '1=1'
        # print('username')
    sql_getsystemlist = "select id,systemname,systemadmin,devadmin,description,levels" \
                        " from systeminfo where systemadmin='%s'" % current_username
    print(sql_getsystemlist)
    with connection.cursor() as cursor:
        cursor.execute(sql_getsystemlist)
        data = dictfetchall(cursor)
    # print(sql_getsystemlist,data)
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})


# 获取某个应用系统下对应服务器清单
def get_machine_list(request):
    current_system = request.GET.get('systemname')
    sql_getsystemlist = "select id,systemname,machinename,machineip,types,levels,priority " \
                        "from machineinfo where systemname ='%s'" % current_system
    with connection.cursor() as cursor:
        cursor.execute(sql_getsystemlist)
        data = dictfetchall(cursor)
    # print(sql_getsystemlist,data)
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})


# 系统检查启停操作
@csrf_exempt
def opt_checksystem(request):
    machines = eval(request.POST.get('machines'))
    system = machines[0]['systemname']
    hostlist = [machine['machineip'] for machine in machines]
    hostlist = list(set(hostlist))
    # print(hostlist)
    myuuid = str(uuid.uuid1())
    taskinfo = {'taskid': myuuid, 'taskers': []}
    # taskinfo = {'taskid': myuuid,
    #             'taskers': [{'ipaddress': '10.26.202.133', 'taskcount': 2},
    #                         {'ipaddress': '10.26.202.134', 'taskcount': 2}]
    #             }
    # print(taskinfo)
    i = 0
    for item in hostlist:
        taskinfo['taskers'].append({'ipaddress': item, 'taskcount': 4})
        taskcount = taskinfo['taskers'][i]['taskcount']
        #print("taskcount=", taskcount)
        # 将任务信息更新到tasksumary表中
        sql_inserttasksummary = "insert into tasksummary(taskid,ipaddress,taskcount) VALUES ('%s','%s','%d') " \
                                % (myuuid, item, taskcount)
        # print("inserttasksummary=", sql_inserttasksummary)
        with connection.cursor() as cursor:
            cursor.execute(sql_inserttasksummary)
            connection.close()
        host = [item]
        i = i + 1
        taskname = "process" + str(i)
        # print(host)
        ymlfile = ['/operation/autoops/yml/os.yml']
        task = multiprocessing.Process(
            target=AnsibleAPI(hostlist=host, playbooks=ymlfile, uuid=myuuid, systemname=system,
                              processname=taskname).runplaybook)
        #print("taskname=", taskname)
        task.start()
    #print("taskinfo=", taskinfo)
    # anl = AnsibleAPI(
    #     hostlist = ['10.26.222.216'],
    #     playbooks = ['/tempdir/ancode/test.yml'],
    #     uuid = myuuid,
    #     systemname = system
    # )
    # an2 = AnsibleAPI(
    #     hostlist = [ '10.26.222.213'],
    #     playbooks = ['/tempdir/ancode/test.yml'],
    #     uuid = myuuid,
    #     systemname = system
    # )
    # 多进程
    # processes = []
    # #p1 = multiprocessing.Process(name='process_one', target=anl.runplaybook)
    # p1 = multiprocessing.Process(target=anl.runplaybook)
    # p2 = multiprocessing.Process(target=an2.runplaybook)
    # processes.append(p1)
    # processes.append(p2)
    # for p in processes:
    #     p.start()

    # machine_count = request.POST.get('count')
    # check_list = request.POST
    # task = []
    # for i in range(0, int(machine_count)):
    #     key = 'machines[' + str(i) + '][machineip]'
    #     # print(check_list.get(key))
    #     ipaddress = [check_list.get(key)]
    #     ymlfile = ['/tempdir/ancode/test.yml']
    #     # print(i, ipaddress, ymlfile)
    #     # plist.append(AnsibleAPI(ipaddress,ymlfile))
    #     # print(plist[i])
    #     #task.append(multiprocessing.Process(target=plist[i].runplaybook))
    #     #task[i].start()
    #     #hostlist1 = ['10.26.222.213']
    #     #playbooks1 = ['/tempdir/ancode/test.yml']
    #     p= AnsibleAPI(ipaddress, ymlfile)
    #     task.append(multiprocessing.Process(target=p.runplaybook))
    #     # task.append(t1)
    # # print(playbook)
    # for t in task:
    #     # t.daemon=True
    #     t.start()

    # hostlist1 = ['10.26.222.213']
    # playbooks1 = ['/tempdir/ancode/test.yml']
    # p1 = AnsibleAPI(hostlist1, playbooks1)
    #
    # hostlist2 = ['10.26.222.210']
    # playbooks2 = ['/tempdir/ancode/test.yml']
    # p2 = AnsibleAPI(hostlist2, playbooks2)
    #
    # processes = []
    # t1 = multiprocessing.Process(target=p1.runplaybook)
    # #t1.start()
    # processes.append(t1)
    # t2 = multiprocessing.Process(target=p2.runplaybook)
    # #t2.start()
    # processes.append(t2)
    # for t in processes:
    #     # t.daemon=True
    #     t.start()
    # # mainThread = threading.current_thread()
    # for t in processes:
    #     t.join()
    # threads = []
    # thr1 = threading.Thread(target=func1, args=(u'线程1',))
    # threads.append(thr1)
    # thr2 = threading.Thread(target=func2, args=(u'线程2',))
    # threads.append(thr2)
    #
    # thr3 = threading.Thread(target=func2, args=(u'线程3',))
    # threads.append(thr3)
    # print("%s===执行开始了。\n" %time.time())
    # for t in threads:
    #     t.setDaemon(True)
    #     t.start()
    #
    # for t in threads:
    #     t.join()
    #     # join()的作用是，在子线程完成运行之前，阻塞父线程。
    # print("%s===执行结束了。\n" % time.time())

    return JsonResponse(taskinfo)


# 根据前端的taskid提供后台任务运行的进度
def query_taskprocess(request):
    taskid = request.GET.get('taskid')
    # print(taskid)
    with connection.cursor() as cursor:
        sqlstatement = 'select ipaddress,taskcurrent as stepcount from tasksummary where taskid = "%s" ' % (
            taskid)
        cursor.execute(sqlstatement)
        data = dictfetchall(cursor)
    taskprocess = {}
    for item in data:
        taskprocess[item['ipaddress']] = item['stepcount']
    print("taskprocess=", taskprocess)
    return JsonResponse({'datas': taskprocess})


# 根据前端的taskid提供最终检查的结果
@csrf_exempt
def systemcheck_report(request):
    taskid = request.GET.get('taskid')
    sql_systemcheckreport = 'select ipaddress,result,taskname  from checksystem where result!="[]" and taskid = "%s" group by ipaddress' % (
        taskid)
    with connection.cursor() as cursor:
        cursor.execute(sql_systemcheckreport)
        data = dictfetchall(cursor)
    # print(sql_getsystemlist,data)
    # print("report==================",taskid)
    # print(data)
    return JsonResponse({'reports': data})

# class ansibleThread(threading.Thread):
#     def run(self):
#         print("start.... %s" % (self.getName(),))
#         for i in range(10):
#             time.sleep(1)
#             print(i)
#         print("end.... %s" % (self.getName(),))
# def func1(var):
#     for i in range(3):
#         print("%s===func1 running %s\n" % (time.time(), var))
#         time.sleep(3)
#
# def func2(var):
#     for i in range(2):
#         print("%s===func2 running %s\n" % (time.time(), var))
#         time.sleep(2)

#####################################################
#            常用工具=====END                       #
#####################################################
