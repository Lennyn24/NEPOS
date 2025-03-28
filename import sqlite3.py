import sqlite3

# Conectar a la base de datos SQLite (puedes poner el nombre de tu base de datos .db)
conn = sqlite3.connect('inventario_nepos.db')  # Reemplaza 'mydatabase.db' con el nombre de tu archivo .db

# Crear un cursor para ejecutar comandos SQL
cursor = conn.cursor()

# Realizar una consulta SQL (SELECT)
cursor.execute("SELECT * FROM PRODUCTOSN")  # Reemplaza 'PRODUCTOS' con el nombre de tu tabla
registros = cursor.fetchall()

# Imprimir los registros obtenidos
for registro in registros:
    print(registro)

# Cerrar la conexión después de realizar las operaciones
conn.close()
