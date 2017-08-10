from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^operation/$', views.operation, name='operation'),
    url(r'^operation/deleteuser$', views.opdeluser, name='opdeluser'),
    url(r'^operation/modifyuserdata/$', views.modify_user_data, name='modifyuserdata'),
    url(r'^operation/saveuserdata/$', views.save_user_data, name='saveuserdata'),
    url(r'^operation/adduserdata/$', views.add_user_data, name='adduserdata'),
    url(r'^tomcatData/$', views.get_tomcat_data, name='tomcat'),
    url(r'^oracleData/$', views.get_oracle_data, name='oracle'),
    url(r'^searchtomcat/$', views.search_tomcat, name='oracle'),
    url(r'^usermanagement/$', views.get_user_data, name='usermanagement'),
    url(r'^$', views.login, name='login'),
    url(r'^auditlog/$', views.get_auditlog_data, name='auditlog'),
    url(r'^searchauditlog/$', views.search_auditlog, name='searchauditlog'),
]
