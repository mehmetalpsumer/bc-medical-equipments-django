from django.contrib import admin

from .models import Organization, OrganizationUser, Delivery, Deal, MinistryOrder, HospitalOrder, PaymentLetter, ProducerOffer, Payment


admin.site.register(Organization)
admin.site.register(OrganizationUser)
admin.site.register(Delivery)
admin.site.register(Deal)
admin.site.register(MinistryOrder)
admin.site.register(HospitalOrder)
admin.site.register(PaymentLetter)
admin.site.register(ProducerOffer)
admin.site.register(Payment)
