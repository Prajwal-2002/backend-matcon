from django.db import models
from django import forms
from datetime import date
from django.utils import timezone

class CustomerMaster(models.Model):
    cust_id = models.CharField(primary_key=True, max_length=4)
    cust_name = models.CharField(max_length=50, blank=True, null=True)
    cust_addr1 = models.CharField(max_length=50, blank=True, null=True)
    cust_addr2 = models.CharField(max_length=50, blank=True, null=True)
    cust_city = models.CharField(max_length=15, blank=True, null=True)
    cust_st_code = models.IntegerField(blank=True, null=True)
    cust_st_name = models.CharField(max_length=20, blank=True, null=True)
    cust_pin = models.CharField(max_length=6, blank=True, null=True)
    cust_gst_id = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'customer_master'

class GstRates(models.Model):
    cgst_rate = models.IntegerField(blank=True, null=True)
    sgst_rate = models.IntegerField(blank=True, null=True)
    igst_rate = models.IntegerField(blank=True, null=True)
    id = models.IntegerField(null=False,primary_key=True)

    class Meta:
        managed = True
        db_table = 'gst_rates'


class GstStateCode(models.Model):
    state_code = models.IntegerField(null=False,primary_key=True)
    state_name = models.CharField(max_length=70, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'gst_state_code'

class InwDc(models.Model):
    grn_no = models.CharField(max_length=20)
    grn_date = models.DateField(default=timezone.now)
    rework_dc = models.BooleanField(default=False)
    po_no = models.CharField(max_length=20, blank=False, null=False)
    po_date = models.DateField(default=timezone.now)
    receiver_id = models.CharField(max_length=10, blank=True, null=True)
    consignee_id = models.CharField(max_length=10, blank=True, null=True)
    po_sl_no = models.IntegerField(blank=False, null=False)
    cust_id = models.CharField(max_length=4, blank=True, null=True)
    part_id = models.CharField(max_length=20, blank=True, null=True)
    part_name = models.CharField(max_length=100, blank=True, null=True)
    qty_received = models.IntegerField(blank=True, null=True)
    purpose = models.CharField(max_length=50, blank=True, null=True)
    uom = models.CharField(max_length=10, blank=True, null=True)
    unit_price = models.DecimalField(blank=True, null=True,max_digits=10, decimal_places=2)
    total_price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    qty_delivered = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    qty_balance = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'inw_dc'
        unique_together = (('grn_no', 'po_no', 'po_sl_no'),)


class MatCompanies(models.Model):
    mat_code = models.CharField(max_length=3, null=False,primary_key=True)
    mat_name = models.CharField(max_length=50, blank=True, null=True)
    mat_address = models.CharField(max_length=50, blank=True, null=True)
    mat_gst_code = models.CharField(max_length=20, blank=True, null=True)
    bank_acc_no = models.CharField(max_length=15, blank=True, null=True)
    bank_name = models.CharField(max_length=30, blank=True, null=True)
    bank_address = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    fin_yr = models.CharField(max_length=10, blank=True, null=True)
    last_gcn_no = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'mat_companies'


class OtwDc(models.Model):
    mat_code = models.CharField(max_length=3)
    gcn_no = models.CharField(max_length=15)
    gcn_date = models.DateField(default=timezone.now)
    grn_no = models.CharField(max_length=20,blank=True, null=True)
    grn_date = models.DateField(default=timezone.now)
    po_no = models.CharField(max_length=15)
    po_date = models.DateField(default=timezone.now)
    receiver_id = models.CharField(max_length=4, blank=True, null=True)
    consignee_id = models.CharField(max_length=4, blank=True, null=True)
    po_sl_no = models.IntegerField()
    part_id = models.CharField(max_length=15,blank=True, null=True)
    part_name = models.CharField(max_length=50, blank=True, null=True)
    qty_delivered = models.IntegerField(blank=True, null=True)
    uom = models.CharField(max_length=5, blank=True, null=True)
    unit_price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    taxable_amt = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    cgst_price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    sgst_price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    igst_price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    rejected_item = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'otw_dc'
        unique_together = (('mat_code', 'gcn_no', 'po_no', 'po_sl_no'),)


class PartMaster(models.Model):
    id = models.AutoField(primary_key=True)
    part_id = models.CharField(max_length=20)
    part_name = models.CharField(max_length=50, blank=True, null=True)
    cust_id = models.ForeignKey(CustomerMaster, on_delete=models.CASCADE, db_column='cust_id', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'part_master'
        unique_together = (('part_id', 'cust_id'), )


class Po(models.Model):
    id = models.AutoField(primary_key=True)
    po_no = models.CharField(max_length=20, blank=False, null=False)
    po_date = models.DateField(default=timezone.now)
    open_po = models.BooleanField(default=False)
    open_po_validity = models.DateField(null=True, blank=True,)
    cust_id = models.ForeignKey(CustomerMaster, on_delete=models.CASCADE, blank=True, null=True)
    quote_ref_no = models.CharField(max_length=5, blank=True, null=True)
    receiver_id = models.CharField(max_length=4, blank=True, null=True)
    consignee_id = models.CharField(max_length=4, blank=True, null=True)
    po_sl_no = models.IntegerField()
    part_id = models.CharField(max_length=20, blank=True, null=True)
    qty = models.IntegerField(blank=True, null=True)
    qty_sent = models.IntegerField(blank=True, null=True)
    uom = models.CharField(max_length=5, blank=True, null=True)
    unit_price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    total_price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'po'
        unique_together = ('po_no', 'po_sl_no')


# class Invoice(models.Model):
#     mcc = forms.CharField(label='MCC', max_length=20)
#     grn_no = forms.CharField(label='GRN NO', max_length=20)
#     # po_no = forms.CharField(label='PO NO', max_length=20)
#     po_sl_no = forms.IntegerField(label='PO SERIAL NO')
#     qty_received = forms.IntegerField(label='QUANTITY RECEIVED')

# [('35', 'Andaman and Nicobar Islands'),
# ('28', 'Andhra Pradesh'),
# ('12', 'Arunachal Pradesh'),
# ('18', 'Assam'),
# ('10', 'Bihar'),
# ('4', 'Chandigarh'),
# ('22', 'Chhattisgarh'),
# ('26', 'Dadra and Nagar Haveli and Daman and Diu'),
# ('7', 'Delhi'),
# ('30', 'Goa'),
# ('24', 'Gujarat'),
# ('6', 'Haryana'),
# ('2', 'Himachal Pradesh'),
# ('1', 'Jammu and Kashmir'),
# ('20', 'Jharkhand'),
# ('29', 'Karnataka'),
# ('32', 'Kerala'),
# ('37', 'Ladakh'),
# ('31', 'Lakshadweep'),
# ('23', 'Madhya Pradesh'),
# ('27', 'Maharashtra'),
# ('14', 'Manipur'),
# ('17', 'Meghalaya'),
# ('15', 'Mizoram'),
# ('13', 'Nagaland'),
# ('21', 'Odisha'),
# ('34', 'Puducherry'),
# ('3', 'Punjab'),
# ('8', 'Rajasthan'),
# ('11', 'Sikkim'),
# ('33', 'Tamil Nadu'),
# ('36', 'Telangana'),
# ('16', 'Tripura'),
# ('9', 'Uttar Pradesh'),
# ('5', 'Uttarakhand'),
# ('19', 'West Bengal')]