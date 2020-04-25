import uuid, datetime
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import Response, APIView
from rest_framework.decorators import api_view

from .serializers import OrganizationSerializer, OrganizationUserSerializer, PaymentSerializer
from . import models
from . import blockchain as bc

'''
Generic views
'''


class OrganizationList(ListCreateAPIView):
    queryset = models.Organization.objects.all()
    serializer_class = OrganizationSerializer


class OrganizationDetail(RetrieveUpdateDestroyAPIView):
    queryset = models.Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_url_kwarg = 'organization_id'


class OrganizationUserList(ListCreateAPIView):
    queryset = models.OrganizationUser.objects.all()
    serializer_class = OrganizationUserSerializer


class OrganizationUserDetail(RetrieveUpdateDestroyAPIView):
    queryset = models.OrganizationUser.objects.all()
    serializer_class = OrganizationUserSerializer
    lookup_url_kwarg = 'user_id'


'''
Non-generic views
'''


@api_view(['GET'])
def get_ministry_mask_amount(request):
    masks = bc.get_ministry_masks()

    if masks:
        return Response({"masks": int(masks)})
    return Response({"error": True}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


'''
Producer functions
'''


class ProducerMaskDetail(APIView):
    def get(self, request, producer_id):
        """
        Get mask amount from a single producer
        :param request:
        :param producer_id:
        :return:
        """
        producer = models.Organization.objects.get(id=producer_id)

        if producer is None or producer.group != 'PRODUCER':
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        mask_amount = bc.get_producer_masks(producer.key)
        print(mask_amount)

        return Response({
            "producer": OrganizationSerializer(producer).data,
            "masks": mask_amount
        })

    def put(self, request, producer_id):
        """
        Update mask amount of a producer
        :param request:
        :param producer_id:
        :return:
        """
        mask_amount = request.data['masks']
        producer = models.Organization.objects.get(id=producer_id)

        if producer is None or producer.group != 'PRODUCER':
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        bc.update_mask(producer.key, int(mask_amount))

        return Response({
            "producer": OrganizationSerializer(producer).data,
            "masks": mask_amount
        })


@api_view(['GET'])
def get_all_producer_mask_amount(request):
    """
    Gets mask amount from all producers.
    :param request:
    :return:
    """
    producers = models.Organization.objects.filter(group='PRODUCER')

    mask_amounts = []
    for producer in producers:
        mask_amount = bc.get_producer_masks(producer.key)

        mask_amounts.append({
            "producer": OrganizationSerializer(producer).data,
            "masks": mask_amount
        })

    return Response(mask_amounts)


@api_view(['GET'])
def get_all_hospital_mask_amount(request):
    """
    Gets mask amount from all hospitals.
    :param request:
    :return:
    """
    producers = models.Organization.objects.filter(group='HOSPITAL')

    mask_amounts = []
    for producer in producers:
        mask_amount = bc.get_(producer.key)
        mask_amounts.append({
            "producer": OrganizationSerializer(producer).data,
            "masks": mask_amount
        })

    return Response(mask_amounts)


'''
Ministry functions
'''


class MinistryOrder(APIView):
    def get(self, request):
        """
        Get all ministry orders
        :param request:
        :return:
        """
        orders = list(models.MinistryOrder.objects.all())

        if "unpaid" in request.query_params:
            payments = models.Payment.objects.all()
            for payment in payments:
                for order in orders:
                    if payment.order == order.id:
                        orders.remove(order)

        result = []
        for order in orders:
            bc_order_id = order.id
            bc_result = bc.get_ministry_order_info(bc_order_id)

            if bc_result is None:
                continue

            result.append(bc_result)

        return Response(result)

    def post(self, request):
        """
        Create a ministry order
        :param request:
        :return:
        """

        mask_amount = request.data['maskAmount']
        end_date = request.data['endDate']  # DD/MM/YYYY as string

        if mask_amount is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            mask_amount = int(mask_amount)

        ministry = models.Organization.objects.filter(group='MINISTRY')[0]
        order_id = uuid.uuid1()
        ministry_order = models.MinistryOrder(
            id=order_id,
            ministry=ministry
        )

        bc_success = bc.make_ministry_order(order_id, mask_amount, end_date)

        if bc_success is False:
            return Response({"error": "Blockchain error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        ministry_order.save()
        return Response({"id": order_id}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_single_ministry_order(request, order_id):
    """
    Get a single ministry order
    :param request:
    :param order_id:
    :return:
    """
    order = get_object_or_404(models.MinistryOrder, id=order_id)

    if order is None:
        return Response({"error": True}, status=status.HTTP_404_NOT_FOUND)

    bc_response = bc.get_ministry_order_info(order_id)

    if bc_response is None:
        return Response({"error": "Blockchain request failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(bc_response, status=status.HTTP_200_OK)


'''
Deal functions
'''


class DealList(APIView):
    def get(self, request):
        """
        Get all deals
        :param request:
        :return:
        """
        deals = models.Deal.objects.all()

        if 'producer' in request.query_params:
            deals = deals.filter(producer__id=request.query_params['producer'])

        result = []
        for deal in deals:
            delivery_id = bc.get_delivery_info(deal)
            result.append({
                "deal": deal.id,
                "delivery": delivery_id
            })

        return Response(result)


class DeliveryList(APIView):
    def get(self, request):
        """
        Get all deliveries
        :param request:
        :return:
        """
        deliveries = models.Delivery.objects.all()
        result = []
        for delivery in deliveries:
            obj = bc.get_delivery_info(delivery.id)

            if obj is not None:
                obj['producer'] = OrganizationSerializer(delivery.producer).data


            result.append(obj)

        return Response(result)

    def patch(self, request):
        delivery_id = request.data['delivery']
        delivery_status = request.data['status']

        if delivery_id is None or delivery_status is None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        bc_response = bc.update_delivery(delivery_id, delivery_status)

        if bc_response is False:
            return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({}, status=status.HTTP_202_ACCEPTED)

'''
Hospital functions
'''


class HospitalOrderDetail(APIView):
    def get(self, request, hospital_id):
        """
        Gets hospital orders from a single hospital.
        :param request:
        :return:
        """
        hospital = get_object_or_404(models.Organization, id=hospital_id)

        if hospital.group != 'HOSPITAL':
            return Response({"error": "Organization is not hospital"}, status=status.HTTP_400_BAD_REQUEST)

        hospital_obj = {
            "id": hospital.id,
            "name": hospital.name,
            "orders": []
        }

        orders = models.HospitalOrder.objects.filter(hospital=hospital)

        for order in orders:
            bc_result = bc.get_hospital_order_info(order.id)

            if bc_result is None:
                continue

            hospital_obj["orders"].append(bc_result)

        orders = hospital_obj["orders"]
        hospital_obj["orders"] = sorted(orders, key=lambda k: k['date'], reverse=True)

        return Response(hospital_obj)

    def post(self, request, hospital_id):
        hospital_id = int(hospital_id)
        mask_amount = request.data["masks"]
        urgency = request.data["urgency"]

        hospital = get_object_or_404(models.Organization, id=hospital_id)

        if hospital.group != 'HOSPITAL':
            return Response({"error": "Wrong organization"}, status=status.HTTP_400_BAD_REQUEST)

        order_key = uuid.uuid1()
        hospital_order = models.HospitalOrder(
            id=order_key,
            hospital=hospital
        )

        bc_success = bc.make_hospital_order(order_key, int(mask_amount), hospital.key, urgency)

        if not bc_success:
            return Response({"error": "Blockchain error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        hospital_order.save()
        return Response({"order": order_key})


class HospitalOrderList(APIView):
    def get(self, request):
        """
            Gets hospital orders from all hospitals.
            :param request:
            :return:
            """
        hospitals = models.Organization.objects.filter(group='HOSPITAL')

        result = []
        for hospital in hospitals:
            hospital_obj = {
                "id": hospital.id,
                "name": hospital.name,
                "orders": [],
                "dirty": False
            }

            orders = models.HospitalOrder.objects.filter(hospital=hospital)

            for order in orders:
                bc_result = bc.get_hospital_order_info(order.id)

                if bc_result is None or bc_result["amount"] == -1:
                    hospital_obj["dirty"] = True
                    continue
                hospital_obj["orders"].append(bc_result)

            result.append(hospital_obj)

        return Response(result)

    def patch(self, request):
        order_id = request.data['order']
        order_status = request.data['status']

        if order_id is None or order_status is None:
            return Response({"error": "Incomplete data"}, status=status.HTTP_400_BAD_REQUEST)

        bc_success = bc.update_hospital_order(order_id, order_status)

        if bc_success is False:
            return Response({"error": "Blockchain request failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(True, status=status.HTTP_202_ACCEPTED)


'''
Bank functions
'''


class PaymentLetterList(APIView):
    def get(self, request):
        """
        Get all payment letters
        :param request:
        :return:
        """
        payment_letters = models.PaymentLetter.objects.all()

        if 'bank' in request.query_params:
            payment_letters = payment_letters.filter(bank__id=request.query_params['bank'])

        if 'producer' in request.query_params:
            producer_payments = models.Payment.objects.filter(producer__id=request.query_params['producer'])
            orders = list(map(lambda x: x['order'], PaymentSerializer(producer_payments, many=True).data))
            payment_letters = payment_letters.filter(order__in=orders)

        result = []
        for payment_letter in payment_letters:
            letter = bc.get_payment_letter_info(payment_letter.id)
            letter["name"] = payment_letter.bank.name
            letter["order"] = payment_letter.order
            result.append(letter)

        return Response(result)

    def post(self, request):
        """
        Create a payment letter from a bank
        :param request:
        :return:
        """
        bank_id = request.data["bank"]
        payment_id = request.data["payment"]

        bank = get_object_or_404(models.Organization, id=bank_id)

        if bank.group != "BANK":
            return Response({"error": "Wrong organization type."}, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(models.Payment, id=payment_id)

        payment_letter_id = uuid.uuid1()
        payment_letter = models.PaymentLetter(
            id=payment_letter_id,
            bank=bank,
            order=payment.order
        )

        bc_success = bc.create_payment_letter(payment_letter_id, bank.key, str(int(payment.price)))

        if bc_success is False:
            return Response({"error": "Blockchain request failed for payment letter."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        payment_letter.save()

        # Get order
        order = bc.get_ministry_order_info(payment.order)
        winner_offer = order['winner']

        if winner_offer is None:
            # TODO handle
            pass


        # Get offer
        offer = bc.get_producer_offer_info(winner_offer)
        producer_id = offer['producer']
        producer = get_object_or_404(models.Organization, key=producer_id)

        if producer_id is None:
            # TODO handle
            pass

        # Create deal
        deal_id = uuid.uuid1()
        deal = models.Deal(
            id=deal_id,
            producer=producer,
            letter=payment_letter_id
        )
        bc_success = bc.create_deal(deal_id, producer_id, payment.price, payment_letter_id, order['amount'])

        if bc_success is False:
            # TODO handle
            return
        deal.save()

        # Create delivery
        delivery_id = uuid.uuid1()
        delivery = models.Delivery(
            id=delivery_id,
            producer=producer
        )
        bc_success = bc.create_delivery(delivery_id, producer_id, "1")

        if bc_success is False:
            # TODO handle
            return
        delivery.save()

        return Response({"letter": payment_letter_id, "deal": deal_id, "delivery": delivery_id})


'''
Offers
'''


class ProducerOfferList(APIView):
    def get(self, request):
        """
        Get all producer offers.
        :param request:
        :return:
        """
        offers = models.ProducerOffer.objects.all()

        if 'producer' in request.query_params:
            offers = offers.filter(producer=request.query_params['producer'])

        if 'order' in request.query_params:
            offers = offers.filter(order=request.query_params['order'])

        result = []
        for offer in offers:
            bc_result = bc.get_producer_offer_info(offer.id)
            if bc_result:
                result.append(bc_result)

        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create an offer for an order.
        :param request:
        :return:
        """
        producer_id = request.data["producer"]
        order_id = request.data["order"]
        offer_price = request.data["offer"]

        producer = get_object_or_404(models.Organization, id=producer_id)

        if producer.group != "PRODUCER":
            return Response({"error": "Wrong organization type."}, status=status.HTTP_400_BAD_REQUEST)

        offer_id = uuid.uuid1()
        offer = models.ProducerOffer(
            id=offer_id,
            producer=producer,
            order=order_id
        )

        bc_success = bc.create_producer_offer(offer_id, producer.key, order_id, offer_price)

        if bc_success is False:
            return Response({"error": "Blockchain request failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        offer.save()
        return Response({"id": offer_id}, status=status.HTTP_201_CREATED)


class ProducerOfferDetail(APIView):
    def get(self, request, offer_id):
        """
        Get a single offer.
        :param request:
        :param offer_id:
        :return:
        """

        bc_response = bc.get_producer_offer_info(offer_id)
        if bc_response is None:
            return Response({"error": "Blockchain request error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(bc_response, status=status.HTTP_200_OK)

    def post(self, request, offer_id):
        """
        Accept the offer for an order.
        :param request:
        :param offer_id: Blockchain ID of the offer.
        :return:
        """

        offer = get_object_or_404(models.ProducerOffer, id=offer_id)
        order_id = offer.order

        if order_id is None or offer_id is None:
            return Response({"error": "Missing data"}, status=status.HTTP_400_BAD_REQUEST)

        bc_response = bc.accept_offer(offer_id, order_id)

        if bc_response is False:
            return Response({"error": "Blockchain request failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Offer accepted"}, status=status.HTTP_202_ACCEPTED)


'''
Payments
'''


class PaymentList(APIView):
    def get(self, request):
        """
        Get all payments. Can be filtered with order.
        :param request:
        :return:
        """
        payments = models.Payment.objects.all()

        if 'order' in request.query_params:
            payments = payments.filter(order=request.query_params['order'])

        payments = PaymentSerializer(payments, many=True).data

        for payment in payments:
            payment['producerName'] = models.Organization.objects.get(id=payment['producer']).name

        if 'unpaid' in request.query_params:
            payment_letters = models.PaymentLetter.objects.all()
            result = []
            for payment in payments:
                found = False
                for letter in payment_letters:
                    if payment['order'] == letter.order:
                        found = True

                if not found:
                    result.append(payment)
            payments = result


        return Response(payments)

    def post(self, request):
        """
        Create a new payment.
        :param request:
        :return:
        """

        price = request.data['price']
        order = request.data['order']
        producer_id = request.data['producer']

        producer = get_object_or_404(models.Organization, key=producer_id)

        if order is None or price is None:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        payment = models.Payment(price=price, order=order, producer=producer)
        payment.save()

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
