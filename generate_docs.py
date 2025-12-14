import os
import pandas as pd
import glob
import shutil

# Configuration
DATA_DIR = 'Sales Dataset'
JUNK_FILES = [
    'Expense IIGF.csv', 
    'Cloud Warehouse Compersion Chart.csv'
]

# Descriptions
TABLE_DESCRIPTIONS = {
    'Amazon Sale Report': "Primary sales transaction table containing details of orders placed on Amazon, including status, amount, and fulfillment information.",
    'International sale Report': "Records of international sales transactions, focusing on customer details and gross amounts.",
    'Sale Report': "Inventory and stock master table showing available stock levels for different designs and sizes.",
    'May-2022': "Product master data for May 2022, containing MRP, transfer prices, and weight details for SKUs.",
    'P  L March 2021': "Product master and Profit & Loss related data for March 2021, similar to the May-2022 file."
}

COLUMN_DESCRIPTIONS = {
    'Order ID': "Unique identifier for each customer order.",
    'Date': "Date when the order was placed.",
    'Status': "Current status of the order (e.g., Shipped, Cancelled, Delivered).",
    'Fulfilment': "Entity responsible for fulfilling the order (e.g., Amazon, Merchant).",
    'Sales Channel': "Platform where the sale occurred (e.g., Amazon.in).",
    'ship-service-level': "Shipping priority level (e.g., Standard, Expedited).",
    'Style': "Style identifier of the product.",
    'SKU': "Stock Keeping Unit - unique identifier for the specific product variant.",
    'Category': "Product category (e.g., Kurta, Set, Top).",
    'Size': "Size of the product (e.g., S, M, L, XL).",
    'ASIN': "Amazon Standard Identification Number.",
    'Courier Status': "Delivery status reported by the courier.",
    'Qty': "Quantity of items ordered.",
    'currency': "Currency of the transaction (e.g., INR).",
    'Amount': "Total transaction amount.",
    'ship-city': "City where the order is being shipped.",
    'ship-state': "State where the order is being shipped.",
    'ship-postal-code': "Postal code of the shipping address.",
    'ship-country': "Country of the shipping address.",
    'promotion-ids': "IDs of any promotions applied to the order.",
    'B2B': "Boolean indicating if the order is a Business-to-Business transaction.",
    'fulfilled-by': "Specific entity handling fulfillment (e.g., Easy Ship).",
    'Stock': "Current quantity available in inventory.",
    'Design No.': "Design number associated with the product.",
    'Color': "Color of the product.",
    'GROSS AMT': "Gross amount of the sale before deductions.",
    'CUSTOMER': "Name of the customer (for international sales).",
    'MRP Old': "Maximum Retail Price (Old).",
    'Final MRP Old': "Final adjusted MRP (Old).",
    'TP': "Transfer Price.",
    'Weight': "Weight of the product."
}

def clean_and_document():
    # 1. Delete Junk Files
    print("--- Cleaning Junk Files ---")
    for junk in JUNK_FILES:
        path = os.path.join(DATA_DIR, junk)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"Deleted: {junk}")
            except Exception as e:
                print(f"Error deleting {junk}: {e}")
        else:
            print(f"Not found (already deleted): {junk}")

    # 2. Generate Documentation
    print("\n--- Generating Documentation ---")
    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        table_name = os.path.splitext(filename)[0]
        
        print(f"Processing: {table_name}")
        
        try:
            # Read Data
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='ISO-8859-1')
            
            # Drop index if present
            if 'index' in df.columns:
                df = df.drop(columns=['index'])
                
            # Create Directory
            doc_dir = os.path.join(DATA_DIR, table_name)
            os.makedirs(doc_dir, exist_ok=True)
            
            # Write Table Description
            desc_file = os.path.join(doc_dir, f"{table_name}_desc.txt")
            with open(desc_file, 'w', encoding='utf-8') as f:
                desc = TABLE_DESCRIPTIONS.get(table_name, f"Data table for {table_name}.")
                f.write(f"{desc}\n\n")
                f.write("Top 3 Rows:\n")
                f.write(df.head(3).to_string(index=False))
            
            # Write Column Descriptions
            for col in df.columns:
                col_clean = col.strip()
                col_file = os.path.join(doc_dir, f"{col_clean}_desc.txt")
                
                # Sanitize filename (remove invalid chars)
                col_file = "".join([c for c in col_file if c.isalnum() or c in (' ', '.', '_', '-', '\\', '/')])
                
                with open(col_file, 'w', encoding='utf-8') as f:
                    col_desc = COLUMN_DESCRIPTIONS.get(col_clean, f"Column representing {col_clean}.")
                    f.write(f"{col_desc}\n")
                    
                    # Add unique values for categorical/low-cardinality columns
                    if df[col].dtype == 'object' or df[col].nunique() < 20:
                        unique_vals = df[col].dropna().unique()
                        if len(unique_vals) > 0 and len(unique_vals) < 50:
                            f.write("\nUnique Values:\n")
                            for val in unique_vals:
                                f.write(f"- {val}\n")
                        elif len(unique_vals) >= 50:
                             f.write(f"\n(Contains {len(unique_vals)} unique values - too many to list)\n")
                             
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    clean_and_document()
