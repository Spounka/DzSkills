from rest_framework import generics, status, response, permissions, mixins
from . import serializers, models


# Create your views here.
class UserProfileAPI(generics.RetrieveUpdateAPIView, mixins.CreateModelMixin):
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.filter()

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
