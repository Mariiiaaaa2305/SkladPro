
CREATE DATABASE IF NOT EXISTS warehouse_management
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE warehouse_management;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'manager') NOT NULL DEFAULT 'manager',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(120),
    phone VARCHAR(30),
    email VARCHAR(120),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contractors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    contractor_type ENUM('customer', 'partner', 'other')
        NOT NULL DEFAULT 'customer',
    phone VARCHAR(30),
    email VARCHAR(120),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    sku VARCHAR(80) NOT NULL UNIQUE,
    description TEXT,
    quantity INT NOT NULL DEFAULT 0,
    min_quantity INT NOT NULL DEFAULT 5,
    price DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    supplier_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_supplier
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        ON DELETE SET NULL,
    CONSTRAINT chk_products_quantity CHECK (quantity >= 0),
    CONSTRAINT chk_products_min_quantity CHECK (min_quantity >= 0),
    CONSTRAINT chk_products_price CHECK (price >= 0)
);

CREATE TABLE IF NOT EXISTS stock_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    movement_type ENUM('receipt', 'shipment', 'write_off') NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    notes TEXT,
    created_by INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_movements_product
        FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_movements_user
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL,
    CONSTRAINT chk_movements_quantity CHECK (quantity > 0),
    CONSTRAINT chk_movements_price CHECK (unit_price >= 0)
);

CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_number VARCHAR(50) NOT NULL UNIQUE,
    document_type ENUM('invoice', 'act') NOT NULL,
    contractor_id INT NULL,
    supplier_id INT NULL,
    created_by INT NULL,
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_documents_contractor
        FOREIGN KEY (contractor_id) REFERENCES contractors(id)
        ON DELETE SET NULL,
    CONSTRAINT fk_documents_supplier
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        ON DELETE SET NULL,
    CONSTRAINT fk_documents_user
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL,
    CONSTRAINT chk_documents_total CHECK (total_amount >= 0)
);

CREATE TABLE IF NOT EXISTS document_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    CONSTRAINT fk_document_items_document
        FOREIGN KEY (document_id) REFERENCES documents(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_document_items_product
        FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT chk_document_items_quantity CHECK (quantity > 0),
    CONSTRAINT chk_document_items_price CHECK (unit_price >= 0)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    message VARCHAR(255) NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notifications_product
        FOREIGN KEY (product_id) REFERENCES products(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_movements_created_at
    ON stock_movements(created_at);

CREATE INDEX idx_movements_product_date
    ON stock_movements(product_id, created_at);

CREATE INDEX idx_documents_created_at
    ON documents(created_at);
```