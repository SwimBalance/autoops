from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^operation/$', views.operation, name='operation'),
    url(r'^tomcatData/$', views.get_tomcat_data, name='tomcat'),
    url(r'^oracleData/$', views.get_oracle_data, name='oracle'),
    url(r'^searchtomcat/$', views.search_tomcat, name='oracle'),
    url(r'^login/$', views.login, name='login'),
]
