from django.shortcuts import render

# Create your views here.
rooms = [{'id': 1, 'name': 'lets learn python'},
         {'id': 2, 'name': 'lets learn java'},
         {'id': 3, 'name': 'lets learn node'}]


def home(request):
    context = {'rooms': rooms}
    return render(request, 'base/home.html', context)


def room(request):
    return render(request, 'base/room.html')
