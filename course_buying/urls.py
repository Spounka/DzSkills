from django.urls import path

from . import views

urlpatterns = [
    path('', views.OrderAPI.as_view(), name="orders-list"),
    path('<int:pk>/', views.OrderAPI.as_view(), name='order-view'),
    path('<int:pk>/payment/', views.PaymentAPI.as_view(), name="payment-view"),

    path('payments/', views.PaymentAPI.as_view(), name="payments"),
    path('payments/<int:payment>/', views.PaymentAPI.as_view(), name="payment-view"),

    path('all/', views.RelatedOrdersAPI.as_view(), name='related-orders')
]
