from rest_framework import status, response, generics, viewsets, permissions
from . import models, serializers


# Create your views here.
class TicketViewSet(viewsets.ModelViewSet):
    queryset = models.Report.objects.all()
    serializer_class = serializers.TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

