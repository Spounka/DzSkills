import time

from django.shortcuts import render
from rest_framework import generics, response, mixins, status, permissions

import admin_dashboard.models
from . import models, serializers


# Create your views here.

class ListCreateReceipts(generics.ListCreateAPIView):
    queryset = models.Receipt.objects.filter()
    serializer_class = serializers.ReceiptSerializer

    def create(self, request, *args, **kwargs):
        self.serializer_class = serializers.CreateReceiptSerializer
        return super().create(request, *args, **kwargs)


class ReceiptsDelete(generics.UpdateAPIView):
    serializer_class = serializers.ReceiptsListDeleteSerializer
    queryset = models.Receipt.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for pk in serializer.validated_data.get('receipts'):
            try:
                level = self.queryset.get(pk=pk)
                level.delete()
            except models.Receipt.DoesNotExist:
                continue
        return response.Response(status=status.HTTP_200_OK)


class RetrieveCurrentReceipt(generics.GenericAPIView):
    queryset = models.Receipt.objects.filter()
    serializer_class = serializers.ReceiptSerializer

    def get(self, request, *args, **kwargs):
        receipt: models.Receipt = self.queryset.filter(is_current=True).last()
        if not receipt:
            receipt = self.queryset.first()
            receipt.is_current = True
            receipt.count = 1
            receipt.save()
        serializer = self.get_serializer(receipt, context={'request': request})
        return response.Response(status=status.HTTP_200_OK, data=serializer.data)


class UpdateDestroyReceipt(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ReceiptSerializer
    queryset = models.Receipt.objects.all()

    def update(self, request, *args, **kwargs):
        receipt = self.get_object()
        if receipt.is_current:
            receipt.count = 0
            receipt.save()
        return super().update(request, *args, **kwargs)


class RetrieveUpdateAdminSettingsView(generics.RetrieveUpdateAPIView):
    queryset = models.AdminConfig.objects.filter().prefetch_related('images')
    serializer_class = serializers.AdminConfigSerializer

    def get_serializer_class(self):
        if self.request.method in ['GET', 'OPTIONS']:
            return serializers.AdminConfigSerializer
        return serializers.AdminConfigUpdateSerializer

    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        if request.data.get('images[0].id', False):
            image = request.FILES.get('images[0].image')
            id = request.data.get('images[0].id')
            instance = models.LandingPageImage.objects.get(pk=id)
            instance.image = image
            instance.save()
        if request.data.get('images[1].id', False):
            image = request.FILES.get('images[1].image')
            id = int(request.data.get('images[1].id'))
            instance = models.LandingPageImage.objects.get(pk=id)
            instance.image = image
            instance.save()
        if request.data.get('images[2].id', False):
            image = request.FILES.get('images[2].image')
            id = int(request.data.get('images[2].id'))
            instance = models.LandingPageImage.objects.get(pk=id)
            instance.image = image
            instance.save()
        return super().update(request, *args, **kwargs)

    def get_object(self):
        models.AdminConfig.load()
        return self.queryset.first()


class CreateListRatingsAPI(generics.ListCreateAPIView):
    serializer_class = serializers.LandingPageRatingSerializer
    queryset = models.LandingPageRating.objects.all()

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UpdateDeleteRatingAPI(generics.UpdateAPIView, mixins.DestroyModelMixin):
    serializer_class = serializers.LandingPageRatingSerializer
    queryset = models.LandingPageRating.objects.all()
