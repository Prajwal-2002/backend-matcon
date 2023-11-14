import mysql.connector 
import datetime ,sys
from datetime import datetime
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Matcon545@@',
    database='mydatabase'
)
mycursor = mydb.cursor(buffered=True)
def po_sl(mydb, mycursor, elm):
    mycursor.execute("SELECT * FROM inw_dc WHERE po_sl_no= %s", (elm,))
    result = mycursor.fetchone()
    if result==None:
        return False
    else:                        
        return result
            
def inw(mydb, mycursor, grn):
    query = "SELECT grn_no FROM inw_dc WHERE grn_no= %s"
    mycursor.execute(query, (grn,))
    result = mycursor.fetchone()
    if result == None:
        return False
    else:
        return result

print("Enter the Inward delivery number")
grn = input()
po_sl_numbers = []
if inw(mydb, mycursor, grn):
    print(f"'{grn}' exists in the database.")
    ritem=0   
    n = int(input("Enter total number of part items: "))  
    for i in range(n):
        # print("Enter part item sl no: ")
        elm = int(input("Enter part item sl no: "))
        po_sl_numbers.append(elm)

        if po_sl(mydb, mycursor, elm):
            print(f"The part item with '{elm}' exists in the database.")
            
            qty_deli = int(input("Enter the quantity to be delivered: "))
            
            mycursor.execute("SELECT qty_balance FROM inw_dc WHERE grn_no = %s", (grn,))
            bal_qty = mycursor.fetchone()[0]
            
            mycursor.execute("SELECT qty_received FROM inw_dc WHERE grn_no = %s", (grn,))
            qty_reci = mycursor.fetchone()[0]
            
            mycursor.execute("select po_no from inw_dc where grn_no=%s",(grn,))
            po_no=mycursor.fetchone()[0]
          
            mycursor.execute("select qty from po where po_no =%s AND po_sl_no=%s",(po_no,elm))
            qty=mycursor.fetchone()[0]
           
            mycursor.execute("Select qty_sent from po where po_no =%s AND po_sl_no =%s",(po_no,elm,))
            qty_sent= mycursor.fetchone()[0]
            
            mycursor.execute("SELECT rework_dc from inw_dc where grn_no=%s AND po_sl_no =%s",(grn,elm,))
            rework_dc=mycursor.fetchone()[0]
            
            mycursor.execute("SELECT open_po from po where po_no=%s AND po_sl_no =%s",(po_no,elm,))
            open_po=mycursor.fetchone()[0]
            
            mycursor.execute("SELECT open_po_validity from po where po_no=%s AND po_sl_no =%s",(po_no,elm,))
            open_po_date=mycursor.fetchone()[0]
           
            mycursor.execute("select grn_date from inw_dc where grn_no=%s and po_sl_no=%s",(grn,elm,))
            grn_date=mycursor.fetchone()[0]
            
            open_po_date_str = open_po_date.strftime("%Y-%m-%d")
            grn_date_str = grn_date.strftime("%Y-%m-%d")
            
            opn_po_dte = datetime.strptime(open_po_date_str, "%Y-%m-%d")
            grn_dte = datetime.strptime(grn_date_str, "%Y-%m-%d")
            
            if qty_deli <= bal_qty and qty_deli<=qty_reci:
                mycursor.execute("UPDATE inw_dc SET qty_delivered = qty_delivered + %s WHERE grn_no = %s AND po_sl_no = %s", (qty_deli, grn, elm))
                mydb.commit()
            
                mycursor.execute("UPDATE inw_dc SET qty_balance = qty_balance - %s WHERE grn_no= %s AND po_sl_no = %s", (qty_deli, grn, elm))
                mydb.commit()
                
                if rework_dc==True or open_po==True:
                  pass
                else:
                  if qty_sent <= qty:
                   mycursor.execute("UPDATE po SET qty_sent = qty_sent + %s WHERE po_no= %s AND po_sl_no = %s", (qty_deli,po_no, elm))
                   mydb.commit()
                  else:
                   print("Sorry , there is nothing to be delivered ")
                   sys.exit()
                   
                if open_po==True:
                    if grn_dte > opn_po_dte:
                        print("Your open po validity is over")
                        sys.exit()
                        
                mycursor.execute("SELECT qty_balance FROM inw_dc WHERE grn_no = %s AND po_sl_no= %s", (grn,elm))
                bal_qty = mycursor.fetchone()[0]
                print("Remaining quantity is:", bal_qty)
                
                mycursor.execute("SELECT qty_delivered FROM inw_dc WHERE grn_no = %s AND po_sl_no= %s", (grn,elm))
                updated_qty_deli = mycursor.fetchone()[0]
                print("Total number of quantities delivered is:", updated_qty_deli)
         
            else:
                print("Nothing to be delivered")
                sys.exit()
        else:
            print(f"The part item with '{elm}' does not exist in the database.")   
            sys.exit()
    
    
    current=datetime.now()
    print(current,"current value ")
    current_yyyy = current.year
    current_mm =current.month
    mycursor.execute("SELECT fin_yr FROM mat_companies where mat_code='MEE'")
    fin_year= mycursor.fetchone()[0] 
  
    if  fin_year < current_yyyy and current_mm >3:
        fin_year=current_yyyy
        mycursor.execute("UPDATE mat_companies SET fin_yr = %s WHERE mat_code = 'MEE'",(fin_year,))
    f_year=fin_year+1
    fy=str(f_year)
    fyear=fy[2:]
               
    mycursor.execute("SELECT last_gcn_no FROM mat_companies where mat_code='MEE'")
    source_value = mycursor.fetchone()[0]
    print("Source Value:", source_value)
    destination_value = source_value + 1
    print("Destination Value:", destination_value)
    update_query = "UPDATE mat_companies SET last_gcn_no = %s WHERE mat_code = 'MEE'"
    mycursor.execute(update_query, (destination_value,))
    mydb.commit() 
    gcn_num=(str(destination_value) + "/" + str(fin_year)+"-"+str(fyear)).zfill(11) 
   
    current_date =current
    date = str(current_date.strftime('%Y-%m-%d'))    
    mycursor.execute("SELECT grn_no, grn_date, po_no, po_date, receiver_id, consignee_id, po_sl_no, part_id, qty_delivered, uom, unit_price, part_name FROM inw_dc WHERE grn_no=%s AND po_sl_no IN ({})".format(','.join(map(str, po_sl_numbers))), (grn,))
    data_inw = mycursor.fetchall()
    print(type(data_inw))
    print("Data from inw_delivery_challan:", data_inw)
    code='MEE'

    mycursor.execute("SELECT qty_delivered, unit_price FROM inw_dc where grn_no= %s",(grn,))
    rows = mycursor.fetchall()
    print(rows)
    list_tax_amt=[]
    total_taxable_amount = 0
    
    for row in rows:
            qty_delivered, unit_price = row
            taxable_amount = qty_delivered * unit_price
            formatted_number = float('{:.2f}'.format(taxable_amount))
            list_tax_amt.append(formatted_number)
            total_taxable_amount += formatted_number
    print("Total Taxable Amount:", total_taxable_amount)  
       
    insert_data = []
    for idx, row in enumerate(data_inw):
        mycursor.execute("SELECT po_no from inw_dc where grn_no = %s", (grn,))
        x = mycursor.fetchone()
        mycursor.execute("select receiver_id from po where po_no = %s", (x[0],))
        y = mycursor.fetchone()[0]
        mycursor.execute("select cust_st_code from customer_master where cust_id= %s", (y,))
        state_code = mycursor.fetchone()[0]
        if state_code == 29:
            cgst_price = '{:.2f}'.format( 0.09 * list_tax_amt[idx])
            sgst_price = '{:.2f}'.format( 0.09 * list_tax_amt[idx])
            igst_price = 0   
        else:
            cgst_price = 0  
            sgst_price = 0  
            igst_price = '{:.2f}'.format( 0.18 * list_tax_amt[idx])
  
        insert_row = (code, gcn_num,date) + row + (list_tax_amt[idx], cgst_price, sgst_price, igst_price) + (ritem,)
        insert_data.append(insert_row)
    insert_query = """
                INSERT INTO otw_dc 
                (mat_code, gcn_no, gcn_date, grn_no, grn_date, po_no, po_date, receiver_id, consignee_id, po_sl_no, part_id, qty_delivered, uom, unit_price,part_name, taxable_amt, cgst_price, sgst_price, igst_price,rejected_item) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s) 
                """
    mycursor.executemany(insert_query, insert_data)

    mydb.commit()
    mycursor.execute("SELECT * FROM otw_dc WHERE grn_no = %s", (grn,))

    inserted_data = mycursor.fetchall()
    print("outward delivary challan data :")
    for row in inserted_data:
        print(row)
          
else:
    print(f"The record with '{grn}' does not exist in the database.")
    sys.exit()
    
mycursor.close()
mydb.close()