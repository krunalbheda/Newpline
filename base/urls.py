from django.urls import path
from . import views

urlpatterns = [
    
    path('login/',views.loginpage,name="login"),
    path('logout/',views.logoutuser,name="logout"),
    path('register/',views.registeruser,name="register"),
    
    path('',views.home ,name='home') ,
    path('room/<str:pk>/', views.room, name='room'),
    
    path('create-room/', views.createroom, name='create-room'),
    path('update-room/<str:pk>/', views.updateroom, name='update-room'),
    path('delete-room/<str:pk>/', views.deleteroom, name='delete-room'),
    
    path('delete-message/<str:pk>/', views.deletemsg, name="delete-message"),
    
    path('profile/<str:pk>/',views.userprofile,name="user-profile"),
    
    path('update-user/', views.updateuser, name='update-user'),
    
    path('topics/', views.topicspage, name='topics'),
    path('activity/', views.activtiypage, name='activity')
    
    
    
]
 