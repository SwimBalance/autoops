from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .tools.ostools import Task
from django.db import connection
from .tools.dbtools import dictfetchall
import datetime
from django.urls import reverse


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


#@login_auth
def index(request):
    currentuser = request.COOKIES.get('loginname')
    return render(request, 'maintenance/index.html',{'user':currentuser})

# 根据ID生成taskinfo
def get_taskinfo(tomcat_id, tomcat_action, oper):
    command = ''
    userinfo = ''
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT id, tomcatport, tomcathome, ipaddress, startwait, stopwait FROM tomcatdata WHERE id = %s' % tomcat_id
        )
        tomcater = dictfetchall(cursor)[0]
        serverip = tomcater['ipaddress']
        res = cursor.execute(
            "SELECT user1,password1 FROM machine_pwd WHERE ipaddress = '%s'" % serverip
        )
        if res:
            userinfo = dictfetchall(cursor)[0]
        else:
            userinfo={'user1':'other','password1':'other'}
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


# 写入操作记录并更新tomcat状态
def genrecords_updatestatus(taskinfo):
    with connection.cursor() as cursor:
        sqlstatement1 = "insert into audit_log (oper_user, oper_command, oper_message) VALUES ('%s', '%s', '%s')" % (
            taskinfo['oper'], taskinfo['cmd'], taskinfo['resulut'])
        sqlstatement2 = "update tomcatdata set status = %d where id = %r" % (int(taskinfo['resulut']), taskinfo['id'])
        cursor.execute(sqlstatement1)
        cursor.execute(sqlstatement2)


# 针对tomcat服务器的操作:
# 1.首先通过前台获得ID 和 操作
# 2.通过ID 丰富信息
# 3.形成完整的操作SQL
# 4.执行SQL，返回结果
# 5.将操作信息及结果写入操作记录表，并将结果返回前台
# 6.前台收到信息更新tomcat现在运行状态
def operation(request):
    # 获得前台信息
    tomcat_id = request.GET.get('id')
    tomcat_action = request.GET.get('action')
    oper = request.COOKIES.get('loginname')
    # 根据ID和action 获得任务信息，并形成完整的操作SQL，都存入taskinfo中
    taskinfo = get_taskinfo(tomcat_id, tomcat_action, oper)
    # 传入taskinfo，执行SQL操作，返回目标服务器控制台的结果
    mytask = Task(taskinfo)
    result = mytask.execute()
    #print("result=",result)
    if result.isdigit():
        taskinfo['resulut'] = result
    else:
        taskinfo['resulut'] = '102'
    # 将操作记录写入记录表中，同时更新tomcatdata表中的状态字段
    genrecords_updatestatus(taskinfo)
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


# 展示tomcat服务器列表
def get_tomcat_data(request):
    #定义每个页面最大显示的数据行数
    maxline = 9
    with connection.cursor() as cursor:
        page_number = int(request.GET.get('page'))
        #数据查询的起点
        startpos = (page_number - 1) * maxline
        cursor.execute(
            'select id, machine, tomcathome, ipaddress, description, status,startwait,stopwait,checkwait from tomcatdata LIMIT %d, %d;' % (startpos, maxline))
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

# 展示auditlog列表
def get_auditlog_data(request):
    #定义每个页面最大显示的数据行数
    maxline = 13
    with connection.cursor() as cursor:
        page_number = int(request.GET.get('page'))
        #数据查询的起点
        startpos = (page_number - 1) * maxline
        cursor.execute(
            'select audit_log.oper_user, audit_log.machine, audit_log.IP, audit_log.command, statuscode.description, audit_log.oper_time from audit_log RIGHT JOIN statuscode ON audit_log.oper_message=statuscode.returncode LIMIT %d, %d;' % (startpos, maxline))
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

def search_auditlog(request):
    return None


# 根据IP或者主机名搜索tomcat服务器
def search_tomcat(request):
    search_val = request.GET.get('data')
    sqlsatement = "select id, machine, tomcathome, ipaddress, description,status,startwait,stopwait,checkwait from tomcatdata WHERE ipaddress= '%s' OR machine= '%s'" % (
        search_val, search_val)
    with connection.cursor() as cursor:
        cursor.execute(sqlsatement)
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

# 系统管理：用户信息维护：展示系统中用户的信息
def get_user_data(request):
    #定义每个页面最大显示的数据行数
    maxline = 9
    with connection.cursor() as cursor:
        page_number = int(request.GET.get('page'))
        #数据查询的起点
        startpos = (page_number - 1) * maxline
        cursor.execute(
            'select id,username,password, email, privilege,groups,regtime from accinfo LIMIT %d, %d;' % (startpos, maxline))
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

# 系统管理：用户信息维护：根据前端请求，删除某一个用户
def opdeluser(request):
    #获取前端传过来的用户名称
    message=''
    username = request.GET.get('id')
    oper = request.COOKIES.get('loginname')
    print("username from ajax:"+username+",username from cookiess:"+oper)
    if (username == oper):
        message='不能删除自己，请联系管理员'
    else:
        with connection.cursor() as cursor:
            #查询当前用户组，如果不是admin组，提示该用户没有权限
            sqlstatement1 = "select groups from accinfo where username= '%s'" % oper
            print(sqlstatement1)
            cursor.execute(sqlstatement1)
            data = dictfetchall(cursor)[0]['groups']
            print(data)
            if data !='admin':
                message='您没有删除用户的权限，请联系管理员'
                print(message)
            else:
                sqlstatement2 ="delete from accinfo where username='%s'" % username
                print(sqlstatement2)
                cursor.execute(sqlstatement2)
                message = '用户已经删除'
                print(message)
    return JsonResponse(message, safe=False, json_dumps_params={'ensure_ascii': False})

#系统管理：用户信息维护：修改用户信息
def modify_user_data(request):
    userid = request.GET.get('userid')
    sqlsatement = "select id,username,password, email, privilege,groups from accinfo WHERE username= '%s'" % userid
    with connection.cursor() as cursor:
        cursor.execute(sqlsatement)
        data = cursor.fetchone()
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

#系统管理：用户信息维护：保存用户信息
def save_user_data(request):
    user_username = request.GET.get('username')
    user_password = request.GET.get('password')
    user_email = request.GET.get('email')
    user_privilege = request.GET.get('privilege')
    user_group = request.GET.get('group')
    print(user_username+user_password+user_email+user_privilege+user_group)
    sqlsatement = "update accinfo set username='%s',password='%s',email='%s',privilege=%s,groups='%s' WHERE username='%s'" % (user_username,user_password,user_email,user_privilege,user_group,user_username)
    with connection.cursor() as cursor:
        cursor.execute(sqlsatement)
    return JsonResponse('dddd', safe=False, json_dumps_params={'ensure_ascii': False})






def get_oracle_data(request):
    return JsonResponse([{'message': 'ORACLE'}], safe=False)


# 登录
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
        print("message=",dpass,"dpass1=", dpass[1])
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
                response.set_cookie('group',group)
                response.set_cookie('logintime', datetime.datetime.now())
                return response
            else:
                print("Authentication Failed!")
            return HttpResponseRedirect(reverse('APP:login'))
    else:
        print("get method")
    return render(request, 'maintenance/login.html')
