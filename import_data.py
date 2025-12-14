import sqlite3
import pandas as pd
import os

DB_NAME = 'Database/iris.db'
SCHEMA_FILE = 'Database/schema.sql'
RAW_DATA_DIR = 'Sales Dataset/Raw_data'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    with open(SCHEMA_FILE, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    return conn

def load_product_master(conn):
    print("Loading Product Master...")
    file_path = os.path.join(RAW_DATA_DIR, 'May-2022.csv')
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
        
    # Rename columns to match schema
    df.columns = [c.strip() for c in df.columns]
    column_map = {
        'Sku': 'sku', 'Style Id': 'style_id', 'Catalog': 'catalog', 'Category': 'category',
        'Weight': 'weight', 'TP': 'tp', 'MRP Old': 'mrp_old', 'Final MRP Old': 'final_mrp_old',
        'Ajio MRP': 'ajio_mrp', 'Amazon MRP': 'amazon_mrp', 'Amazon FBA MRP': 'amazon_fba_mrp',
        'Flipkart MRP': 'flipkart_mrp', 'Limeroad MRP': 'limeroad_mrp', 'Myntra MRP': 'myntra_mrp',
        'Paytm MRP': 'paytm_mrp', 'Snapdeal MRP': 'snapdeal_mrp'
    }
    df = df.rename(columns=column_map)
    
    # Keep only schema columns
    schema_cols = list(column_map.values())
    df = df[schema_cols]
    
    df.to_sql('product_master', conn, if_exists='replace', index=False)
    print(f"Loaded {len(df)} rows into product_master")

def load_amazon_sales(conn):
    print("Loading Amazon Sales...")
    file_path = os.path.join(RAW_DATA_DIR, 'Amazon Sale Report.csv')
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')

    df.columns = [c.strip() for c in df.columns]
    
    # Date conversion
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
    
    column_map = {
        'Order ID': 'order_id', 'Date': 'date', 'Status': 'status', 'Fulfilment': 'fulfilment',
        'Sales Channel': 'sales_channel', 'ship-service-level': 'ship_service_level',
        'Style': 'style', 'SKU': 'sku', 'Category': 'category', 'Size': 'size', 'ASIN': 'asin',
        'Courier Status': 'courier_status', 'Qty': 'qty', 'currency': 'currency', 'Amount': 'amount',
        'ship-city': 'ship_city', 'ship-state': 'ship_state', 'ship-postal-code': 'ship_postal_code',
        'ship-country': 'ship_country', 'promotion-ids': 'promotion_ids', 'B2B': 'b2b',
        'fulfilled-by': 'fulfilled_by'
    }
    df = df.rename(columns=column_map)
    
    # Filter columns
    df = df[[c for c in column_map.values() if c in df.columns]]
    
    df.to_sql('amazon_sales', conn, if_exists='replace', index=False)
    print(f"Loaded {len(df)} rows into amazon_sales")

def load_international_sales(conn):
    print("Loading International Sales...")
    file_path = os.path.join(RAW_DATA_DIR, 'International sale Report.csv')
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')

    df.columns = [c.strip() for c in df.columns]
    
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce').dt.date
    
    column_map = {
        'DATE': 'date', 'Months': 'months', 'CUSTOMER': 'customer', 'Style': 'style',
        'SKU': 'sku', 'Size': 'size', 'PCS': 'pcs', 'RATE': 'rate', 'GROSS AMT': 'gross_amt'
    }
    df = df.rename(columns=column_map)
    df = df[[c for c in column_map.values() if c in df.columns]]
    
    df.to_sql('international_sales', conn, if_exists='replace', index=False)
    print(f"Loaded {len(df)} rows into international_sales")

def load_inventory(conn):
    print("Loading Inventory...")
    file_path = os.path.join(RAW_DATA_DIR, 'Sale Report.csv')
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')

    df.columns = [c.strip() for c in df.columns]
    
    column_map = {
        'SKU Code': 'sku_code', 'Design No.': 'design_no', 'Stock': 'stock',
        'Category': 'category', 'Size': 'size', 'Color': 'color'
    }
    df = df.rename(columns=column_map)
    df = df[[c for c in column_map.values() if c in df.columns]]
    
    df.to_sql('inventory', conn, if_exists='replace', index=False)
    print(f"Loaded {len(df)} rows into inventory")

def main():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        
    conn = init_db()
    
    try:
        load_product_master(conn)
        load_amazon_sales(conn)
        load_international_sales(conn)
        load_inventory(conn)
        print("Data import completed successfully.")
    except Exception as e:
        print(f"Error importing data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
