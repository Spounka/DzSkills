from django.shortcuts import render
from rest_framework import generics, mixins, response, status, permissions
from .models import Order, Payment
from . import serializers
from courses.models import StudentProgress
from authentication.models import User


# Create your views here.
class OrderAPI(generics.ListCreateAPIView, mixins.RetrieveModelMixin):
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.all()

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.ViewOrderSerializer
        return serializers.OrderSerializer


class PaymentAPI(generics.ListCreateAPIView, mixins.RetrieveModelMixin):
    serializer_class = serializers.PaymentSerializer
    queryset = Payment.objects.all()
    lookup_field = 'payment'

    def get_serializer_context(self):
        if pk := self.kwargs.get('pk', None):
            return {
                'order': Order.objects.get(pk=pk)
            }
        return {}

    def post(self, request, *args, **kwargs):
        if not kwargs.get('pk', None):
            return response.Response(status=status.HTTP_400_BAD_REQUEST,
                                     data={'message': 'need to pass an order pk to the url'})
        return super().post(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if pk := kwargs.get('pk', None):
            order = Order.objects.get(pk=pk)
            serializer = self.get_serializer(order.payment)
            return response.Response(status=status.HTTP_200_OK, data=serializer.data)
        return super().retrieve(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk', None) or kwargs.get('payment', None):
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)


class RelatedOrdersAPI(generics.ListAPIView):
    serializer_class = serializers.ListOrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.order_set


class ListPaymentsForAdminAPI(generics.ListAPIView):
    serializer_class = serializers.ListPaymentsForAdminSerializer
    queryset = Payment.objects.filter()


class AcceptPaymentAPI(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        payment = Payment.objects.get(pk=kwargs['pk'])
        payment.status = payment.ACCEPTED
        payment.save()
        progress = StudentProgress(user=payment.order.buyer, course=payment.order.course)
        progress.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class RejectPaymentAPI(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        payment = Payment.objects.get(pk=kwargs['pk'])
        payment.status = payment.REFUSED
        payment.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
