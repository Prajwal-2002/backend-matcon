from django.shortcuts import render,HttpResponse
from rest_framework import status
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.db.models import Sum
from .models import *
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.parsers import JSONParser
from django.shortcuts import render 
from rest_framework.views import APIView 
from . models import *
from rest_framework.response import Response 
from . serializer import *
import datetime as d
from datetime import datetime
#pip3 install Babel
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate, login,logout
import json

from babel.numbers import format_currency

def report(request):
    return render(request,'reports.html')



@login_required(login_url='login')
def HomePage(req):
    return render(req,'home.html')


class SignUpPage(APIView):
    def post(self,req):
        data = req.data
        print(data)
        uname = data['uname']
        pass1 = data['pass1']
        pass2 = data['pass2']

        if pass1 != pass2:
            return Response(status=status.HTTP_400_BAD_REQUEST,data ={'pw': pass1})
        else :
            try:
                user = User.objects.get(username=uname)
                return Response(status=status.HTTP_400_BAD_REQUEST, data = {'username' : data['uname']})
            except:
                my_user = User.objects.create_user(username= uname)
                my_user.set_password(pass1)
                my_user.save()
          
        
        return Response(status=status.HTTP_202_ACCEPTED)

class LoginPage(APIView):
    def post(self,req):
        data = req.data
        print(data)
        username = data['uname']
        password = data['password']
        user = authenticate(username=username,password =password)
        print(user)
        if user is not None:
            login(req,user)
            return Response(status=status.HTTP_200_OK,data='successful')
            # return redirect('home')
        else:
            return Response(status = status.HTTP_200_OK,data = 'incorrect')
       

class LogoutPage(APIView):
    def post(self,req):
        logout(req)
        return Response(status = status.HTTP_200_OK,data = 'out')


class InvoicePrint(APIView):
    def get(self, request):
        print("get request recevied")
        try:
            data = invoice_print(request)
            # print(data, 'data before sending to frontend')
            if data == 'invalid otw_dc_no':
                return HttpResponse('Invalid otw_dc')
            return render(request, 'tax_invoice.html', data)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

class DCPrint(APIView):
    def get(self, request):
        try:
            data = dc_print(request)
            if data == 'invalid otw_dc_no':
                return HttpResponse('Invalid otw_dc')
            return render(request, 'dc.html', data)
            # return Response(data=data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    
def convert_rupees_to_words(amount):
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", 
            "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen","Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    thousands = ["", "Thousand", "Lakh", "Crore"]
    def convert_two_digits(num):
        if num < 20:
            return ones[num] + " "
        else:
            return tens[num // 10] + " " + ones[num % 10]
    def convert_three_digits(num):
        if num < 100:
            return convert_two_digits(num)
        else:
            return ones[num // 100] + " Hundred " + convert_two_digits(num % 100)
    result = ""    
    amount = format(amount, ".2f")
    # print(type(amount))   
    RsPs = str(amount).split('.')
    Rs = int(RsPs[0])
    Ps = int(RsPs[1])
    if Rs == 0:
        result += "Zero "
    else:
        for i in range(4):
            if i == 0 or i == 3:
                chunk = Rs % 1000
                Rs //= 1000
            else:
                chunk = Rs % 100
                Rs //= 100
            if chunk != 0:
                result = convert_three_digits(chunk) + " " + thousands[i] + " " +result
    if Ps > 0:
        result = result.strip() + " and Paise " + convert_two_digits(Ps)        
    result = "Rupees " + result.strip() + " Only"
    # print("conversion success")
    return result.upper()

class InvoiceProcessing(APIView):    
    # serializer_class = InvoiceForm  
    def post(self, request):
        try:
            response = invoice_processing(request)
            if(response == 'Nothing to be delivered'):
                return Response(status=status.HTTP_200_OK, data = 'zero items')
            elif response == 'grn_no does not exists':
                return Response(status=status.HTTP_200_OK, data = 'grn_no')
            elif response[0:8] == 'po_sl_no':
                return Response(status=status.HTTP_200_OK,data = response)
            elif response == 'open_po_validity':
                return Response(status=status.HTTP_200_OK,data = 'open_po')
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)



class InwardDcInput(APIView): 
    def post(self, request):
        request.data['qty_delivered'] = 0
        request.data['qty_balance'] = request.data['qty_received']
        serializer = InwardDCForm(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # print('saved to database')
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerMasterInput(APIView):
    def post(self, request):
        serializer = CustomerMasterForm(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PartMasterInput(APIView):
    def post(self, request):
        serializer = PartMasterForm(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PurchaseOrderInput(APIView):
    def post(self, request):
        request.data['qty_sent'] = 0
        serializer = PurchaseOrderForm(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def invoice_processing(request):
    grn_no = request.data['grn_no']
    mat_code = request.data['mcc']
    query_set = InwDc.objects.filter(grn_no=grn_no)
    print(len(query_set))

    if request.data['rejected'] == 1:
        ritem = 1
    else:
        ritem = 0 

    try:
        if query_set.exists():
            query = query_set[0]
            po_sl_numbers = []
            for i in range(int(request.data['items'])):
                item = 'item'+str(i)
                po_sl_no = int(request.data[item]['po_sl_no'])
                qty_to_be_delivered = int(request.data[item]['qty_delivered'])
                po_sl_numbers.append(po_sl_no)

                try :
                    po_sl_no = get_object_or_404(InwDc, grn_no=grn_no, po_sl_no=po_sl_no).po_sl_no
                
                    balance_qty = query.qty_balance
                    qty_received = query.qty_received
                    po_no = query.po_no
                    qty = get_object_or_404(Po, po_no=po_no, po_sl_no=po_sl_no).qty
                    qty_sent = get_object_or_404(Po, po_no=po_no, po_sl_no=po_sl_no).qty_sent
                    rework_dc = query.rework_dc
                    grn_date = query.grn_date
                    open_po = get_object_or_404(Po, po_no=po_no, po_sl_no=po_sl_no).open_po
                    open_po_validity = get_object_or_404(Po, po_no=po_no, po_sl_no=po_sl_no).open_po_validity

                    if qty_to_be_delivered <= balance_qty and qty_to_be_delivered<=qty_received:
                        InwDc.objects.filter(grn_no=grn_no, po_sl_no=po_sl_no).update(qty_delivered=models.F('qty_delivered') + qty_to_be_delivered)

                        InwDc.objects.filter(grn_no=grn_no, po_sl_no=po_sl_no).update(qty_balance=models.F('qty_balance') - qty_to_be_delivered)

                        print('open_po',open_po)
                        if rework_dc==True or open_po==True:
                            print('pass')
                            pass
                        else:
                            if qty_sent <= qty:
                                Po.objects.filter(po_no=po_no, po_sl_no=po_sl_no).update(qty_sent=models.F('qty_sent') + qty_to_be_delivered)
                            else:
                                print("Sorry , there is nothing to be delivered ")
                                sys.exit()
                        
                        # if open_po==True:
                        #     # open_po_date_str = open_po_validty.strftime("%Y-%m-%d")
                        #     # grn_date_str = grn_date.strftime("%Y-%m-%d")                        
                        #     # opn_po_dte = datetime.strptime(open_po_date_str, "%Y-%m-%d")
                        #     # grn_dte = datetime.strptime(grn_date_str, "%Y-%m-%d")
                        #     print(grn_date,open_po_validity)

                        #     if grn_date > open_po_validity:
                        #         return 'open_po_validity'

                        balance_qty = get_object_or_404(InwDc, grn_no=grn_no, po_sl_no=po_sl_no).qty_balance
                        updated_qty_delivered = get_object_or_404(InwDc, grn_no=grn_no, po_sl_no=po_sl_no).qty_delivered
                        print("Remaining qty : \n", balance_qty)
                        print("Updated delivered qtuantities : \n", updated_qty_delivered)

                    else:
                        return "Nothing to be delivered"
                
                except Exception as e:
                    print('type' ,e)
                    print(f"The part item with '{po_sl_no}' does not exist in the database.") 
                    return "po_sl_no" + str(po_sl_no)
            
            current= d.datetime.now()
            print(current,"current value ")
            current_yyyy = current.year
            current_mm = current.month
            fin_year = int(get_object_or_404(MatCompanies, mat_code=mat_code).fin_yr)
            print(type(fin_year))

            if  fin_year < current_yyyy and current_mm >3:
                fin_year=current_yyyy
                MatCompanies.objects.filter(mat_code=mat_code).update(fin_yr=fin_year)
            f_year=fin_year+1
            fy=str(f_year)
            fyear=fy[2:]

            gcn_no = get_object_or_404(MatCompanies,mat_code='MEE').last_gcn_no
            print("Source Value:", gcn_no)
            destination_value = gcn_no + 1
            print("Destination Value:", destination_value)
            MatCompanies.objects.filter(mat_code='MEE').update(last_gcn_no = destination_value)
            if rework_dc==True:
                flag='R'
            else:
                flag=''    
            gcn_num=(str(destination_value).zfill(3)  + flag+ "/" + str(fin_year)+"-"+str(fyear))
            source_value = get_object_or_404(MatCompanies, mat_code=mat_code).last_gcn_no
            destination_value = source_value + 1

            MatCompanies.objects.filter(mat_code=mat_code).update(last_gcn_no=destination_value)

            gcn_num=(str(destination_value) + "/" + str(fin_year)+"-"+str(fyear)).zfill(11)

            current_date = current
            date = str(current_date.strftime('%Y-%m-%d'))
            
            data_inw = InwDc.objects.filter(grn_no=grn_no, po_sl_no__in=po_sl_numbers).values('grn_no', 'grn_date', 'po_no', 'po_date', 'receiver_id', 'consignee_id', 'po_sl_no', 'part_id', 'qty_delivered', 'uom', 'unit_price', 'part_name') 
            code='MEE'
            
            rows = InwDc.objects.filter(grn_no=grn_no).values('qty_delivered', 'unit_price')
            list_tax_amt=[]
            total_taxable_amount = 0
            
            for row in rows:
                qty_delivered, unit_price = row['qty_delivered'], row['unit_price']
                taxable_amount = qty_delivered * unit_price
                formatted_number = float('{:.2f}'.format(taxable_amount))

                list_tax_amt.append(formatted_number)
                # print(taxable_amount)
                total_taxable_amount += formatted_number
            print("Total Taxable Amount:", total_taxable_amount)  
            
            
            insert_data = []
            for idx, row in enumerate(data_inw):
                x=po_no
                print(x)
                receiver_id = Po.objects.filter(po_no=x).values_list('receiver_id', flat=True).first()
                state_code = CustomerMaster.objects.filter(cust_id=receiver_id).values_list('cust_st_code', flat=True).first()
                print(state_code)

                if ritem == 1:
                    amt = 0
                else:
                    amt = list_tax_amt[idx]

                if state_code == 29:
                    cgst_price = '{:.2f}'.format( 0.09 * amt)
                    sgst_price = '{:.2f}'.format( 0.09 * amt)
                    igst_price = 0   
                else:
                    cgst_price = 0  
                    sgst_price = 0  
                    igst_price = '{:.2f}'.format( 0.18 * amt)
                    
                    insert_instance = OtwDc(
                    mat_code=code,
                    gcn_no=gcn_num,
                    gcn_date=date,
                    grn_no=row['grn_no'],
                    grn_date=row['grn_date'],
                    po_no=row['po_no'],
                    po_date=row['po_date'],
                    receiver_id=receiver_id,
                    consignee_id=row['consignee_id'],
                    po_sl_no=row['po_sl_no'],
                    part_id=row['part_id'],
                    qty_delivered=row['qty_delivered'],
                    uom=row['uom'],
                    unit_price=row['unit_price'],
                    part_name=row['part_name'],
                    taxable_amt=amt,
                    cgst_price=cgst_price,
                    sgst_price=sgst_price,
                    igst_price=igst_price,
                    rejected_item=ritem
                    )

                    insert_data.append(insert_instance) 
                    
                OtwDc.objects.bulk_create(insert_data) 
                return('success')   
        else:
            print(f"The record with '{grn_no}' does not exist in the database.")
            return('grn_no does not exists')
            
    except Exception as e:
        print(e)

def invoice_print(request):
    try:
        gcn_no = request.query_params.get('data[gcn_no]')
        print(gcn_no)
        odc = OtwDc.objects.filter(gcn_no=gcn_no)
        odc1 = get_object_or_404(OtwDc,po_sl_no='1',gcn_no=gcn_no)    
        mat = odc1.mat_code
        m = MatCompanies.objects.get(mat_code=mat)
        r_id = odc1.receiver_id
        r = CustomerMaster.objects.get(cust_id=r_id)
        c_id = odc1.consignee_id
        c = CustomerMaster.objects.get(cust_id=c_id)
        gr = get_object_or_404(GstRates,id=1)
        total_qty = OtwDc.objects.filter(gcn_no=gcn_no).aggregate(total_qty=Sum('qty_delivered'))['total_qty']
        total_taxable_value =OtwDc.objects.filter(gcn_no=gcn_no).aggregate(total_taxable_value=Sum('taxable_amt'))['total_taxable_value']
        total_cgst = OtwDc.objects.filter(gcn_no=gcn_no).aggregate(total_cgst=Sum('cgst_price'))['total_cgst']
        total_sgst = OtwDc.objects.filter(gcn_no=gcn_no).aggregate(total_sgst=Sum('sgst_price'))['total_sgst']
        total_igst = OtwDc.objects.filter(gcn_no=gcn_no).aggregate(total_igst=Sum('igst_price'))['total_igst']
        grand_total= round(float('{:.2f}'.format(total_taxable_value+total_cgst+total_sgst+total_igst)))
        gt=format_currency(grand_total, 'INR', locale='en_IN')
        aw = convert_rupees_to_words(grand_total) 
        context = {
            'odc': odc,
            'm': m,
            'r': r,
            'c': c,
            'gr': gr,
            'odc1': odc1,
            'amount' : aw,
            'total_taxable_value':"{:.2f}".format(total_taxable_value),
            'total_cgst':"{:.2f}".format(total_cgst),
            'total_sgst':"{:.2f}".format(total_sgst),
            'total_igst':"{:.2f}".format(total_igst),
            'gt':gt,
            'total_qty':total_qty,  
        }
        return context
    except Exception as e:
        print(e)
        return "invalid otw_dc_no"


def dc_print(request):
    try:
        gcn_no=request.query_params.get('data[gcn_no]')
        odc=OtwDc.objects.filter(gcn_no=gcn_no)
        odc1=OtwDc.objects.filter(gcn_no=gcn_no)[0]
        c_id=odc1.consignee_id
        c=CustomerMaster.objects.get(cust_id=c_id)
        r_id = odc1.receiver_id
        r = CustomerMaster.objects.get(cust_id=r_id)
        mat= odc1.mat_code
        m=MatCompanies.objects.get(mat_code=mat)
        context = {
            'm':m,
            'c':c,
            'r':r,
            'odc1':odc1,
            'odc':odc,
        
        }
        return context
    
    except Exception as e:
        print(e)
        return "invalid otw_dc_no"





