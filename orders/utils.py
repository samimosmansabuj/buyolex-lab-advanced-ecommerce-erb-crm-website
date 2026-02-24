from django.shortcuts import get_object_or_404
from .models import DeliveryOption
import requests


class SteadFastParcelAPI:
    def __init__(self, id):
        self.id = id
    
    def get_steadfast_credentials(self):
        try:
            steadfast = get_object_or_404(DeliveryOption, id=self.id)
            return steadfast
        except DeliveryOption.DoesNotExist:
            return None

    def create_order(self, order_data):
        url = f"{self.get_steadfast_credentials().api_url}/create_order"
        headers = {
            "Content-Type": "application/json",
            "Api-Key": self.get_steadfast_credentials().api_key,
            "Secret-Key": self.get_steadfast_credentials().secret_key
        }
        response = requests.post(url, headers=headers, json=order_data)
        response.raise_for_status()
        return response.json()

    def delivery_status_checking(self, consignment_id):
        steadfast = self.get_steadfast_credentials()
        url = f"{steadfast.api_url}/status_by_cid/{consignment_id}"
        headers = {
            "Content-Type": "application/json",
            "Api-Key": steadfast.api_key,
            "Secret-Key": steadfast.secret_key
        }
        response = requests.get(url=url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
