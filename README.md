# 💊 Pharmacy Management System — TSA Project

A full-stack web application for managing day-to-day operations of a medical/pharmacy shop. Built with **Flask (Python)** on the backend and **vanilla HTML/Tailwind CSS** on the frontend, connected to a **PostgreSQL (Neon)** cloud database.

---

## 📁 Project Structure

```
pharmacy_system/
├── app.py                  # Flask backend — all API endpoints
├── static/
│   └── front.js            # Shared frontend JavaScript logic
├── templates/
│   ├── homepage1.html      # Main dashboard / navigation hub
│   ├── test2.html          # New Sales Bill form
│   ├── customer_search1.html  # Search sales by name or date
│   ├── b_analysis4.html    # Analytics & reports dashboard
│   ├── in_stock2.html      # Stock / inventory management
│   ├── product1.html       # Product viewer
│   ├── product2.html       # Product master (add/edit)
│   └── wholesaler3.html    # Wholesaler management
├── medical_shop_dump.sql   # Full PostgreSQL schema + seed data
├── sql.sql                 # Quick query scratchpad
├── .gitignore
└── README.md
```

---

## 🗃️ Database Schema (PostgreSQL via Neon)

| Table | Purpose |
|---|---|
| `customer` | Stores customer name, phone, address, type |
| `customer_type` | Lookup: General / Doctor / Wholesale |
| `sales` | One record per bill — links customer, date, payment mode |
| `sale_item` | Line items per sale — product + quantity + discount |
| `in_voice` | Invoice/payment record — totals, balance, due date |
| `product` | Medicine master — name, MRP, GST, purchase rate, profit |
| `product_category` | Drug categories (e.g., Antibiotic, Vitamin) |
| `in_stock` | Live inventory — qty, batch, shelf, expiry per product |
| `wholesaler` | Supplier info — name, contact, drug license, tax ID |
| `payment_mode` | Lookup: Cash / Card / UPI |
| `payment_status` | Lookup: Paid / Balance |
| `notification` | System notifications (low stock alerts etc.) |

> **Note:** `product.profit` is a **generated column** in PostgreSQL — auto-calculated as `base_price - purchase_rate * (1 + gst/100)`.

---

## 🔌 API Endpoints (Flask — `app.py`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/sales` | Create a full sales bill (customer + sale + items + invoice) |
| GET | `/api/medicines` | Fetch all products with stock details |
| GET | `/api/product/<id>` | Get a single product by ID |
| GET | `/api/next-bill-number` | Get the next auto-incremented bill number |
| GET | `/api/search/sales` | Search sales by customer name or date |
| POST | `/api/stock` | Add new stock / inventory entry |
| POST | `/api/product` | Add a new product to master |
| GET | `/api/wholesalers` | List all wholesalers |
| POST | `/api/wholesaler` | Add a new wholesaler |
| GET | `/api/analytics/kpis` | Top KPI numbers (revenue, bills, customers) |
| GET | `/api/analytics/top-products` | Best-selling medicines |
| GET | `/api/analytics/top-profit` | Most profitable medicines |
| GET | `/api/analytics/sales-over-time` | Daily revenue for last 30 days |
| GET | `/api/analytics/slow-moving` | Dead stock (not sold in 90+ days) |
| GET | `/api/analytics/inventory-value` | Total value of current inventory |
| GET | `/api/analytics/top-customers` | Top 10 customers by spend |
| GET | `/api/analytics/pending-total` | Total outstanding balance |
| GET | `/api/analytics/pending-list` | Detailed list of pending payments |

---

## ⚙️ Setup & Run

### Prerequisites
- Python 3.10+
- pip
- A Neon PostgreSQL account (or any PostgreSQL server)

### 1. Install Dependencies
```bash
pip install flask flask-cors psycopg2-binary
```

### 2. Configure Database
Open `app.py` and update the `DB_CONFIG` dictionary:
```python
DB_CONFIG = {
    "dbname": "your_db_name",
    "user": "your_user",
    "password": "your_password",
    "host": "your_host",
    "port": "5432",
    "sslmode": "require"   # Remove this line if not using Neon/SSL
}
```

### 3. Import the Database Schema
```bash
psql -U your_user -d your_db -f medical_shop_dump.sql
```

### 4. Run the Server
```bash
python app.py
```
Server starts at `http://127.0.0.1:5000`

### 5. Open the App
Open `templates/homepage1.html` in your browser, or serve via Flask templates.

---

## 🌟 Key Features

- **New Sales Bill** — Multi-item billing with auto-fetched product details, GST, discount, and live balance calculation
- **Customer Auto-Create** — If a phone number is new, a customer record is created automatically
- **Inventory Auto-Deduction** — Stock is reduced automatically on every sale
- **Search Portal** — Find any past bill by customer name or date
- **Analytics Dashboard** — Charts for top products, revenue trends, slow-moving stock, pending payments
- **Stock Management** — Add new inventory batches with shelf and expiry info
- **Product Master** — Full CRUD on medicine catalog
- **Wholesaler Management** — Track suppliers and analyze profitability

---

## 🔐 Security Note

> ⚠️ The database credentials in `app.py` are currently hardcoded. Before deploying or pushing to a public repository, move them to a `.env` file and use `python-dotenv`:
```bash
pip install python-dotenv
```
```python
from dotenv import load_dotenv
import os
load_dotenv()
DB_CONFIG = {
    "password": os.getenv("DB_PASSWORD"),
    ...
}
```
Add `.env` to your `.gitignore`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-CORS |
| Database | PostgreSQL (hosted on Neon) |
| DB Driver | psycopg2 |
| Frontend | HTML5, Tailwind CSS, Vanilla JS |
| Icons | Lucide Icons |
| Date Picker | Flatpickr |
| Hosting (DB) | Neon Serverless PostgreSQL |

---

## 👨‍💻 Author

 Medical Shop Management System  
Academic project demonstrating full-stack development with PostgreSQL.
