from django.urls import path
from . import views
from django.urls import path
urlpatterns = [
    path('', views.index, name='home'),
    path('about', views.about,  name='about'),
    path('password', views.password,  name='password'),
    path('scenarios/', views.scenario_list, name='scenario_list'),
    path('scenarios/random/', views.random_scenario, name='random_scenario'),
    path('scenarios/<int:sc_id>/', views.scenario_chat, name='scenario_chat'),
    path('scenarios/<int:sc_id>/answer/', views.scenario_answer, name='scenario_answer'),
    path('session-expired/', views.session_expired, name='session_expired'),
    path('logout/', views.logout_user, name='logout'),
    path('test', views.tests,  name='tests'),
    path('test/<int:test_id>/start/', views.start_test, name='start_test'),
    path('test/<int:test_id>/', views.test_detail, name='test_detail'),
    path('test/<int:test_id>/result/', views.test_result, name='test_result'),
    path('posts/', views.post_feed, name='post_feed'),
    path('post/<int:post_id>/check/', views.check_post, name='check_post'),
]