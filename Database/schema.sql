-- Amazon Sales Report (Primary Transaction Table)
CREATE TABLE IF NOT EXISTS amazon_sales (
    order_id TEXT PRIMARY KEY,
    date DATE,
    status TEXT,
    fulfilment TEXT,
    sales_channel TEXT,
    ship_service_level TEXT,
    style TEXT,
    sku TEXT,
    category TEXT,
    size TEXT,
    asin TEXT,
    courier_status TEXT,
    qty INTEGER,
    currency TEXT,
    amount REAL,
    ship_city TEXT,
    ship_state TEXT,
    ship_postal_code TEXT,
    ship_country TEXT,
    promotion_ids TEXT,
    b2b BOOLEAN,
    fulfilled_by TEXT,
    FOREIGN KEY (sku) REFERENCES product_master(sku)
);

-- International Sales Report
CREATE TABLE IF NOT EXISTS international_sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    months TEXT,
    customer TEXT,
    style TEXT,
    sku TEXT,
    size TEXT,
    pcs INTEGER,
    rate REAL,
    gross_amt REAL,
    FOREIGN KEY (sku) REFERENCES product_master(sku)
);

-- Inventory / Sale Report
CREATE TABLE IF NOT EXISTS inventory (
    sku_code TEXT PRIMARY KEY,
    design_no TEXT,
    stock INTEGER,
    category TEXT,
    size TEXT,
    color TEXT,
    FOREIGN KEY (sku_code) REFERENCES product_master(sku)
);

-- Product Master (from May-2022.csv)
CREATE TABLE IF NOT EXISTS product_master (
    sku TEXT PRIMARY KEY,
    style_id TEXT,
    catalog TEXT,
    category TEXT,
    weight REAL,
    tp REAL, -- Transfer Price
    mrp_old REAL,
    final_mrp_old REAL,
    ajio_mrp REAL,
    amazon_mrp REAL,
    amazon_fba_mrp REAL,
    flipkart_mrp REAL,
    limeroad_mrp REAL,
    myntra_mrp REAL,
    paytm_mrp REAL,
    snapdeal_mrp REAL
);
