from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Notification
from main.serializers import NotificationGetSerializer


class GetNotificationView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationGetSerializer

    def get(self, request):
        notifications = Notification.objects.all()
        serializer = self.get_serializer(notifications, many=True)

        return Response({'success': True, 'notification': serializer.data})


class NotificationDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationGetSerializer

    def get(self, request, pk):
        notification = Notification.objects.get(pk=pk)
        serializer = self.get_serializer(notification)
        notification.status = True
        notification.save()

        return Response({'success': True, 'notification': serializer.data})

    def delete(self, request, pk):
        notifications = Notification.objects.get(pk=pk)
        notifications.delete()

        return Response({'success': True, 'message': 'Notification Deleted Successfully!' })


