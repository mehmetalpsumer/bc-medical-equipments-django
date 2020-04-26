import requests, json, time, datetime, os

bc_url = os.environ["BLOCKCHAIN_API_URL"]


def get_timestamp_in_millis():
    """
    Get current time in millis.
    :return: Time as string.
    """
    return str(int(round(time.time() * 1000)))


def millis_to_str(millis):
    """
    Get given millis as a human readable date time.
    :param millis:
    :return: Date time string.
    """
    ms = int(millis)
    return datetime.datetime.fromtimestamp(ms/1000.0).strftime("%Y-%m-%d %H:%M")


def create_admin():
    """
    Enrolls admin on blockchain.
    :return:
    """
    print("Enrolling admin...")
    url = bc_url + "enrollAdmin"
    data = {
        "adminName": "admin",
        "password": "adminpw",
    }

    try:
        requests.post(url, data, timeout=10)
        print("Admin enrolled!")
    except:
        print("Error while enrolling admin...")


def blockchain_request(path, data):
    """
    Template for blockchain request. All blockchain functions use this.
    :param path: URL path after the API section.
    :param data: Data to be sent in the request body.
    :return: Response body as dictionary type.
    """
    create_admin()
    url = bc_url + path
    print("Sending request to " + url)
    print(data)
    response_content = None
    try:
        response = requests.post(url, json=data, timeout=10)
        response_content = response.content
    except Exception as inst:
        print("Error!")
        print(inst)
        return None

    try:
        response_dict = json.loads(response_content)
        print(response_dict)
        return response_dict
    except:
        return response_content


def get_ministry_masks():
    """
    Get mask amount at hand for ministry.
    :return: Mask amount.
    """
    path = "getMinistryInfo"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
    }
    resp = blockchain_request(path, data)
    if resp is not None and "maskAmount" in resp:
        return resp["maskAmount"]
    return None


def get_producer_masks(producer_id):
    """
    Get mask amount at hand for given producer.
    :param producer_id: ID of the producer in the blockchain.
    :return: Mask amount
    """
    path = "getProducerInfo"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {"coID": str(producer_id)}
    }
    resp = blockchain_request(path, data)

    if resp is None:
        return -1

    if 'amount' not in resp:
        return -1

    return int(resp['amount'])


def get_ministry_order_info(order_id):
    """
    Get ministry order details
    :param order_id: Blockchain id of the order
    :return: Amount and end date
    """
    path = "getMinistryOrderInfo"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {"orderID": str(order_id)}
    }
    resp = blockchain_request(path, data)

    if resp is None:
        return None

    result = {
        "id": resp["orderID"],
        "amount": resp["amount"],
        "endDate": resp["endDate"],
        "openDate": millis_to_str(resp["openDate"]),
        "winner": None if resp["winnerOffer"] == 'none' else resp["winnerOffer"]
    }

    return result


def make_ministry_order(order_id, mask_amount, date_str):
    """
        Make a new order by ministry
        :param order_id: Blockchain id of order
        :param mask_amount: Mask amount requested
        :return: Success of transaction as bool
        """
    path = "makeMinistryOrder"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {
            "orderID": str(order_id),
            "maskAmount": str(mask_amount),
            "endDate": date_str,
            "date": get_timestamp_in_millis()
        }
    }
    resp = blockchain_request(path, data)
    return resp is not None


def update_mask(producer_id, mask_amount):
    """
    Update mask stocks of a producer
    :param producer_id: Blockchain id of producer
    :param mask_amount: Mask amount to be added
    :return: Success of transaction as bool
    """
    path = "updateMask"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {
            "coID": str(producer_id),
            "amount": str(mask_amount)
        }
    }
    resp = blockchain_request(path, data)
    return resp is not None


def make_hospital_order(order_id, mask_amount, hospital_id, urgency):
    """
    Makes order from hospital for their needs
    :param order_id: Blockchain key for the order
    :param mask_amount: Mask amount needed by hospital
    :param hospital_id: Blockchain key for the hospital
    :return:
    """
    path = "makeHospitalOrder"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {
            "orderID": str(order_id),
            "maskAmount": str(mask_amount),
            "hosID": str(hospital_id),
            "urgency": str(urgency),
            "date": get_timestamp_in_millis(),
            "deliveryStatus": "0"
        }
    }
    resp = blockchain_request(path, data)
    return resp is not None


def update_hospital_order(order_id, status):
    """
    Updates hospital order status
    :param order_id: Blockchain key for the order
    :return: Success of the transaction
    """
    path = "updateHospitalDelivery"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {
            "orderID": str(order_id),
            "deliveryStatus": str(status)
        }
    }
    resp = blockchain_request(path, data)
    return resp is not None


def get_delivery_info(deal_id):
    path = "getDeliveryInfo"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {"delID": str(deal_id)}
    }
    resp = blockchain_request(path, data)

    if resp is None:
        return None

    return {
        "id": resp["delID"],
        "date": millis_to_str(resp["date"]),
        "status": resp["status"]
    }


def get_hospital_order_info(order_id):
    """
    Get hospital order mask amount
    :param order_id: Blockchain key for oder
    :return: Number of masks ordered with priority
    """
    path = "getHospitalOrderInfo"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {"orderID": str(order_id)}
    }
    resp = blockchain_request(path, data)

    if resp is None:
        return None

    hospital_order = {
        "id": str(order_id),
        "amount": int(resp["amount"]),
        "urgency": int(resp["urgency"]),
        "date": millis_to_str(resp["date"]),
        "status": resp["deliveryStatus"]
    }

    return hospital_order


def get_producer_offer_info(offer_id):
    """
    Get offer made by producer
    :param offer_id: Blockchain key for offer
    :return: Offer
    """
    path = "getProducerOfferInfo"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {"offerID": str(offer_id)}
    }
    resp = blockchain_request(path, data)

    if resp is None:
        return None

    offer = {
        "id": resp["offerID"],
        "producer": resp["coID"],
        "order": resp["orderID"],
        "offer": resp["offer"],
        "status": resp["status"],
        "date": millis_to_str(resp["date"])
    }
    return offer


def create_producer_offer(offer_id, producer_id, order_id, offer):
    """
    Create offer by producers.
    :param offer_id:
    :param producer_id:
    :param order_id:
    :param offer:
    :return:
    """
    path = "makeProducerOffer"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {
            "offerID": str(offer_id),
            "coID": str(producer_id),
            "orderID": str(order_id),
            "offer": str(offer),
            "date": get_timestamp_in_millis()
        }
    }
    resp = blockchain_request(path, data)

    return resp is not None


def accept_offer(offer_id, order_id):
    """
    Accept offer for an order.
    :param offer_id: Blockchain ID of the offer.
    :param order_id: Blockchain ID of the order.
    :return: Success of transaction.
    """
    path = "acceptOffer"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {
            "offerID": str(offer_id),
            "orderID": str(order_id)
        }
    }

    resp = blockchain_request(path, data)
    return resp is not None


def create_deal(deal_id, producer_id, price, letter_id, mask_amount):
    """
    Creates a deal in blockchain
    :param deal_id:
    :param producer_id:
    :param price:
    :param letter_id:
    :param mask_amount:
    :return: True if anything is returned in the body, else False
    """
    path = "createDeal"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {
            "dealID": str(deal_id),
            "coID": str(producer_id),
            "dealPrice": str(price),
            "letterID": str(letter_id),
            "maskAmount": str(mask_amount),
            "date": get_timestamp_in_millis(),
        }
    }
    resp = blockchain_request(path, data)
    return resp is not None


def create_delivery(delivery_id, producer_id, status=1):
    """
    Create a new delivery.
    :param delivery_id: UUID of the delivery.
    :param producer_id: Blockchain ID of the producer.
    :param status: Status of the delivery, 1 by default.
    :return: Success of the transaction.
    """
    path = "createDelivery"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {
            "delID": str(delivery_id),
            "coID": str(producer_id),
            "status": str(status),
            "date": get_timestamp_in_millis(),
        }
    }
    resp = blockchain_request(path, data)
    return resp is not None


def update_delivery(delivery_id, status):
    """
    Update status of a delivery.
    :param delivery_id: Blockchain ID of the delivery.
    :param status: New status of the delivery.
    :return: Success of the transaction as bool.
    """
    path = "updateDelivery"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {
            "delID": str(delivery_id),
            "status": str(status)
        }
    }
    resp = blockchain_request(path, data)
    return resp is not None


def get_payment_letter_info(letter_id):
    """
    Get payment amount
    :param letter_id: Bc id of the letter
    :return: Payment letter as dictionary.
    """
    path = "getPaymentLetterInfo"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {
            "letterID": str(letter_id),
        }
    }
    resp = blockchain_request(path, data)

    if resp is None:
        return None

    return {
        "id": resp["letterID"],
        "bank": resp["bankID"],
        "price": int(resp["price"]),
        "date": millis_to_str(resp["date"])
    }


def create_payment_letter(letter_id, bank_id, price):
    """
    Create a payment letter by bank
    :param letter_id: UUID of the payment letter.
    :param bank_id: Blockchain ID of the bank.
    :param price: Price of the payment.
    :return: Boolean of success of transaction
    """
    path = "createPaymentLetter"
    data = {
        "username": "admin",
        "channel": "channel1",
        "smartcontract": "cc",
        "args": {
            "letterID": str(letter_id),
            "bankID": str(bank_id),
            "price": str(price),
            "Date": get_timestamp_in_millis(),
        }
    }
    resp = blockchain_request(path, data)

    return resp is not None
