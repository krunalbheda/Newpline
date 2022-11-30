from email import message
from multiprocessing import context
from pydoc_data.topics import topics
from django.shortcuts import render,redirect    
from django.db.models import Q
from .models import Room,Topic,Message,User
from .forms import RoomForm, UserForm ,CreateUser
# from django.contrib.auth.models import User
# from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate ,login,logout,get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
# Create your views here.

# rooms = [
#     {'id':1, 'name':'lets learn python'},
#     {'id':2, 'name':'design with me'},
#     {'id':3, 'name':'devlper chat'},
# ]
User = get_user_model()

# login page
def loginpage(request):
    
    page = 'login'
   
    if request.user.is_authenticated:
        return redirect('home') 
       
    if request.method == 'POST':
          
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        
        try:
            email = User.objects.get(email= email)
        except:
            messages.error(request,'email or Password is incoorrect')
        
        email = authenticate(request, email=email, password=password) 
        
        if email is not None:
             login(request, email) #login the user            
             messages.info(request, f"You are now logged in as {email}.")
             return redirect('home')
        else:
            messages.error(request,'email or Password is does not exits')

    context = {'page':page}
    return render(request,'base/login_register.html',context)

# logout
def logoutuser(request):
    logout(request)
    messages.info(request, 'You are now logged out')
    return redirect('home')

# User Register Form
def registeruser(request):
    # form = UserCreationForm()
    form = CreateUser()
        
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # user.username = user.username.lower()
            user.save() 
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error occured Registertion')
    
    return render(request,'base/login_register.html',{'form':form})

# Home Page
def home(request):
    q =  request.GET.get('q') if request.GET.get('q') else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) | Q(name__icontains=q) | Q(description__icontains=q)
        )
    
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_message =  Message.objects.filter(Q(room__topic__name__icontains = q))
    context = {'rooms':rooms,'topics':topics,'room_count':room_count,'room_message':room_message}   
    return render(request,'base/home.html',context)

# user profile page
def userprofile(request,pk):
    user = User.objects.get(id=pk)
    rooms  = user.room_set.all()
    room_message = user.room_set.all()  # user.message.set_all()
    topics = Topic.objects.all()
    context = {'user':user,'rooms':rooms,'room_message':room_message,'topics':topics}
    return render(request,'base/profile.html',context)

# room page
def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
            )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
            
    context = {'room':room,'room_messages':room_messages,'participants':participants}       
    return render(request,'base/room.html',context)


# create room
@login_required(login_url='login')
def createroom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    
    if request.method == 'POST':
       topic_name = request.POST.get('topic')
       topic ,created = Topic.objects.get_or_create(name=topic_name)
       
       Room.objects.create(
           host =request.user,
           topic = topic,
           name= request.POST.get('name'),
           description = request.POST.get('description')    
           
       ) 
    #    form = RoomForm(request.POST)
    #    if form.is_valid():
    #        room = form.save(commit=False)
    #        room.host = request.user
    #        room.save()
       return redirect('home')
              
    context = {'form':form,'topics':topics}
    return render(request,'base/room_form.html',context)

# update room
@login_required(login_url='login')
def updateroom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed to edit this room')

    if request.method == 'POST':
        # form = RoomForm(request.POST,instance=room)
        topic_name = request.POST.get('topic')
        topic ,created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        # if form.is_valid():
        #     form.save()
        return redirect('home')    
    
    context = {'form':form,'topics':topics,'room':room}
    return render(request,'base/room_form.html',context)

# delete room
@login_required(login_url='login')
def deleteroom(request,pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed to delete this room')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    return render(request,'base/delete.html',{'obj':room})



# delete message in chat
@login_required(login_url='login')
def deletemsg(request,pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse('You are not allowed to delete this room')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    return render(request,'base/delete.html',{'obj':message})

# update user
@ login_required(login_url='login')
def updateuser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    return render(request,'base/update-user.html',{'form':form})  

# all topics
def topicspage(request):
    q =  request.GET.get('q') if request.GET.get('q') else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request,'base/topics.html',{'topics':topics})

# all activity page
def activtiypage(request):
    room_message = Message.objects.all()[0:5]
    return render(request,'base/activity.html',{'room_message':room_message})