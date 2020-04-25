from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_swagger.views import get_swagger_view

from . import views


urlpatterns = [
    # Auth
    path('token-auth', obtain_jwt_token),
    path('token-refresh', refresh_jwt_token),

    # Views
    path('organizations/<organization_id>', views.OrganizationDetail.as_view(), name='organization_detail'),
    path('organizations', views.OrganizationList.as_view(), name='organization_list'),
    path('users/<user_id>', views.OrganizationUserDetail.as_view(), name='user_detail'),
    path('users', views.OrganizationUserList.as_view(), name='user_list'),

    # API function based views
    path('ministry-masks/', views.get_ministry_mask_amount),
    path('producer-masks/<producer_id>', views.ProducerMaskDetail.as_view()),
    path('producer-masks/', views.get_all_producer_mask_amount),

    path('ministry-orders/', views.MinistryOrder.as_view()),
    path('ministry-orders/<order_id>', views.get_single_ministry_order),

    path('hospital-orders/<hospital_id>', views.HospitalOrderDetail.as_view()),
    path('hospital-orders/', views.HospitalOrderList.as_view()),

    path('payment-letters/', views.PaymentLetterList.as_view()),

    path('offers/<offer_id>', views.ProducerOfferDetail.as_view()),
    path('offers/', views.ProducerOfferList.as_view()),

    path('payments/', views.PaymentList.as_view()),

    path('deals/', views.DealList.as_view()),
    path('deliveries/', views.DeliveryList.as_view()),
]
