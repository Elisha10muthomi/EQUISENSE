from database import get_connection

connection = get_connection()

if connection:
    print("✅ Database connection successful!")
    connection.close()
else:
    print("❌ Connection failed!")