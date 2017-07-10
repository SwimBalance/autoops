from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^index/$', views.index, name='index'),
	url(r'^operation/$', views.operation, name='operation'),
	url(r'^tomcatData/$', views.getTomcatData, name='tomcat'),
	url(r'^oracleData/$', views.getOracleData, name='oracle'),
]
