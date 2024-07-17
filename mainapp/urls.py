from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import get_messages, avito_chats, user_login

urlpatterns = [
    path('webhook/', views.webhook_endpoint, name='webhook_endpoint'),

    path('login/', user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('', views.avito_accounts, name='avito_accounts'),
    path('avito_chats', views.avito_chats, name='avito_chats'),

    path('chats/', avito_chats, name='avito_chats'),
    path('messages/<str:chat_id>/', get_messages, name='get_messages'),
    path('ignored_chats/check/<str:chat_id>/', views.check_ignored_chat, name='check_ignored_chat'),
    path('ignored_chats/toggle/<str:chat_id>/', views.toggle_ignored_chat, name='toggle_ignored_chat'),
    path('send_message/', views.send_message_endpoint, name='send_message_endpoint'),

    path('whatsapp_accounts', views.whatsapp_accounts, name='whatsapp_accounts'),
    path('whatsapp_chats', views.whatsapp_chats, name='whatsapp_chats'),
    path('whatsapp_broadcasts', views.whatsapp_broadcasts, name='whatsapp_broadcasts'),
    path('whatsapp_templates', views.whatsapp_templates, name='whatsapp_templates'),
    path('whatsapp_send_message', views.whatsapp_send_message, name='whatsapp_send_message'),
    path('whatsapp_statistics', views.whatsapp_statistics, name='whatsapp_statistics'),

    path('accounts/', views.avito_accounts, name='avito_accounts'),
    path('accounts/add/', views.add_account, name='add_account'),
    path('accounts/edit/<int:account_id>/', views.edit_account, name='edit_account'),
    path('accounts/delete/<int:account_id>/', views.delete_account, name='delete_account'),
]
