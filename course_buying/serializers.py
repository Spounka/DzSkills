from rest_framework import serializers

import courses.models
from .models import Payment, Order
from authentication import serializers as auth_ser
from courses import serializers as cs


class OrderCreationPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['receipt']


class ViewOrderSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(read_only=True)
    buyer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=courses.models.Course.objects.all())
    buyer = auth_ser.UserSerializer(read_only=True)
    payment = OrderCreationPaymentSerializer()

    def create(self, validated_data):
        user = self.context['request'].user
        payment_data = validated_data.pop('payment')
        order = Order.objects.create(buyer=user, **validated_data)
        payment = Payment.objects.create(order=order, **payment_data)
        payment.save()
        return order

    class Meta:
        model = Order
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['receipt', 'status']


class ListOrderSerializer(serializers.ModelSerializer):
    course = cs.CourseSerializer()
    buyer = auth_ser.UserSerializer(read_only=True)
    payment = PaymentSerializer()

    class Meta:
        model = Order
        fields = '__all__'
        depth = 1
