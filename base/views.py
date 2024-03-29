from django.shortcuts import render, redirect
from .models import Room, Topic, Message
from .forms import RoomForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
# rooms = [{'id': 1, 'name': 'lets learn python'},
#          {'id': 2, 'name': 'lets learn java'},
#          {'id': 3, 'name': 'lets learn node'}]


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
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
            messages.error(request, 'Username or password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':  # pass user data
        # throws the data into the usercretaionform
        form = UserCreationForm(request.POST)
        if form.is_valid():  # check form is valid
            # after user gets created we will bw able to access the user
            user = form.save(commit=False)
            # if the form is valid we get the usernme in lowercase
            user.username = user.username.lower()
            user.save()  # save the user in the database
            login(request, user)  # user that just registered will be logged in
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    # This code retrieves the value of the "q" parameter from the request's GET parameters.
    # If the "q" parameter is present and has a non-null value, then its value is assigned to the variable "q".
    # Otherwise, the variable "q" is assigned an empty string.
    # q = request.GET.get('q','') ---> another option
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # icontains - eg. when you enter py for python it will show
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__username__icontains=q))
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)).order_by('-created')
    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    # gives set of messages that are related to the specific room
    # .order_by('-created') gives the messages in the descending order of the created time, i.e most recent messages
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        # this user will be added to the many to many field
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()  # to get all the users
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url="login")
def createroom(request):
    form = RoomForm()
    if request.method == 'POST':
        print(request.POST)  # prints the input in the terminal
        form = RoomForm(request.POST)
        if form.is_valid():
            # to automatically select the user after logging while creating room
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        # you cannot edit others room
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        # here instance will change the particular room, without it a new room will be created
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        # you cannot delete others room
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': message})
