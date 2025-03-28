import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

def verificar_contraseña():
    contraseña_correcta = "nepos123"  # Reemplaza con la contraseña correcta

    if entrada_contraseña.get() == contraseña_correcta:
        ventana_login.destroy()  # Cerrar la ventana de login
        mostrar_ventana_principal()  # Llamar a la función para mostrar la ventana principal
    else:
        messagebox.showerror("Error", "Contraseña incorrecta. Intenta de nuevo.")
        
# Función para cargar los datos desde la base de datos
def cargar_datos():
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect('inventario_nepos.db')  # Reemplaza con el nombre de tu DB
        cursor = conn.cursor()

        # Consulta a la base de datos
        cursor.execute("SELECT * FROM PRODUCTOS")  # Reemplaza 'mi_tabla' con el nombre de tu tabla
        registros = cursor.fetchall()

        # Limpiar el Treeview antes de cargar nuevos datos
        for row in tree.get_children():
            tree.delete(row)

        # Insertar registros en el Treeview
        for registro in registros:
            tree.insert("", tk.END, values=registro)

        # Cerrar la conexión
        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror("Error", f"No se pudo acceder a la base de datos: {e}")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Visualizador de Base de Datos SQLite")

# Crear un Treeview para mostrar los datos
tree = ttk.Treeview(ventana, columns=("Cod_Prod", "Descripción", "Unidad","Precio_Unit", "Precio_Iva", "Paga_Impuesto", "Existencia", "Observación" ), show="headings")
tree.heading("Cod_Prod", text="Cod_Prod")
tree.heading("Descripción", text="Descripción")
tree.heading("Unidad", text="Unidad")
tree.heading("Precio_Unit", text="Precio_Unit")
tree.heading("Precio_Iva", text="Precio_Iva")
tree.heading("Paga_Impuesto", text="Paga_Impuesto")
tree.heading("Existencia", text="Existencia")
tree.heading("Observación", text="Observación")
tree.pack(fill=tk.BOTH, expand=True)

# Botón para cargar los datos
boton_cargar = tk.Button(ventana, text="Cargar Datos", command=cargar_datos)
boton_cargar.pack(pady=10)

# Ejecutar la interfaz gráfica
ventana.mainloop()

# Crear la ventana de login
ventana_login = tk.Tk()
ventana_login.title("Iniciar sesión")

# Etiqueta de la contraseña
etiqueta_contraseña = tk.Label(ventana_login, text="Introduce la contraseña:")
etiqueta_contraseña.pack(pady=10)

# Entrada para la contraseña
entrada_contraseña = tk.Entry(ventana_login, show="*")  # El "show='*'" oculta la contraseña
entrada_contraseña.pack(pady=10)

# Botón para verificar la contraseña
boton_ingresar = tk.Button(ventana_login, text="Ingresar", command=verificar_contraseña)
boton_ingresar.pack(pady=10)

# Ejecutar la ventana de login
ventana_login.mainloop()
