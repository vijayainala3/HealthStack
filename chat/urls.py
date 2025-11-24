from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_chat_view, name='start_chat'),
    path('<int:conversation_id>/', views.chat_page_view, name='chat_page'),
    path('list/', views.chat_list_view, name='chat_list'),
]