"""army_cms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from complaints import views

urlpatterns = [
    url(r'^$',views.IndexView.as_view(), name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, {'template_name': 'complaints/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^add-complaint/',views.ComplaintCreateView.as_view(),name='add-complaint'),
    url(r'^pending-complaints/(?P<category>\w+)/$',views.PendingComplaintsView.as_view(),name='pending-complaints'),
    url(r'^list-complaints/(?P<category>\w+)/$',views.ListComplaintsView.as_view(),name='list-complaints'),
    url(r'^list-settled-complaints/(?P<category>\w+)/$',views.ListSettledComplaintsView.as_view(),name='settled-complaints'),
    url(r'^list-returned-complaints/$',views.ListReturnedComplaintsView.as_view(),name='returned-complaints'),
    url(r'^returned/(?P<complaint>[0-9]+)/', views.ReturnedDetailView.as_view(), name='returned-detail'),
    url(r'^view/(?P<complaint>[0-9]+)/', views.ComplaintView.as_view(), name='complaint-view'),
    url(r'^complaint/(?P<complaint>[0-9]+)/', views.ComplaintDetailView.as_view(), name='complaint-detail'),
    url(r'^complaint/delete/(?P<complaint>[0-9]+)/', views.ComplaintDeleteView.as_view(), name='complaint-delete'),
    url(r'^update-reply-letter/(?P<complaint>[0-9]+)/', views.UpdateReplyLetterMisView.as_view(), name='reply-letter'),
    #url(r'^report/', views.ReportView.as_view(), name='report'),
    url(r'^report/(?P<category>\w+)/', views.CategoryReportView.as_view(), name='category-report'),
    # url(r'^csv-report/(?P<dept>\w+)/', views.csv_report, name='csv-report')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

