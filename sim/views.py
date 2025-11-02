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
            request.session['username'] = f"{random.choice(names)}-{random.randint(1000, 9999)}"
        return redirect('chat')
    else:
        return render(request, 'lobby.html')


def chat(request: HttpRequest) -> HttpResponse:
    if not request.session.get('username'):
        return redirect('lobby')
    messages = models.Message.objects.order_by("created_at")
    return render(request, 'chat.html', {"messages": messages})
