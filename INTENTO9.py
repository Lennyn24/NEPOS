import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import webbrowser
import os
import datetime

def obtener_fecha_modificacion():
    try:
        ruta_db = "inventario_nepos.db"
        timestamp = os.path.getmtime(ruta_db)  # Obtiene la fecha de modificación en formato timestamp
        fecha_modificacion = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        return fecha_modificacion
    except Exception as e:
        return f"Error al obtener fecha: {e}"

def cambiar_contraseñas():
    if not solicitar_contraseña("Admin"):
        messagebox.showerror("Error", "Contraseña incorrecta.")
        return
    
    ventana_cambio = tk.Toplevel()
    ventana_cambio.title("Cambiar Contraseñas")
    ventana_cambio.geometry("350x200")
    ventana_cambio.configure(bg="royalblue4")
    
    tk.Label(ventana_cambio, text="Nueva Contraseña General:", bg="royalblue4", fg="white").pack(pady=5)
    entrada_general = tk.Entry(ventana_cambio, show="*")
    entrada_general.pack(pady=5)
    
    tk.Label(ventana_cambio, text="Nueva Contraseña Administrador:", bg="royalblue4", fg="white").pack(pady=5)
    entrada_admin = tk.Entry(ventana_cambio, show="*")
    entrada_admin.pack(pady=5)
    
    # Obtener fecha de modificación del archivo desde Python
    fecha_modificacion = obtener_fecha_modificacion()
    
    tk.Label(ventana_cambio, text=f"Última modificación: {fecha_modificacion}", bg="royalblue4", fg="gold2").pack(pady=5)
    tk.Label(ventana_cambio, text="Para insertar una nueva base de datos, abra DB Browser.", bg="royalblue4", fg="gold2").pack(pady=5)
  
    def guardar_nuevas_contraseñas():
        nueva_general = entrada_general.get()
        nueva_admin = entrada_admin.get()
        if not nueva_general or not nueva_admin:
            messagebox.showwarning("Aviso", "Las contraseñas no pueden estar vacías.")
            return
        try:
            conn = sqlite3.connect('inventario_nepos.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE CONTRASENA SET general=?, admin=?", (nueva_general, nueva_admin))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Contraseñas actualizadas correctamente.")
            ventana_cambio.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo actualizar las contraseñas: {e}")
    
    tk.Button(ventana_cambio, text="Guardar", command=guardar_nuevas_contraseñas, bg="white", fg="black").pack(pady=10)
    ventana_cambio.bind("<Return>", lambda event: guardar_nuevas_contraseñas()) #Comando para que, al dar Enter se guarden los cambios

def verificar_contraseña():
    try:
        conn = sqlite3.connect('inventario_nepos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT general FROM CONTRASENA")
        contraseña_correcta = cursor.fetchone()[0]
        conn.close()

        if entrada_contraseña.get() == contraseña_correcta:
            ventana_login.destroy()
            mostrar_ventana_principal()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta. Intenta de nuevo.")
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"No se pudo verificar la contraseña: {e}")

def solicitar_contraseña(accion):
    password = simpledialog.askstring("Contraseña", f"Ingrese la contraseña para {accion}:", show='*')
    try:
        conn = sqlite3.connect('inventario_nepos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT admin FROM CONTRASENA")
        contraseña_correcta = cursor.fetchone()[0]
        conn.close()
        return password == contraseña_correcta
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"No se pudo verificar la contraseña: {e}")
        return False

def cargar_datos():
    try:
        conn = sqlite3.connect('inventario_nepos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PRODUCTOSN")
        registros = cursor.fetchall()
        actualizar_treeview(registros)
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"No se pudo acceder a la base de datos: {e}")

def actualizar_treeview(datos):
    for row in tree.get_children():
        tree.delete(row)
    for registro in datos:
        tree.insert("", tk.END, values=registro)

def buscar_elemento():
    criterio = entrada_busqueda.get()
    if not criterio:
        messagebox.showwarning("Aviso", "Introduce un criterio de búsqueda.")
        return
    palabras = criterio.split()  # Divide el criterio en palabras individuales
    condiciones = " OR ".join(["(Cod_Prod LIKE ? OR Descripcion LIKE ? OR Observacion LIKE ?)"] * len(palabras))
    valores = []
    for palabra in palabras:
        valores.extend([f'%{palabra}%', f'%{palabra}%', f'%{palabra}%'])
    
    try:
        conn = sqlite3.connect('inventario_nepos.db')
        cursor = conn.cursor()
        consulta = f"SELECT * FROM PRODUCTOSN WHERE {condiciones}"
        cursor.execute(consulta, valores)
        registros = cursor.fetchall()
        conn.close()
        actualizar_treeview(registros)
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"No se pudo buscar el elemento: {e}")

def restablecer_busqueda():
    entrada_busqueda.delete(0, tk.END)
    cargar_datos()

def eliminar_elemento():
    if not solicitar_contraseña("Admin"):
        messagebox.showerror("Error", "Contraseña incorrecta.")
        return
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Selecciona un elemento para eliminar.")
        return
    valores = tree.item(selected_item, 'values')
    cod_prod = valores[0]
    try:
        conn = sqlite3.connect('inventario_nepos.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM PRODUCTOSN WHERE Cod_Prod=?", (cod_prod,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
        cargar_datos()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")
        
def verificar_codigo_producto(codigo):
    try:
        conn = sqlite3.connect('inventario_nepos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM PRODUCTOSN WHERE Cod_Prod = ?", (codigo,))
        existe = cursor.fetchone()
        conn.close()
        return existe is not None  
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"No se pudo verificar el código de producto: {e}")
        return False
    
# Función para obtener el siguiente código de producto consecutivo
def obtener_siguiente_codigo():
    try:
        conn = sqlite3.connect('inventario_nepos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(Cod_Prod) FROM PRODUCTOSN")
        ultimo_codigo = cursor.fetchone()[0]
        conn.close()
        return str(int(ultimo_codigo) + 1) if ultimo_codigo else "1"
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"No se pudo obtener el código de producto: {e}")
        return "1"

def mostrar_ventana_edicion(valores=None):
    ventana_edicion = tk.Toplevel()
    ventana_edicion.title("Editar Producto" if valores else "Añadir Producto")
    ventana_edicion.geometry("280x350")
    ventana_edicion.configure(bg="royalblue4")
    
    campos = ["Cod_Prod", "Descripcion", "Unidad", "Precio_Unit", "Precio_Iva", "Existencia", "Observacion"]
    entradas = []
    
    for i, campo in enumerate(campos):
        tk.Label(ventana_edicion, text=campo, font=("Times", 10, "bold"), fg="white", bg="royalblue4").grid(row=i, column=0, padx=10, pady=5)
        entrada = tk.Entry(ventana_edicion, width=25)
        entrada.grid(row=i, column=1, padx=10, pady=5)
        
        if campo == "Cod_Prod":
            if valores:
                entrada.insert(0, valores[i]) 
                entrada.config(state='disabled') # Deshabilitar edición para productos existentes
            else:
                entrada.insert(0, obtener_siguiente_codigo())  # Si es nuevo, asignar el siguiente código consecutivo
                entrada.config(state='disabled')  # Deshabilitar edición para nuevos productos
        elif valores:
            entrada.insert(0, valores[i])
        
        entradas.append(entrada)
    
    tk.Label(ventana_edicion, text="Aplicar IVA 15%:", bg="royalblue4", fg="gold2", font=("Arial", 9, "bold")).grid(row=7, column=0, columnspan=2, pady=5)
       
    # Botones "Sí" y "No" para actualizar el precio con IVA
    def actualizar_precio_iva(opcion):
        precio_unit = float(entradas[3].get())  # Precio Unitario
        if opcion == "Sí":
            precio_iva = round(precio_unit * 1.15, 2)
        else:
            precio_iva = 0
        entradas[4].delete(0, tk.END)  # Limpiar el campo de Precio_Iva
        entradas[4].insert(0, str(precio_iva))  # Insertar el nuevo valor de Precio_Iva
    
    # Frame para los botones
    frame_botones_iva = tk.Frame(ventana_edicion, bg="royalblue4")
    frame_botones_iva.grid(row=8, column=0, columnspan=2, pady=5)
    
    # Botones "Sí" y "No"
    boton_si = tk.Button(frame_botones_iva, text="Sí", command=lambda: actualizar_precio_iva("Sí"), bg="lightgreen", width=10)
    boton_si.pack(side=tk.LEFT, padx=20)  # Alinear a la izquierda con espacio a la derecha

    boton_no = tk.Button(frame_botones_iva, text="No", command=lambda: actualizar_precio_iva("No"), bg="salmon", width=10)
    boton_no.pack(side=tk.LEFT, padx=20)  # Alinear a la izquierda con espacio a la izquierda
     
    def guardar_datos():
        nuevos_valores = [entrada.get() for entrada in entradas]
        cod_prod = nuevos_valores[0]  # El primer valor es el código de producto
        
        # Si estamos editando un producto, comprobamos si el código ha cambiado
        if valores and cod_prod != valores[0]:  # Si el código cambió
            # Verificamos si el código de producto ya existe en la base de datos
            if verificar_codigo_producto(cod_prod):
                messagebox.showerror("Error", f"Ya existe un producto con el código {cod_prod}. Ingresa un código diferente.")
                return

        try:
            conn = sqlite3.connect('inventario_nepos.db')
            cursor = conn.cursor()
            if valores:  # Si valores no es None, estamos actualizando un producto
                cursor.execute("""
                    UPDATE PRODUCTOSN SET Descripcion=?, Unidad=?, Precio_Unit=?, Precio_Iva=?, Existencia=?, Observacion=? WHERE Cod_Prod=?
                """, (nuevos_valores[1], nuevos_valores[2], nuevos_valores[3], nuevos_valores[4], nuevos_valores[5], nuevos_valores[6], cod_prod))
            else:  # Si valores es None, estamos añadiendo un nuevo producto
                cursor.execute("""
                    INSERT INTO PRODUCTOSN (Cod_Prod, Descripcion, Unidad, Precio_Unit, Precio_Iva, Existencia, Observacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, nuevos_valores)
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Producto actualizado correctamente." if valores else "Producto añadido correctamente.")
            cargar_datos()
            ventana_edicion.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo actualizar el producto: {e}")
    
    tk.Button(ventana_edicion, text="Guardar", command=guardar_datos, bg="white", fg="black").grid(row=10, column=0, columnspan=2, pady=10)
    ventana_edicion.bind("<Return>", lambda event: guardar_datos())
    
def editar_elemento():
    if not solicitar_contraseña("Admin"):
        messagebox.showerror("Error", "Contraseña incorrecta.")
        return
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Selecciona un elemento para editar.")
        return
    valores = tree.item(selected_item, 'values')
    mostrar_ventana_edicion(valores)

def agregar_elemento():
    if not solicitar_contraseña("Admin"):
        messagebox.showerror("Error", "Contraseña incorrecta.")
        return
    mostrar_ventana_edicion()

# Edición ventana que contiene la base de datos
def mostrar_ventana_principal():
    global tree, entrada_busqueda
    ventana = tk.Tk()
    ventana.title("Inventario de Materiales NEPOS ENERGY S.A.S.")
    ventana.geometry("1000x650")
    ventana.configure(bg="royalblue4")
        
    frame_busqueda = tk.Frame(ventana, bg="royalblue4")
    frame_busqueda.pack(fill=tk.X, padx=10, pady=5)
    
    tk.Label(frame_busqueda, text="Buscar:", bg="royalblue4", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
    entrada_busqueda = tk.Entry(frame_busqueda, width=30)
    entrada_busqueda.pack(side=tk.LEFT)
    tk.Button(frame_busqueda, text="Buscar", command=buscar_elemento).pack(side=tk.LEFT)
    entrada_busqueda.bind("<Return>", lambda event: buscar_elemento()) # Comando para dar ENTER y buscar
    tk.Button(frame_busqueda, text="Restablecer", command=restablecer_busqueda).pack(side=tk.LEFT)
    
    # FRAME PARA EL TREEVIEW Y SCROLLBAR
    frame_tabla = tk.Frame(ventana)
    frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Scrollbar Vertical
    scrollbar_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
    
    # Crear Treeview con la scrollbar
    tree = ttk.Treeview(frame_tabla, columns=("Cod_Prod", "Descripcion", "Unidad", "Precio_Unit", "Precio_Iva", "Existencia", "Observacion"), 
                         show="headings", yscrollcommand=scrollbar_y.set)
    
    # Configurar la scrollbar para que funcione con el Treeview
    scrollbar_y.config(command=tree.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)  # Ubicar la barra a la derecha
    
    # Configurar encabezados y tamaño de columnas
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=120)  # Ajustar tamaño de columnas

    tree.pack(fill=tk.BOTH, expand=True)

    # BOTONES DE ABAJO - VENTANA PRINCIPAL (BASE DE DATOS)
    btn_frame = tk.Frame(ventana, bg="royalblue4")
    btn_frame.pack(fill=tk.X, pady=5)
    
    tk.Button(btn_frame, text="Editar Seleccionado", command=editar_elemento).pack(side=tk.LEFT)
    tk.Button(btn_frame, text="Añadir Producto", command=agregar_elemento).pack(side=tk.LEFT)
    tk.Button(btn_frame, text="Eliminar Producto", command=eliminar_elemento, bg="coral3", fg="white").pack(side=tk.LEFT)
    tk.Button(btn_frame, text="Configuración", command=cambiar_contraseñas, bg="gold2").pack(side=tk.LEFT)
       
    cargar_datos()
    ventana.mainloop()
    
def abrir_sitio_web():
    webbrowser.open("http://www.neposenergy.com")

# Ventana de inicio de sesión con información de la empresa
ventana_login = tk.Tk()
ventana_login.title("Iniciar sesión")
ventana_login.geometry("600x480")
ventana_login.configure(bg="royalblue4")

tk.Label(ventana_login, text="NEPOS ENERGY S.A.S.", font=("Times", 20, "bold"), fg="light goldenrod", bg="royalblue4").pack(pady=7)

# Cargar imagen
ruta_imagen = "LOGON.png"  # Nombre de la imágen en formato .png
imagen = Image.open(ruta_imagen)
imagen = imagen.resize((90, 90))  # Ajusta el tamaño de la imagen
imagen_tk = ImageTk.PhotoImage(imagen)

# Mostrar imagen en la ventana de inicio de sesión
label_imagen = tk.Label(ventana_login, image=imagen_tk, bg="royalblue4")
label_imagen.pack(pady=10)

tk.Label(ventana_login, text="Inventario de Materiales", bg="royalblue4", fg="gray85", font=("Times", 18, "bold")).pack()

# Espacio para Ingreso de contraseña
tk.Label(ventana_login, text="Introduce la contraseña:", bg="royalblue4", fg="gray85").pack(pady=10)
entrada_contraseña = tk.Entry(ventana_login, show="*")
entrada_contraseña.pack(pady=10)

# Vincular la tecla "Enter" para verificar la contraseña
entrada_contraseña.bind("<Return>", lambda event: verificar_contraseña())

tk.Button(ventana_login, text="Ingresar", command=verificar_contraseña).pack(pady=15)

tk.Label(ventana_login, text="Dirección: Juan Severino E8-14 y Diego de Almagro, Quito", bg="royalblue4", font=("Times", 11), fg="gray85").pack()
tk.Label(ventana_login, text="Teléfonos: +593(0)958818767 / +593(0)979000873 ", bg="royalblue4", font=("Times", 11), fg="gray85").pack()
tk.Label(ventana_login, text="Correo: proyectos@neposenergy.com", bg="royalblue4", font=("Times", 11), fg="gray85").pack()

# Hipervinculo a la página de NEPOS
link_label = tk.Label(ventana_login, text="Sitio Web: www.neposenergy.com", bg="royalblue4", font=("Times", 11, "underline"), fg="light goldenrod", cursor="hand2")
link_label.pack()
link_label.bind("<Button-1>", lambda e: abrir_sitio_web())

tk.Label(ventana_login, text="Copyright 2025 - Todos los derechos reservados", bg="royalblue4", font=("Times", 11), fg="gray85").pack()

ventana_login.mainloop()