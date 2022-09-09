

from . import views
from django.urls import include, path


urlpatterns = [
    path('', views.home),
    path('manteniance', views.maintenance,name='manteniance'),
    path('form_register_email', views.form_register_email, name='form_register_email'),
    path('register_email', views.register_email, name='register_email'),
    path('indicators', views.getAssets, name='indicators'),
    path('coin_detail/<symbol>', views.coin_detail, name='coin_detalle'),
    path('graphics', views.graph_default, name='graph_default'),
    path('addGraphics', views.graphics, name='addGraphics'),
    path('services',views.services, name='services'),
    path('regulation',views.regultation, name='regulation'),
    path('education',views.education, name='education'),
    path('monitoring',views.monitoring, name='monitoring'),
    path('servicioshome',views.servicioshome, name='servicioshome'),
    path('MonitorMtGox',views.MonitorMtGox, name='MonitorMtGox')
]
