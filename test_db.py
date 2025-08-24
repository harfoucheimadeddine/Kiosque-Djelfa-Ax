from modules import db_utils

# Create a sale
sale_id = db_utils.create_sale(store_id=1)

# Add an item (2 Coca-Cola)
db_utils.add_sale_item(sale_id, item_id=1, quantity=2, price=150.0)

# Show sales summary
print("📊 All time:", db_utils.get_sales_summary("all"))
