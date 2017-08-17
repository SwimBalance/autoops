from django.conf.urls import url
from . import views

urlpatterns = [
    # 登录主页面
    url(r'^$', views.login, name='login'),
    # 登录成功后程序主页面
    url(r'^index/$', views.index, name='index'),
    # 【服务启停功能】前端获取后台数据
    url(r'^apacheData/$', views.get_apache_data, name='apache'),
    url(r'^nginxData/$', views.get_nginx_data, ),
    url(r'^tomcatData/$', views.get_tomcat_data, name='tomcat'),
    url(r'^oracleData/$', views.get_oracle_data, name='oracle'),
    url(r'^mysqlData/$', views.get_mysql_data, name='mysql'),
    # 【系统管理：用户信息维护】
    url(r'^usermanagementData/$', views.get_user_data, name='usermanagement'),
    # 【报表：用户操作日志】
    url(r'^auditlogData/$', views.get_auditlog_data, name='auditlog'),
    # 【服务启停功能】前端查找后台数据
    url(r'^searchtomcat/$', views.search_tomcat, name='oracle'),
    url(r'^searchapache/$', views.search_apache),
    url(r'^searchnginx/$', views.search_nginx),
    url(r'^searchmysql/$', views.search_mysql, name='search_mysql'),
    url(r'^searchauditlog/$', views.search_auditlog, name='searchauditlog'),
    # 【服务启停功能】前端执行操作，后台响应
    url(r'^operation/apache/$', views.opt_apache),
    url(r'^operation/nginx/$', views.opt_nginx),
    url(r'^operation/tomcat$', views.opt_tomcat, name='operation'),
    url(r'^operation/oracle/$', views.opt_oracle, name='operation_oracle'),
    url(r'^operation/mysql$', views.opt_mysql, name='operation_mysql'),
    # 【系统管理：用户信息维护】前端执行操作，后台响应
    url(r'^operation/deleteuser$', views.opdeluser, name='opdeluser'),
    url(r'^operation/modifyuserdata/$', views.modify_user_data, name='modifyuserdata'),
    url(r'^operation/saveuserdata/$', views.save_user_data, name='saveuserdata'),
    url(r'^operation/adduserdata/$', views.add_user_data, name='adduserdata'),
    # 【常用工具：系统健康检查】
    url(r'^operation/getsystemlist/$', views.get_system_list, name='getsystemlist'),
    url(r'^operation/getmachinelist/$', views.get_machine_list, name='getmachinelist'),

]
