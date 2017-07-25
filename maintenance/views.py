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
    return render(request, 'maintenance/index.html')


def get_taskinfo(tomcat_id, tomcat_action, oper):  # 根据ID生成taskinfo
    command = ''
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT id, tomcatport, tomcathome, ipaddress, startwait, stopwait FROM tomcatdata WHERE id = %s' % tomcat_id
        )
        tomcater = dictfetchall(cursor)[0]
        serverip = tomcater['ipaddress']
        cursor.execute(
            "SELECT user1,password1 FROM machine_pwd WHERE ipaddress = '%s'" % serverip
        )
        userinfo = dictfetchall(cursor)[0]
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


def genrecords_updatestatus(taskinfo):  # 写入操作记录并更新tomcat状态
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


# 展示服务器列表
def get_tomcat_data(request):
    with connection.cursor() as cursor:
        page_number = int(request.GET.get('page'))
        m = (page_number - 1) * 10
        cursor.execute(
            'select id, machine, tomcathome, ipaddress, description, status from tomcatdata LIMIT %d, %d;' % (m, 10))
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})


# 根据IP或者主机名搜索服务器
def search_tomcat(request):
    search_val = request.GET.get('data')
    sqlsatement = "select id, machine, tomcathome, ipaddress, description from tomcatdata WHERE ipaddress= '%s' OR machine= '%s'" % (
        search_val, search_val)
    with connection.cursor() as cursor:
        cursor.execute(sqlsatement)
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})


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
        sqlsatement = "SELECT password FROM accinfo WHERE username=%r" % username.upper()
        # print(sqlsatement)
        cursor.execute(sqlsatement)
        dpass = cursor.fetchone()
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
                response.set_cookie('logintime', datetime.datetime.now())
                return response
            else:
                print("Authentication Failed!")
            return HttpResponseRedirect(reverse('APP:login'))
    else:
        print("get method")
    return render(request, 'maintenance/login.html')
