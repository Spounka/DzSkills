import time

from django.shortcuts import render
from rest_framework import generics, response, mixins, status

import admin_dashboard.models
from . import models, serializers


# Create your views here.

class ListCreateReceipts(generics.ListCreateAPIView):
    queryset = models.Receipt.objects.filter()
    serializer_class = serializers.ReceiptSerializer

    def create(self, request, *args, **kwargs):
        self.serializer_class = serializers.CreateReceiptSerializer
        return super().create(request, *args, **kwargs)


class RetrieveCurrentReceipt(generics.GenericAPIView):
    queryset = models.Receipt.objects.filter()
    serializer_class = serializers.ReceiptSerializer

    def get(self, request, *args, **kwargs):
        time.sleep(1)
        receipt: models.Receipt = self.queryset.filter(is_current=True).last()
        if not receipt:
            receipt = self.queryset.first()
            receipt.is_current = True
            receipt.count = 1
            receipt.save()
        else:
            receipt = receipt.increment()
        serializer = self.get_serializer(receipt, context={'request': request})
        return response.Response(status=status.HTTP_200_OK, data=serializer.data)
