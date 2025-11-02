from datetime import datetime
import random
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from . import models

def lobby(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            request.session['username'] = username
        else:
            names = [
                "Horatio", "Benvolio", "Mercutio", "Lysander", "Demetrius", "Sebastian", "Orsino",
                "Malvolio", "Hero", "Bianca", "Gratiano", "Feste", "Antonio", "Lucius", "Puck", "Lucio",
                "Goneril", "Edgar", "Edmund", "Oswald"
            ]
            request.session['username'] = f"{random.choice(names)}-{hash(datetime.now().timestamp())}"
        return redirect('chat')
    else:
        return render(request, 'lobby.html')

def chat(request: HttpRequest) -> HttpResponse:
    if not request.session.get('username'):
        return redirect('lobby')
    # Handle form submission
    if request.method == 'POST':
        content = request.POST.get("content")
        if content:
            username = request.session.get("username")
            author, _ = models.Author.objects.get_or_create(name=username)
            models.Message.objects.create(author=author, content=content)
        return redirect('chat')   # reload page after sending
    messages = models.Message.objects.order_by("created_at")
    return render(request, 'chat.html', {"messages": messages})


def create_message(request: HttpRequest) -> HttpResponse:
    content = request.POST.get("content")
    username = request.session.get("username")
    if not username:
        return HttpResponse(status=403)
    author, _ = models.Author.objects.get_or_create(name=username)
    if content:
        models.Message.objects.create(author=author, content=content)
        return HttpResponse(status=201)
    else:
        return HttpResponse(status=200)
