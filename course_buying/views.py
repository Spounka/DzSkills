from rest_framework import generics, mixins, response, status, permissions
from .models import Order, Payment
from . import serializers
from courses.models import StudentProgress
from admin_dashboard import models
from django.utils.translation import gettext_lazy as _
from account_balance.models import AccountBalance
from authentication.models import User
from notifications.service import NotificationService
from courses.serializers import CourseListSerializer


# Create your views here.
class OrderAPI(generics.ListCreateAPIView, mixins.RetrieveModelMixin):
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.all()

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        existing_order = Order.objects.filter(
            buyer=request.user, course=request.data.get("course")
        ).filter(payment__status__in=["p", "a"])
        if existing_order.exists():
            return response.Response(
                data={"message": "an existing order already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().post(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.ViewOrderSerializer
        return serializers.OrderSerializer


class PaymentAPI(generics.ListCreateAPIView, mixins.RetrieveModelMixin):
    serializer_class = serializers.PaymentSerializer
    queryset = Payment.objects.all()
    lookup_field = "payment"

    def get_serializer_context(self):
        if pk := self.kwargs.get("pk", None):
            return {"order": Order.objects.get(pk=pk)}
        return {}

    def post(self, request, *args, **kwargs):
        if not kwargs.get("pk", None):
            return response.Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "need to pass an order pk to the url"},
            )
        return super().post(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if pk := kwargs.get("pk", None):
            order = Order.objects.get(pk=pk)
            serializer = self.get_serializer(order.payment)
            return response.Response(status=status.HTTP_200_OK, data=serializer.data)
        return super().retrieve(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if kwargs.get("pk", None) or kwargs.get("payment", None):
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
        receipt: models.Receipt = models.Receipt.objects.filter(
            is_current=True).last()
        payment = Payment.objects.get(pk=kwargs["pk"])
        if payment.status == payment.ACCEPTED:
            return response.Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "code": "payment_already_accepted",
                    "message": _("The payment is already accepted"),
                },
            )
        payment.status = payment.ACCEPTED
        payment.save()
        receipt = receipt.increment()
        receipt.save()
        progress = StudentProgress(
            user=payment.order.buyer, course=payment.order.course, disabled=False
        )
        progress.save()
        teacher = payment.order.course.owner
        if not hasattr(teacher, "accountbalance"):
            teacher.accountbalance = AccountBalance.objects.create(
                user=teacher)
            teacher.save()
        amount = payment.order.course.price

        teacher.accountbalance.balance += int(amount * 0.6)
        User.get_site_admin().accountbalance.balance += int(amount * 0.4)

        teacher.accountbalance.save()
        User.get_site_admin().accountbalance.save()

        NotificationService.create(
            sender=User.get_site_admin(),
            recipient_user=payment.order.buyer,
            notification_type="payment_accepted",
            extra_data={
                "course": CourseListSerializer(
                    payment.order.course, context={"request": request}
                ).data
            },
        )
        if not teacher.is_admin():
            NotificationService.create(
                sender=User.get_site_admin(),
                recipient_user=teacher,
                notification_type="course_bought",
                extra_data={
                    "order": serializers.OrderSerializer(
                        payment.order, context={"request": request}
                    ).data
                },
            )
        payments = Payment.objects.filter(
            order__buyer=payment.order.buyer, order__course=payment.order.course
        )
        payments.update(status=Payment.ACCEPTED)
        Payment.objects.bulk_update(payments, ["status"])
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class RejectPaymentAPI(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        payment = Payment.objects.get(pk=kwargs["pk"])
        payment.status = payment.REFUSED
        payment.save()
        progress = StudentProgress.objects.filter(
            user=payment.order.buyer, course=payment.order.course
        )

        teacher = payment.order.course.owner
        amount = payment.order.course.price
        if progress.exists():
            for p in progress.all():
                teacher.accountbalance.balance -= int(amount * 0.6)
                User.get_site_admin().accountbalance.balance -= int(amount * 0.4)
                p.delete()
            payments = Payment.objects.filter(
                order__buyer=payment.order.buyer, order__course=payment.order.course
            )
            payments.update(status=Payment.REFUSED)
            Payment.objects.bulk_update(payments, ["status"])

        teacher.accountbalance.save()
        User.get_site_admin().accountbalance.save()
        NotificationService.create(
            sender=User.get_site_admin(),
            recipient_user=payment.order.buyer,
            notification_type="payment_refused",
            extra_data={
                "course": CourseListSerializer(
                    payment.order.course, context={"request": request}
                ).data
            },
        )
        return response.Response(status=status.HTTP_204_NO_CONTENT)
