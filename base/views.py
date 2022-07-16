from django.shortcuts import render, redirect
from .models import Room, Message
from .forms import RoomForm
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # Get all rooms from the database that match with the query 'q'
    rooms = Room.objects.filter(Q(name__icontains=q) | Q(description__icontains=q)) 
    room_count = rooms.count()
    context = {'rooms': rooms, 'room_count': room_count}
    # context allows us to use the context data on an html file
    return render(request, 'base/home.html', context)

def room(request, pk): # pass in the pk parameter of a room (id)
    room = Room.objects.get(id=pk) # get a specific room from the database        
    room_messages = room.message_set.all().order_by('-created') # get all messages on this room

    if request.method == 'POST':
        if len(request.POST.get('body')) != 0:
            message = Message.objects.create(
                user=request.user,
                room=room,
                body=request.POST.get('body'),
            )
            return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages}
    return render(request, 'base/room.html', context)

# don't let the user create rooms unless he is logged id, redirect them to login page
@login_required(login_url='login')
def createRoom(request):
    page = 'create'
    if request.method == 'POST':
        if request.POST.get('name') != '':
            room = Room.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                host=request.user,
            )
            room.save()
            context = {'room': room}
            return render(request, 'base/room.html', context)
        else:
            return render(request, 'base/room_form.html')
    return render(request, 'base/room_form.html')


# don't let the user create rooms unless he is logged id, redirect them to login page
@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) # Fill out the form with the room data

    if request.user != room.host:
        return HttpResponse('You are not allowed to edit this room')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            context = {'room': room}
            return render(request, 'base/room.html', context)
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

# don't let the user create rooms unless he is logged id, redirect them to login page
@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed to delete this room')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "incorrect username or password")

    context={'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    context = {'form': form}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) 
            # commit lets us get the user object right away and modify it before
            # actually sending it to the database
            user.username = user.username.lower()
            user.save()
            login(request, user) # login user right away
            return redirect('home')
        else:
            messages.error(request, 'Error registering')

    return render(request, 'base/login_register.html', context)

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    room = message.room
    context = {'room': room}
    if request.user != message.user:
        return HttpResponse('You are not allowed to delete this message')

    if request.method == 'POST':
        message.delete()
        return redirect('room', pk=room.id)
    return render(request, 'base/delete.html', {'obj': message})