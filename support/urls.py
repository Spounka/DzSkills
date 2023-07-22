from django.urls import path
from . import views

urlpatterns = [
    path('', views.TicketCreate.as_view(), name='create-ticket'),
    path('<int:pk>/', views.RetrieveUpdateTicket.as_view(), name="retrieve-update-ticket"),
    path('<int:pk>/conversation/', views.GetSupportConversationAPIView.as_view(), name='retrieve-ticket-conversation')
]
