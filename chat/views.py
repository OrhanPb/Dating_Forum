from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Message
from django.contrib.auth.models import User

@login_required
def chat_room(request, receiver_id):
    receiver = User.objects.get(id=receiver_id)
    messages_sent = Message.objects.filter(sender=request.user, receiver=receiver)
    messages_received = Message.objects.filter(sender=receiver, receiver=request.user)
    messages = messages_sent.union(messages_received).order_by('timestamp')
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=receiver, content=content)
            return redirect('chat_room', receiver_id=receiver_id)
    return render(request, 'chat/chat_room.html', {'messages': messages, 'receiver': receiver})
