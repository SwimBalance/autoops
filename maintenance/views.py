from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from .tools.ostools import Task
from django.db import connection
from .tools.dbtools import dictfetchall
import datetime


def index(request):
    return render(request, 'maintenance/index.html')


# 针对tomcat服务器的操作
def operation(request):
    vm_id = request.GET.get('id')
    vm_action = request.GET.get('action')
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT id, tomcatport, tomcathome, ipaddress, startwait, stopwait FROM tomcatdata WHERE id = %s' % vm_id
        )
        tomcater = dictfetchall(cursor)[0]
    # print(tomcater)
    if vm_action == 'check_tomcat':
        command = 'ifconfig'
    elif vm_action == 'start_tomcat':
        # 需要传入三个参数 home目录/端口号/启动超时时长
        tomcat_home = tomcater['tomcathome']
        tomcat_port = tomcater['tomcatport']
        start_wait = tomcater['startwait']
        # sh_dir = '/operation/tomcat/starttomcat.sh'
        command = 'sh /operation/tomcat/starttomcat.sh %s %s %s ' % (tomcat_home, tomcat_port, start_wait)
    elif vm_action == 'stop_tomcat':
        # 需要传入三个参数 home目录/端口号/启动超时时长
        tomcat_home = tomcater['tomcathome']
        tomcat_port = tomcater['tomcatport']
        stop_wait = tomcater['stopwait']
        # sh_dir = '/operation/tomcat/starttomcat.sh'
        command = 'sh /operation/tomcat/stoptomcat.sh %s %s %s ' % (tomcat_home, tomcat_port, stop_wait)
    task_info = {
        'ip': tomcater['ipaddress'],
        'user': 'root',
        'pwd': 'rootroot',
        'cmd': command,
    }
    mytask = Task(task_info)
    message = mytask.execute()
    return JsonResponse({'message': message})


# 展示服务器列表
def get_tomcat_data(request):
    with connection.cursor() as cursor:
        page_number = int(request.GET.get('page'))
        m = (page_number - 1) * 5
        cursor.execute('select id, machine, tomcathome, ipaddress, description from tomcatdata LIMIT %d, %d;' % (m, 5))
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
        sqlsatement = "SELECT password FROM accinfo WHERE username=" + '"' + username.upper() + '"'
        # print(sqlsatement)
        cursor.execute(sqlsatement)
        dpass = cursor.fetchone()
        if dpass is None:
            return HttpResponseRedirect("./../login")
        else:
            dpass = dpass[0]
            print(dpass)
            if password == dpass:
                print("Authentication Success!")
                # return HttpResponse("Hello, world. You're at the login index.")
                response = HttpResponseRedirect("./../index")
                # 使用cookie存储用户登录的信息
                response.set_cookie('loginname', username)
                response.set_cookie('logintime', datetime.datetime.now())
                return response
            else:
                print("Authentication Failed!")
            return HttpResponseRedirect("./../login")
    else:
        print("get method")
    return render(request, 'maintenance/login.html')
