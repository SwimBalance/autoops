from django.http import JsonResponse
from django.shortcuts import render
from .tools.ostools import Task
from django.db import connection
from .tools.dbtools import dictfetchall


def index(request):
	return render(request, 'APP_test/index.html')


# 针对tomcat服务器的操作
def operation(request):
	vm_id = request.GET.get('id')
	vm_action = request.GET.get('action')
	with connection.cursor() as cursor:
		cursor.execute('SELECT id, tomcatport, tomcathome, ipaddress, startwait, stopwait '
		               'FROM tomcatData '
		               'WHERE id = %s' % vm_id
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
		command = ''
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
def getTomcatData(request):
	# 使用SQL
	with connection.cursor() as cursor:
		cursor.execute('select id, machine, tomcathome, ipaddress, description from tomcatData')
		data = dictfetchall(cursor)
	return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

def getOracleData(request):
	return JsonResponse([{'message':'ORACLE'}], safe=False)
