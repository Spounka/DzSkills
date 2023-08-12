from rest_framework import generics
from . import models
from . import serializers


# Create your views here.
class GetAccountBalance(generics.RetrieveAPIView):
    serializer_class = serializers.AccountBalanceSerializer
    queryset = models.AccountBalance.objects.all()

    def get_object(self):
        return self.request.user.accountbalance


class RequestMoneyView(generics.ListCreateAPIView):
    serializer_class = serializers.MoneyRequestSerializer
    queryset = models.MoneyRequest.objects.all()

    # def get_queryset(self):
    #     return self.queryset.filter(account__user=self.request.user)
    #
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ApproveMoneyRequest(generics.UpdateAPIView):
    serializer_class = serializers.MoneyRequestSerializer
    queryset = models.MoneyRequest.objects.all()

    def update(self, request, *args, **kwargs):
        request.data['type'] = 'approve'
        return super().update(request, *args, **kwargs)


class RejectMoneyRequest(generics.UpdateAPIView):
    serializer_class = serializers.MoneyRequestSerializer
    queryset = models.MoneyRequest.objects.all()

    def update(self, request, *args, **kwargs):
        request.data['type'] = 'reject'
        return super().update(request, *args, **kwargs)
