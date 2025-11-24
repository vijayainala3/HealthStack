# chat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Conversation, Message
from accounts.models import User
from hospital.models import Doctor

@login_required(login_url='login')
def start_chat_view(request):
    # Get all users who are doctors
    doctors = User.objects.filter(role='DOCTOR')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        doctor_user = get_object_or_404(User, pk=doctor_id)
        
        # Check if a conversation already exists between these two users
        # Q objects are used for complex lookups (participant A AND participant B)
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=doctor_user
        ).first() # Get the first one if it exists

        if conversation:
            # If it exists, redirect to the existing chat page (we'll build this next)
            return redirect('chat_page', conversation_id=conversation.id)
        else:
            # If not, create a new conversation
            new_conversation = Conversation.objects.create()
            new_conversation.participants.add(request.user, doctor_user)
            # Redirect to the new chat page
            return redirect('chat_page', conversation_id=new_conversation.id)

    context = {
        'doctors': doctors
    }
    return render(request, 'start_chat.html', context)

# --- ADD THIS NEW VIEW ---
@login_required(login_url='login')
def chat_page_view(request, conversation_id):
    # Get the conversation object
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Security check: Ensure the user is a participant
    if request.user not in conversation.participants.all():
        messages.error(request, "You are not part of this conversation.")
        return redirect('start_chat') # Or wherever appropriate

    # Get all messages for this conversation
    messages_list = conversation.messages.all()

    # Handle sending a new message
    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                body=body
            )
            # Redirect back to the same page to show the new message
            return redirect('chat_page', conversation_id=conversation_id)
        else:
            messages.error(request, "Message body cannot be empty.")

    context = {
        'conversation': conversation,
        'messages_list': messages_list
    }
    return render(request, 'chat_page.html', context)

@login_required(login_url='login')
def chat_list_view(request):
    # Get all conversations where the current user is a participant
    user_conversations = request.user.conversations.all().order_by('-created_at').prefetch_related('participants') # Optimize participant lookup

    # Prepare a list to pass to the template, including the other user
    conversation_list = []
    for conv in user_conversations:
        other_participant = conv.participants.exclude(id=request.user.id).first()
        conversation_list.append({
            'conversation': conv,
            'other_user': other_participant
        })

    context = {
        'conversation_list': conversation_list # Pass the new list
    }
    return render(request, 'chat_list.html', context)