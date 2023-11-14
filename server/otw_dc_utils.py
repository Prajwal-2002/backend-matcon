import mysql.connector 
import datetime
import sqlite3

connection = sqlite3.connect('d')

print("Enter the Inward delivery number")
grn = input()

def inw(mydb, mycursor, grn):
    query = "SELECT grn_no FROM inw_dc WHERE grn_no= %s"
    mycursor.execute(query, (grn,))
    result = mycursor.fetchone()
    return result is not None 

if inw(mydb, mycursor, grn):
    print(f"'{grn}' exists in the database.")
    
    # n = int(input("Enter total number of part items: "))  
    n = 1
    po_sl_numbers = []
    for i in range(n):
        print("Enter part item sl no: ")
        elm = int(input())
        po_sl_numbers.append(elm)
        
        def po_sl(mydb, mycursor, elm):
           mycursor.execute("SELECT po_sl_no FROM inw_dc WHERE po_sl_no= %s", (elm,))
           result = mycursor.fetchone()[0]
           return result is not None
        
        if po_sl(mydb, mycursor, elm):
            print(f"The part item with '{elm}' exists in the database.")
            qty_deli = int(input("Enter the quantity to be delivered: "))
            
            mycursor.execute("UPDATE inw_dc SET qty_delivered = qty_delivered + %s WHERE grn_no = %s AND po_sl_no = %s", (qty_deli, grn, elm))
            mydb.commit()
            
            mycursor.execute("SELECT qty_balance FROM inw_dc WHERE grn_no = %s", (grn,))
            bal_qty = mycursor.fetchone()[0]
            
            if qty_deli <= bal_qty:
                mycursor.execute("UPDATE inw_dc SET qty_balance = qty_balance - %s WHERE grn_no= %s AND po_sl_no = %s", (qty_deli, grn, elm))
                mydb.commit()
                
                mycursor.execute("SELECT qty_balance FROM inw_dc WHERE grn_no = %s AND po_sl_no= %s", (grn,elm))
                bal_qty = mycursor.fetchone()[0]
                print("Remaining quantity is:", bal_qty)
                
                mycursor.execute("SELECT qty_delivered FROM inw_dc WHERE grn_no = %s AND po_sl_no= %s", (grn,elm))
                updated_qty_deli = mycursor.fetchone()[0]
                print("Total number of quantities delivered is:", updated_qty_deli)
            else:
                print("Nothing to be delivered")
        else:
            print(f"The part item with '{elm}' does not exist in the database.")
else:
    print(f"The record with '{grn}' does not exist in the database.")


#cursor execution
mycursor.execute("SELECT last_gcn_no FROM mat_companies where mat_code='MEE'")
source_value = mycursor.fetchone()[0]
print("Source Value:", source_value)
destination_value = source_value + 1
print("Destination Value:", destination_value)

update_query = "UPDATE mat_companies SET last_gcn_no = %s WHERE mat_code = 'MEE'"
mycursor.execute(update_query, (destination_value,))
mydb.commit()

current_date = (datetime.date.today())
date = str(current_date.strftime('%d-%m-%Y'))

mycursor.execute("SELECT grn_no, fin_year, grn_date, po_no, po_date, receiver_id, consignee_id, po_sl_no, part_id, qty_delivered, uom, unit_price, part_name FROM inw_dc WHERE grn_no=%s AND po_sl_no IN ({})".format(','.join(map(str, po_sl_numbers))), (grn,))
# mycursor.execute("SELECT grn_no, fin_year ,grn_date, po_no, po_date, receiver_id, consignee_id, po_sl_no, part_id, qty_delivered, uom, unit_price,part_name FROM inw_dc where grn_no=%s AND po_sl_no =IN %s", (grn, tuple(elm)))
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
    # print(taxable_amount)
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
    
    print(state_code)
    
 
    if state_code == 29:
        cgst_price = '{:.2f}'.format( 0.09 * list_tax_amt[idx])
        sgst_price = '{:.2f}'.format( 0.09 * list_tax_amt[idx])
        igst_price = 0  # No IGST in this case
        
    else:
        cgst_price = 0  # No CGST in this case
        sgst_price = 0  # No SGST in this case
        igst_price = '{:.2f}'.format( 0.18 * list_tax_amt[idx])

    # Insert the row with CGST, SGST, and IGST prices
    insert_row = (code, destination_value,date ) + row + (list_tax_amt[idx], cgst_price, sgst_price, igst_price)
    insert_data.append(insert_row)
    
insert_query = """
    INSERT INTO otw_dc 
    (mat_code, gcn_no, gcn_date, grn_no, fin_year, grn_date, po_no, po_date, receiver_id, consignee_id, po_sl_no, part_id, qty_delivered, uom, unit_price,part_name, taxable_amt, cgst_price, sgst_price, igst_price) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s) 
"""
mycursor.executemany(insert_query, insert_data)

mydb.commit()
mycursor.execute("SELECT * FROM otw_dc WHERE grn_no = %s", (grn,))

inserted_data = mycursor.fetchall()
print("outward delivary challan data :")
for row in inserted_data:
    print(row)
    
mycursor.close()
mydb.close()