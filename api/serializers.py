from rest_framework.serializers import ModelSerializer

from .models import Organization, OrganizationUser, Payment


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'group')


class OrganizationUserSerializer(ModelSerializer):
    class Meta:
        model = OrganizationUser
        fields = '__all__'
        depth = 1


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
