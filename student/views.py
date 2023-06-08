from django.shortcuts import render
from rest_framework import generics, mixins, response, status
from . import serializers, models


# Create your views here.
class StudentAPI(generics.RetrieveUpdateDestroyAPIView, mixins.ListModelMixin):
    serializer_class = serializers.StudentSerializer
    queryset = models.Student.objects.filter()

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, args, **kwargs)
