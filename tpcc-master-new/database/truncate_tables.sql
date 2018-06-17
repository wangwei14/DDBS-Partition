SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;

-- ALTER TABLE district  DROP FOREIGN KEY fkey_district_1;
-- ALTER TABLE customer DROP FOREIGN KEY fkey_customer_1;
-- ALTER TABLE history  DROP FOREIGN KEY fkey_history_2;
-- ALTER TABLE new_orders DROP FOREIGN KEY fkey_new_orders_1;
-- ALTER TABLE orders DROP FOREIGN KEY fkey_orders_1;
-- ALTER TABLE order_line DROP FOREIGN KEY fkey_order_line_1;
-- ALTER TABLE stock DROP FOREIGN KEY fkey_stock_1;
-- ALTER TABLE stock DROP FOREIGN KEY fkey_stock_2;
-- ALTER TABLE history  DROP FOREIGN KEY fkey_history_1;
-- ALTER TABLE order_line DROP FOREIGN KEY fkey_order_line_2;

truncate table warehouse;
truncate table item;
truncate table new_orders;
truncate table order_line;
truncate table orders;
truncate table history;
truncate table customer;
truncate table district;
truncate table stock;


SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

