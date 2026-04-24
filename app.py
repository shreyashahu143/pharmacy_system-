import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import date
from psycopg2.extras import RealDictCursor # Used to fetch results as dictionaries

# --- Database Configuration ---
# (Use your Neon connection details)
DB_CONFIG = {
    "dbname": "neondb",
    "user": "neondb_owner",
    "password": "npg_Q3GNJqztUre2",
    "host": "ep-floral-forest-a1al52or-pooler.ap-southeast-1.aws.neon.tech",
    "port": "5432",
    "sslmode": "require"
}

app = Flask(__name__)
CORS(app) 

def get_db_connection():
    """Establishes a new database connection."""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# --- ENDPOINT 1 (Heavily Updated for your Schema) ---
@app.route('/api/sales', methods=['POST'])
def create_sales_bill():
    """
    Receives a sales bill JSON and inserts data into your 4 tables
    (Customer, Sales, Sales_item, Invoice) using your ER diagram.
    """
    data = request.get_json()
    
    # Extract data from the frontend JSON
    header = data['billHeader']
    items = data['billItems']
    summary = data['billSummary']
    payment = data['billPayment']
    
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # --- 1. Handle Customer & Customer_type ---
        
        # a. Get the Customer_type_id (Foreign Key)
        cursor.execute(
            "SELECT type_id FROM customer_type WHERE type_name = %s",
            (header['customer_type'],)
        )
        customer_type_result = cursor.fetchone()
        if not customer_type_result:
            raise Exception(f"Customer type '{header['customer_type']}' not found in database.")
        customer_type_id = customer_type_result[0]
        
        # b. Get or Create the Customer
        cursor.execute(
            "SELECT customer_id FROM Customer WHERE phone_number = %s",
            (header['phone_number'],)
        )
        customer_result = cursor.fetchone()
        
        if customer_result:
            customer_id = customer_result[0]
        else:
            # Create new customer
            customer_sql = """
                INSERT INTO customer (customer_name, address, phone_number, type_id,invoice_number)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING customer_id; 
            """
            cursor.execute(customer_sql, (
                header['customer_name'],
                header.get('address'),
                header['phone_number'],
                customer_type_id  ,# Use the FK we found
                header['bill_number']
            ))
            customer_id = cursor.fetchone()[0]

        # --- 2. Handle Sales & Payment_mode ---
        
        # a. Get the Payment_mode_id (Foreign Key)
        cursor.execute(
            "SELECT mode_id FROM payment_mode WHERE mode_name = %s",
            (payment['payment_mode'],)
        )
        mode_result = cursor.fetchone()
        if not mode_result:
            raise Exception(f"Payment mode '{payment['payment_mode']}' not found in database.")
        mode_id = mode_result[0]
        
        # b. Create the Sales record
        # (Assuming you have a 'BillNumber' column in 'Sales' as per your text)
        sales_sql = """
            INSERT INTO sales (sales_date, customer_id, doctor_name, mode_id)
            VALUES (%s, %s, %s, %s)
            RETURNING sales_id;
        """
        cursor.execute(sales_sql, (

            header['sales_date'],
            customer_id,
            header.get('doctor_name'),
            mode_id
        ))
        sales_id = cursor.fetchone()[0]

        # --- 3. Handle Sales_item (Loop) ---
        item_sql = """
            INSERT INTO sale_item (sales_id, product_id, quantity_of_order, discount)
            VALUES (%s, %s, %s, %s);
        """
        
        for item in items:
            # a. Get the Product_id (Foreign Key) for each item
            cursor.execute(
                "SELECT product_id FROM product WHERE product_name = %s",
                (item['medicine_name'],)
            )
            product_result = cursor.fetchone()
            if not product_result:
                raise Exception(f"Product '{item['medicine_name']}' not found in database.")
            product_id = product_result[0]

            # b. Insert the item into Sales_item
            cursor.execute(item_sql, (
                sales_id,
                product_id, # Use the FK we found
                item['quantity'],
                item.get('item_discount', 0)
            ))
            
            # c. (IMPORTANT) Update stock in your 'In_stock' table
            stock_update_sql = """
                UPDATE in_stock 
                SET quantity_of_units = quantity_of_units - %s 
                WHERE product_id = %s
            """
            cursor.execute(stock_update_sql, (item['quantity'], product_id))

        # --- 4. Handle Invoice & Payment_status ---
        
        # a. Determine Payment_status_id (Foreign Key)
        balance = payment['balance_amount']
        # (Assuming status names are 'Paid' and 'Pending' in your Payment_status table)
        status_name = 'Paid' if balance == 0 else 'Balance' 
        
        cursor.execute(
            "SELECT status_id FROM payment_status WHERE status_name = %s",
            (status_name,)
        )
        status_result = cursor.fetchone()
        if not status_result:
            raise Exception(f"Payment status '{status_name}' not found in database.")
        status_id = status_result[0]

        # b. Create the Invoice record
        # (Using your text mapping for columns)
        invoice_sql = """
            INSERT INTO in_voice (sales_id, total_amount, amount_paid, balance_amount, invoice_date, due_date, status_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(invoice_sql, (
            sales_id,
            summary['total_amount'],
            payment['amount_paid'],
            payment['balance_amount'],
            header['sales_date'], # Use sales date as invoice date
            payment.get('balance_due_date'),
            status_id # Use the FK we found
        ))

        # --- 5. Commit Transaction ---
        conn.commit()
        
        return jsonify({
            "success": True, 
            "message": "Sales bill created successfully",
            "sales_id": sales_id,
            "bill_number": header['bill_number']
        }), 201

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if conn:
            conn.rollback() # Rollback all changes if any step failed
        return jsonify({"success": False, "message": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- ENDPOINT 2 (Updated for your Schema) ---
@app.route('/api/medicines', methods=['GET'])
def get_medicines():
    """ Fetches medicine details from Product and In_stock tables """
    conn = None
    try:
        conn = get_db_connection()
        # Use RealDictCursor to get results as dictionaries
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # (Adjust this query as needed)
        query = """
            SELECT 
                p.product_name AS "name",
                p.category_id, 
                i.batch_no AS "batchNo",
                i.exp_date AS "expiryDate",
                p.base_price AS "price",
                i.quantity_of_units AS "stock"
            FROM product p
            JOIN in_stock i ON p.product_id = i.product_id
            WHERE i.quantity_of_units > 0 AND i.exp_date > CURRENT_DATE;
        """
        cursor.execute(query)
        medicines = cursor.fetchall()
        
        # Convert date objects to strings
        for med in medicines:
            med['expiryDate'] = med['expiryDate'].strftime('%Y-%m-%d')
            # (You might need another join to get category *name* from *Category_id*)
            # For now, I'll just add a placeholder category
            med['category'] = "Medicine" 

        return jsonify(medicines), 200

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- ENDPOINT 3 (Updated for your Schema) ---
# --- ENDPOINT 3 (Updated for your Schema) ---
# --- ENDPOINT 3 (This is the corrected version) ---
@app.route('/api/sales/today', methods=['GET'])
def get_today_sales():
    """ Fetches and assembles all bill data for today """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        today_str = date.today().isoformat()
        
        # 1. Fetch all sales for today.
        # This query joins all the "header" info for every sale today.
        header_sql = """
            SELECT 
                s.sales_id, s.sales_date, s.doctor_name,
                c.customer_name, c.address, c.phone_number, c.invoice_number,
                ct.type_name AS customer_type,
                pm.mode_name AS payment_mode,
                i.total_amount, i.amount_paid, i.balance_amount, i.due_date,
                ps.status_name AS payment_status
            FROM sales s
            JOIN customer c ON s.customer_id = c.customer_id
            JOIN customer_type ct ON c.type_id = ct.type_id
            JOIN in_voice i ON s.sales_id = i.sales_id
            JOIN payment_mode pm ON s.mode_id = pm.mode_id
            JOIN payment_status ps ON i.status_id = ps.status_id
            WHERE s.sales_date = %s;
        """
        cursor.execute(header_sql, (today_str,))
        sales_headers = cursor.fetchall()
        
        if not sales_headers:
            return jsonify([]), 200 # Return empty list if no sales

        # Get all sales IDs to fetch items in one go
        sales_ids = [h['sales_id'] for h in sales_headers]

        # 2. Fetch ALL items for those sales in a single query
        # --- (THIS IS THE FIX, based on your error message) ---
        items_sql = """
            SELECT 
                si.sales_id,  -- <-- FIXED (was sale_id)
                p.product_name AS "medicine_name",
                si.quantity_of_order AS "quantity",
                p.base_price AS "unit_price",
                si.discount AS "item_discount"
            FROM sale_item si
            JOIN product p ON si.product_id = p.product_id
            WHERE si.sales_id = ANY(%s);  -- <-- FIXED (was sale_id)
        """
        cursor.execute(items_sql, (sales_ids,))
        all_items = cursor.fetchall()
        
        # 3. In Python, assemble the nested JSON
        all_bills = []
        for header in sales_headers:
            sales_id = header['sales_id']
            
            # Find all items for this specific header
            bill_items_list = []
            for item in all_items:
                if item['sales_id'] == sales_id: # if item's FK matches
                    item_total = (float(item['quantity']) * float(item['unit_price'])) - float(item['item_discount'])
                    bill_items_list.append({
                        "bill_number": header['invoice_number'],
                        "medicine_name": item['medicine_name'],
                        "category": "N/A", 
                        "batch_no": "N/A", 
                        "expiry_date": "N/A",
                        "quantity": float(item['quantity']),
                        "unit_price": float(item['unit_price']),
                        "item_discount": float(item['item_discount']),
                        "item_total": item_total
                    })
            
            # Calculate total_quantity and sub_total for this bill
            total_qty = sum(i['quantity'] for i in bill_items_list)
            sub_total = sum(i['item_total'] for i in bill_items_list)
            overall_discount = sub_total - float(header['total_amount'])

            # Build the final JSON for this one bill
            bill_json = {
                "billHeader": {
                    "bill_number": header['invoice_number'], # Use the human-readable bill number
                    "sales_date": header['sales_date'].strftime('%Y-%m-%d'),
                    "customer_name": header['customer_name'],
                    "customer_type": header['customer_type'],
                    "address": header['address'],
                    "phone_number": header['phone_number'],
                    "doctor_name": header['doctor_name']
                },
                "billItems": bill_items_list,
                "billSummary": {
                    "bill_number": header['invoice_number'],
                    "total_quantity": total_qty,
                    "sub_total": sub_total,
                    "overall_discount": overall_discount,
                    "total_amount": float(header['total_amount'])
                },
                "billPayment": {
                    "bill_number": header['invoice_number'],
                    "payment_mode": header['payment_mode'],
                    "amount_paid": float(header['amount_paid']),
                    "balance_amount": float(header['balance_amount']),
                    "balance_due_date": header['due_date'].strftime('%Y-%m-%d') if header['due_date'] else None,
                    "payment_status": header['payment_status']
                }
            }
            all_bills.append(bill_json)
            
        return jsonify(all_bills), 200

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()
# --- (Your existing /api/sales, /api/medicines, /api/sales/today routes) ---

# --- NEW ENDPOINT FOR PRODUCT PAGE: GET ALL CATEGORIES ---
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Fetches all product categories from the database."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT category_name FROM product_category ORDER BY category_name")
        categories = cursor.fetchall()
        return jsonify(categories), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# --- NEW ENDPOINT FOR PRODUCT PAGE: GET ALL PRODUCTS ---
@app.route('/api/products', methods=['GET'])
def get_products():
    """Fetches all products for the master list, joining with category."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # (This query assumes your ERD is correct)
        query = """
            SELECT 
                p.product_id,
                p.product_name,
                c.category_name,
                p.description,
                p.base_price AS base_price,
                p.gst,
                p.reorder_level,
                p.mfg_name AS manufacturer
            FROM product p
            LEFT JOIN product_category c ON p.category_id = c.category_id
            ORDER BY p.product_name;
        """
        cursor.execute(query)
        products = cursor.fetchall()
        return jsonify(products), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# --- NEW ENDPOINT FOR PRODUCT PAGE: CREATE A NEW PRODUCT ---
@app.route('/api/products', methods=['POST'])
def create_product():
    """Creates a new product in the database."""
    data = request.get_json()
    conn = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # --- 1. Get or Create Category ID (Foreign Key) ---
        cursor.execute("SELECT category_id FROM product_category WHERE category_name = %s", (data['category'],))
        category_result = cursor.fetchone()
        if category_result:
            category_id = category_result[0]
        else:
            cursor.execute("INSERT INTO product_category (category_name) VALUES (%s) RETURNING category_id", (data['category'],))
            category_id = cursor.fetchone()[0]

        # --- 3. Insert the New Product ---
        # (Using column names from your ER diagram)
        sql = """
            INSERT INTO product (
                 product_name, category_id, description,base_price, gst, reorder_level, mfg_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(sql, (
            data['productName'],
            category_id,
            data['description'],
            data['basePrice'],
            data['gst'],
            data['reorderLevel'],
            data['manufacturer']
        ))
        
        conn.commit()
        return jsonify({"success": True, "message": f"Product {data['productName']} saved."}), 201

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if conn:
            conn.rollback()
        # Handle "product_id already exists" error gracefully
        if "duplicate key" in str(error):
             return jsonify({"success": False, "message": f"Error: Item ID '{data['itemId']}' already exists."}), 400
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()
# --- NEW ENDPOINT FOR CATEGORY MODAL ---
@app.route('/api/categories', methods=['POST'])
def create_category():
    """Creates a new product category."""
    data = request.get_json()
    category_name = data.get('category_name')

    if not category_name:
        return jsonify({"success": False, "message": "Category name is required"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # (Column name from ERD)
        cursor.execute(
            "INSERT INTO product_category (category_name) VALUES (%s)",
            (category_name,)
        )
        conn.commit()
        
        return jsonify({"success": True, "message": f"Category '{category_name}' added"}), 201

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if conn:
            conn.rollback()
        if "duplicate key" in str(error):
            return jsonify({"success": False, "message": "This category already exists"}), 400
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()
# --- NEW ENDPOINT: SEARCH FOR SALES ---
@app.route('/api/search/sales', methods=['GET'])
def search_sales():
    """
    Searches for sales based on customer name and/or date.
    e.g., /api/search/sales?name=shreya
    e.g., /api/search/sales?date=2025-11-08
    e.g., /api/search/sales?name=shreya&date=2025-11-08
    """
    conn = None
    try:
        # Get query parameters from the URL
        customer_name = request.args.get('name')
        sales_date = request.args.get('date')

        if not customer_name and not sales_date:
            return jsonify({"message": "Please provide a name or date to search"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # --- 1. Build the Header Query Dynamically ---
        # This is the same base query as get_today_sales
        base_header_sql = """
            SELECT 
                s.sales_id, s.sales_date, s.doctor_name,
                c.customer_name, c.address, c.phone_number, c.invoice_number,
                ct.type_name AS customer_type,
                pm.mode_name AS payment_mode,
                i.total_amount, i.amount_paid, i.balance_amount, i.due_date,
                ps.status_name AS payment_status
            FROM sales s
            JOIN customer c ON s.customer_id = c.customer_id
            JOIN customer_type ct ON c.type_id = ct.type_id
            JOIN in_voice i ON s.sales_id = i.sales_id
            JOIN payment_mode pm ON s.mode_id = pm.mode_id
            JOIN payment_status ps ON i.status_id = ps.status_id
        """
        
        where_clauses = []
        params = []
        
        if customer_name:
            where_clauses.append("c.customer_name ILIKE %s") # ILIKE is case-insensitive
            params.append(f"%{customer_name}%") # Add % for partial matching
            
        if sales_date:
            where_clauses.append("s.sales_date = %s")
            params.append(sales_date)
            
        # Combine the query
        final_header_sql = base_header_sql + " WHERE " + " AND ".join(where_clauses) + " ORDER BY s.sales_date DESC"
        
        cursor.execute(final_header_sql, tuple(params))
        sales_headers = cursor.fetchall()
        
        if not sales_headers:
            return jsonify([]), 200 # Return empty list if no sales

        sales_ids = [h['sales_id'] for h in sales_headers]

        # --- 2. Fetch all associated items ---
        items_sql = """
            SELECT 
                si.sales_id,
                p.product_name AS "medicine_name",
                si.quantity_of_order AS "quantity",
                p.base_price AS "unit_price",
                si.discount AS "item_discount"
            FROM sale_item si
            JOIN product p ON si.product_id = p.product_id
            WHERE si.sales_id = ANY(%s);
        """
        cursor.execute(items_sql, (sales_ids,))
        all_items = cursor.fetchall()
        
        # --- 3. Assemble the JSON (same as get_today_sales) ---
        all_bills = []
        for header in sales_headers:
            sales_id = header['sales_id']
            bill_items_list = []
            for item in all_items:
                if item['sales_id'] == sales_id:
                    item_total = (float(item['quantity']) * float(item['unit_price'])) - float(item['item_discount'])
                    bill_items_list.append({
                        "bill_number": header['invoice_number'],
                        "medicine_name": item['medicine_name'],
                        "category": "N/A", "batch_no": "N/A", "expiry_date": "N/A",
                        "quantity": float(item['quantity']),
                        "unit_price": float(item['unit_price']),
                        "item_discount": float(item['item_discount']),
                        "item_total": item_total
                    })
            
            total_qty = sum(i['quantity'] for i in bill_items_list)
            sub_total = sum(i['item_total'] for i in bill_items_list)
            overall_discount = sub_total - float(header['total_amount'])

            bill_json = {
                "billHeader": {
                    "bill_number": header['invoice_number'],
                    "sales_date": header['sales_date'].strftime('%Y-%m-%d'),
                    "customer_name": header['customer_name'],
                    "customer_type": header['customer_type'],
                    "address": header['address'],
                    "phone_number": header['phone_number'],
                    "doctor_name": header['doctor_name']
                },
                "billItems": bill_items_list,
                "billSummary": {
                    "bill_number": header['invoice_number'],
                    "total_quantity": total_qty, "sub_total": sub_total,
                    "overall_discount": overall_discount,
                    "total_amount": float(header['total_amount'])
                },
                "billPayment": {
                    "bill_number": header['invoice_number'],
                    "payment_mode": header['payment_mode'],
                    "amount_paid": float(header['amount_paid']),
                    "balance_amount": float(header['balance_amount']),
                    "balance_due_date": header['due_date'].strftime('%Y-%m-%d') if header['due_date'] else None,
                    "payment_status": header['payment_status']
                }
            }
            all_bills.append(bill_json)
            
        return jsonify(all_bills), 200

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()
# --- (Your existing routes are above this) ---
from psycopg2.extras import RealDictCursor # Make sure this is imported at the top

# --- NEW ENDPOINT 1: GET ALL WHOLESALERS (for the dropdown) ---
@app.route('/api/wholesalers', methods=['GET'])
def get_wholesalers():
    """Fetches all wholesalers to populate a dropdown."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT wholesaler_id, wholesaler_name FROM wholesaler ORDER BY wholesaler_name")
        wholesalers = cursor.fetchall()
        return jsonify(wholesalers), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# --- NEW ENDPOINT 2: GET ALL CURRENT STOCK ---
# --- NEW ENDPOINT 2: GET ALL CURRENT STOCK ---
@app.route('/api/stock', methods=['GET'])
def get_all_stock():
    """Fetches all items currently in the in_stock table."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # --- THIS QUERY IS NOW UPDATED ---
        # It now joins 'wholesaler' and selects 'purchase_rate'
        query = """
            SELECT 
                p.product_name,
                w.wholesaler_name,
                i.stock_id,
                i.batch_no,
                i.quantity_of_units,
                i.mfg_date,
                i.exp_date,
                i.shelf_number,
                i.recieved_date,
                i.purchase_rate
            FROM in_stock i
            JOIN product p ON i.product_id = p.product_id
            LEFT JOIN wholesaler w ON i.wholesaler_id = w.wholesaler_id
            WHERE i.quantity_of_units > 0
            ORDER BY p.product_name, i.exp_date;
        """
        cursor.execute(query)
        stock_items = cursor.fetchall()
        
        # Convert date/numeric objects to strings for JSON
        for item in stock_items:
            item['mfg_date'] = item['mfg_date'].strftime('%Y-%m-%d') if item['mfg_date'] else None
            item['exp_date'] = item['exp_date'].strftime('%Y-%m-%d') if item['exp_date'] else None
            item['recieved_date'] = item['recieved_date'].strftime('%Y-%m-%d') if item['recieved_date'] else None
            item['purchase_rate'] = float(item['purchase_rate']) if item['purchase_rate'] else None
            
        return jsonify(stock_items), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# --- NEW ENDPOINT 3: ADD NEW STOCK (from a shipment) ---
# --- Endpoint for Stock Page: ADD NEW STOCK (Crucial for Analysis) ---
# --- Endpoint for Stock Page: ADD NEW STOCK (Crucial for Analysis) ---
@app.route('/api/stock', methods=['POST'])
def add_stock_entry():
    """Adds a new batch/shipment to the in_stock table."""
    data = request.get_json()
    conn = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        product_id = data.get('product_id')
        wholesaler_id = data.get('wholesaler_id')

        # This check ensures product_id and wholesaler_id are not empty
        if not product_id or not wholesaler_id or wholesaler_id == "":
            return jsonify({"success": False, "message": "Product and Wholesaler are required."}), 400

        # SQL to insert the new stock entry, including purchase_rate
        sql = """
            INSERT INTO in_stock (
                product_id, quantity_of_units, mfg_date, exp_date, 
                shelf_number, recieved_date, batch_no, wholesaler_id, purchase_rate
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(sql, (
            product_id,
            data.get('quantity'),
            data.get('mfg_date'),
            data.get('exp_date'),
            data.get('shelf_number'),
            data.get('received_date'),
            data.get('batch_no'),
            wholesaler_id,
            data.get('purchase_rate') # <-- This line saves your price
        ))
        
        conn.commit()
        return jsonify({"success": True, "message": "Stock added successfully."}), 201

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# --- NEW ENDPOINT: GET LOW STOCK ITEMS ---
@app.route('/api/stock/low', methods=['GET'])
def get_low_stock_alerts():
    """
    Fetches products where the SUM of their stock is below the reorder level.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # This query sums up all batches of a product and compares to the reorder level
        query = """
            SELECT 
                p.product_name,
                p.reorder_level,
                SUM(i.quantity_of_units) AS total_stock
            FROM product p
            JOIN in_stock i ON p.product_id = i.product_id
            GROUP BY p.product_id, p.product_name, p.reorder_level
            HAVING SUM(i.quantity_of_units) < p.reorder_level
            ORDER BY p.product_name;
        """
        cursor.execute(query)
        alerts = cursor.fetchall()
        
        # Convert numeric types to float for JSON
        for alert in alerts:
            alert['reorder_level'] = float(alert['reorder_level'])
            alert['total_stock'] = float(alert['total_stock'])
            
        return jsonify(alerts), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# --- NEW ENDPOINT: GET NEAR EXPIRY ITEMS ---
@app.route('/api/stock/expiring', methods=['GET'])
def get_near_expiry_alerts():
    """
    Fetches all stock items expiring within the next 90 days.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # This query finds all batches expiring between today and 90 days from now.
        query = """
            SELECT 
                p.product_name,
                i.batch_no,
                i.quantity_of_units,
                i.exp_date
            FROM in_stock i
            JOIN product p ON i.product_id = p.product_id
            WHERE i.exp_date BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '90 days')
            ORDER BY i.exp_date ASC;
        """
        cursor.execute(query)
        alerts = cursor.fetchall()
        
        # Convert date objects to strings
        for alert in alerts:
            alert['exp_date'] = alert['exp_date'].strftime('%Y-%m-%d')
            alert['quantity_of_units'] = float(alert['quantity_of_units'])
            
        return jsonify(alerts), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# --- NEW ENDPOINT: ADD A NEW WHOLESALER ---
from psycopg2.extras import RealDictCursor # Make sure this is imported at the top

# --- NEW ENDPOINT 1: GET ALL WHOLESALERS (for the new list) ---
# --- (This is the route for your wholesaler list) ---
@app.route('/api/wholesalers/list', methods=['GET'])
def get_wholesaler_list():
    """Fetches all wholesalers to populate a list."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # --- UPDATED to select all new columns ---
        cursor.execute("SELECT wholesaler_id, wholesaler_name, mobile_number, email, address, tax_id, drug_license FROM wholesaler ORDER BY wholesaler_name")
        
        wholesalers = cursor.fetchall()
        return jsonify(wholesalers), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# --- NEW ENDPOINT 2: ADD A NEW WHOLESALER ---
@app.route('/api/wholesalers', methods=['POST'])
def create_wholesaler():
    """Creates a new wholesaler."""
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
            INSERT INTO wholesaler (wholesaler_name, address, mobile_number, email, tax_id , drug_license)
            VALUES (%s, %s, %s, %s, %s , %s)
        """
        cursor.execute(sql, (
            data.get('name'),
            data.get('address'),
            data.get('mobile_number'),
            data.get('email'),
            data.get('tax_id'),
            data.get('drug_license')
        ))
        conn.commit()
        return jsonify({"success": True, "message": "Wholesaler added."}), 201

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# --- NEW ENDPOINT 3: GET PROFIT ANALYSIS FOR A SINGLE PRODUCT ---
@app.route('/api/wholesalers/analysis/<string:product_name>', methods=['GET'])
def get_single_product_analysis(product_name):
    """
    Compares profit margin for a single product across all its wholesalers.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                p.product_name,
                w.wholesaler_name,
                p.base_price AS sale_price,
                AVG(i.purchase_rate) AS avg_purchase_price,
                (p.base_price - AVG(i.purchase_rate)) AS profit_margin,
                COUNT(i.stock_id) AS total_batches_bought
            FROM in_stock i
            JOIN product p ON i.product_id = p.product_id
            JOIN wholesaler w ON i.wholesaler_id = w.wholesaler_id
            WHERE 
                i.purchase_rate IS NOT NULL 
                AND p.product_name ILIKE %s
            GROUP BY 
                p.product_id, w.wholesaler_id, p.product_name, w.wholesaler_name, p.base_price
            ORDER BY 
                profit_margin DESC;
        """
        cursor.execute(query, (f"%{product_name}%",))
        analysis = cursor.fetchall()
        
        if not analysis:
            return jsonify({"success": False, "message": f"No purchase history found for '{product_name}'."}), 404

        # Convert numeric types
        for row in analysis:
            row['sale_price'] = float(row['sale_price'])
            row['avg_purchase_price'] = float(row['avg_purchase_price'])
            row['profit_margin'] = float(row['profit_margin'])
            
        return jsonify(analysis), 200
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()
from psycopg2.extras import RealDictCursor # Make sure this is at the top of your app.py
from datetime import date # Make sure this is at the top of your app.py

## 
## 📊 ANALYTICS ENDPOINTS - SALES & PROFITABILITY
## 

# 1. Top Selling Products (by Quantity)
@app.route('/api/analytics/top-selling-qty', methods=['GET'])
def get_top_selling_by_qty():
    """Fetches top 10 selling products by total quantity sold."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT 
                p.product_name,
                SUM(si.quantity_of_order) AS total_units_sold
            FROM sale_item si
            JOIN product p ON si.product_id = p.product_id
            GROUP BY p.product_id, p.product_name
            ORDER BY total_units_sold DESC
            LIMIT 10;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        for row in data:
            row['total_units_sold'] = float(row['total_units_sold'])
        return jsonify(data), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# 2. Top Selling Products (by Revenue)
@app.route('/api/analytics/top-selling-revenue', methods=['GET'])
def get_top_selling_by_revenue():
    """Fetches top 10 selling products by total revenue."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT 
                p.product_name,
                SUM(si.quantity_of_order * p.base_price) AS total_revenue
            FROM sale_item si
            JOIN product p ON si.product_id = p.product_id
            GROUP BY p.product_id, p.product_name
            ORDER BY total_revenue DESC
            LIMIT 10;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        for row in data:
            row['total_revenue'] = float(row['total_revenue'])
        return jsonify(data), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# 3. Most Profitable Products (Profit Margin)
@app.route('/api/analytics/most-profitable', methods=['GET'])
def get_most_profitable():
    """
    Fetches top 10 most profitable products.
    Profit = (base_price - Avg Purchase Price) * Units Sold
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # This query first finds the avg cost of each product from in_stock
        query = """
            WITH AvgStockPrice AS (
                SELECT product_id, AVG(purchase_rate) as avg_cost
                FROM in_stock
                WHERE purchase_rate IS NOT NULL
                GROUP BY product_id
            ),
            SalesTotals AS (
                SELECT product_id, SUM(quantity_of_order) as total_units_sold
                FROM sale_item
                GROUP BY product_id
            )
            SELECT 
                p.product_name,
                st.total_units_sold,
                p.base_price AS sale_price,
                asp.avg_cost AS purchase_cost,
                (p.base_price - asp.avg_cost) * st.total_units_sold AS total_profit
            FROM SalesTotals st
            JOIN product p ON st.product_id = p.product_id
            LEFT JOIN AvgStockPrice asp ON st.product_id = asp.product_id
            WHERE asp.avg_cost IS NOT NULL
            ORDER BY total_profit DESC
            LIMIT 10;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        for row in data:
            row['total_units_sold'] = float(row['total_units_sold'])
            row['sale_price'] = float(row['sale_price'])
            row['purchase_cost'] = float(row['purchase_cost'])
            row['total_profit'] = float(row['total_profit'])
        return jsonify(data), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# 4. Sales & Profit Over Time (Line Chart)
@app.route('/api/analytics/sales-over-time', methods=['GET'])
def get_sales_over_time():
    """Fetches total sales revenue per day for the last 30 days."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT 
                s.sales_date AS date,
                SUM(i.total_amount) AS total_revenue
            FROM sales s
            JOIN in_voice i ON s.sales_id = i.sales_id
            WHERE s.sales_date >= (CURRENT_DATE - INTERVAL '30 days')
            GROUP BY s.sales_date
            ORDER BY s.sales_date ASC;
        """
        cursor.execute(query)
        sales_data = cursor.fetchall()
        for row in sales_data:
            row['date'] = row['date'].strftime('%Y-%m-%d')
            row['total_revenue'] = float(row['total_revenue'])
        return jsonify(sales_data), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()
# 5. Slowest-Moving Items (Dead Stock)
@app.route('/api/analytics/slow-moving', methods=['GET'])
def get_slow_moving():
    """Fetches products that have not sold in the last 90 days."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # This query finds products last sold > 90 days ago, or never sold
        query = """
            SELECT 
                p.product_name, 
                MAX(s.sales_date) as last_sold_date
            FROM product p
            LEFT JOIN sale_item si ON p.product_id = si.product_id
            LEFT JOIN sales s ON si.sales_id = s.sales_id
            GROUP BY p.product_id, p.product_name
            HAVING MAX(s.sales_date) < (CURRENT_DATE - INTERVAL '90 days')
                OR MAX(s.sales_date) IS NULL
            ORDER BY last_sold_date ASC NULLS FIRST;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        for row in data:
            if row['last_sold_date']:
                row['last_sold_date'] = row['last_sold_date'].strftime('%Y-%m-%d')
            else:
                row['last_sold_date'] = 'Never Sold'
        return jsonify(data), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# 6. Inventory Value
@app.route('/api/analytics/inventory-value', methods=['GET'])
def get_inventory_value():
    """Calculates the total value of all current inventory based on purchase rate."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # This query sums up the value (qty * price) of all items in stock
        query = """
            SELECT SUM(quantity_of_units * purchase_rate) AS total_value
            FROM in_stock
            WHERE purchase_rate IS NOT NULL AND quantity_of_units > 0;
        """
        cursor.execute(query)
        data = cursor.fetchone()
        
        if data and data['total_value']:
            data['total_value'] = float(data['total_value'])
        else:
            data = {'total_value': 0} # Handle case where stock is empty
            
        return jsonify(data), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/analytics/top-customers', methods=['GET'])
def get_top_customers():
    """Fetches top 10 customers by total amount spent."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # We join customer, sales, and invoice to sum up total spending
        query = """
            SELECT 
                c.customer_name,
                c.phone_number,
                SUM(i.total_amount) as total_spent
            FROM customer c
            JOIN sales s ON c.customer_id = s.customer_id
            JOIN in_voice i ON s.sales_id = i.sales_id
            GROUP BY c.customer_id, c.customer_name, c.phone_number
            ORDER BY total_spent DESC
            LIMIT 10;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        for row in data:
            row['total_spent'] = float(row['total_spent'])
        return jsonify(data), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# 8. Total Pending Balance (Single Number)
@app.route('/api/analytics/pending-total', methods=['GET'])
def get_pending_total():
    """Calculates the total outstanding balance from all invoices."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT SUM(balance_amount) AS total_pending
            FROM in_voice
            WHERE balance_amount > 0;
        """
        cursor.execute(query)
        data = cursor.fetchone()
        if data and data['total_pending']:
            data['total_pending'] = float(data['total_pending'])
        else:
            data = {'total_pending': 0} # Handle case where nothing is pending
        return jsonify(data), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# 9. Pending Balance Details List
@app.route('/api/analytics/pending-list', methods=['GET'])
def get_pending_list():
    """Gets details for all sales with an outstanding balance."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # We join all tables to get the required info
        query = """
            SELECT 
                c.invoice_number AS bill_number,
                s.sales_date,
                c.customer_name,
                c.phone_number,
                i.balance_amount,
                i.due_date
            FROM in_voice i
            JOIN sales s ON i.sales_id = s.sales_id
            JOIN customer c ON s.customer_id = c.customer_id
            WHERE i.balance_amount > 0
            ORDER BY i.due_date ASC NULLS LAST, s.sales_date ASC;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        for row in data:
            row['sales_date'] = row['sales_date'].strftime('%Y-%m-%d')
            row['due_date'] = row['due_date'].strftime('%Y-%m-%d') if row['due_date'] else 'N/A'
            row['balance_amount'] = float(row['balance_amount'])
        return jsonify(data), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500
    finally:
        if conn:
            conn.close()

# --- (This should be at the very end) ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)