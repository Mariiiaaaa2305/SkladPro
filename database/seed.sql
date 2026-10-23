
USE warehouse_management;

INSERT INTO suppliers (name, contact_person, phone, email)
VALUES
    ('ТехноПостач', 'Іван Петренко', '+380501112233', 'tech@example.com'),
    ('СкладСервіс', 'Олена Коваль', '+380671234567', 'stock@example.com');

INSERT INTO contractors (name, contractor_type, phone, email)
VALUES
    ('Магазин Плюс', 'customer', '+380931234567', 'shop@example.com');

INSERT INTO products (name, sku, description, quantity, min_quantity, price, supplier_id)
VALUES
    ('Клавіатура USB', 'KB-001', 'Дротова клавіатура', 25, 5, 650.00, 1),
    ('Миша USB', 'MS-001', 'Оптична миша', 3, 10, 320.00, 1),
    ('Монітор 24 дюйми', 'MN-001', 'Монітор Full HD', 12, 3, 4500.00, 2);
