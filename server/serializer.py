from rest_framework import serializers
from .models import *

# class InvoiceForm(serializers.ModelSerializer):
#     class Meta:
#         model = Invoice
#         fields = '__all__'

class InwardDCForm(serializers.ModelSerializer):
    class Meta:
        model = InwDc
        fields = '__all__'

class CustomerMasterForm(serializers.ModelSerializer):
    class Meta:
        model = CustomerMaster
        fields = '__all__'

class PurchaseOrderForm(serializers.ModelSerializer):
    class Meta:
        model = Po
        fields = '__all__'

class PartMasterForm(serializers.ModelSerializer):
    class Meta:
        model = PartMaster
        fields = '__all__'

class MatCompaniesSerialize(serializers.ModelSerializer):
    class Meta:
        model = MatCompanies
        fields = '__all__'
