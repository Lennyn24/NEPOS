import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

def solicitar_contraseña(callback):
    ventana_pass = tk.Toplevel()
    ventana_pass.title("Verificar contraseña")
    ventana_pass.geometry("300x150")
    tk.Label(ventana_pass, text="Introduce la contraseña:").pack(pady=10)
    entrada_pass = tk.Entry(ventana_pass, show="*")
    entrada_pass.pack(pady=5)
    
    def validar():
        if entrada_pass.get() == "nepos123":
            ventana_pass.destroy()
            callback()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta.")
            ventana_pass.destroy()
    
    tk.Button(ventana_pass, text="Ingresar", command=validar).pack(pady=10)
    ventana_pass.mainloop()

def cargar_datos():
    try:
        conn = sqlite3.connect('inventario_nepos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PRODUCTOS")
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
    try:
        conn = sqlite3.connect('inventario_nepos.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM PRODUCTOS 
            WHERE Cod_Prod LIKE ? OR Descripcion LIKE ? OR Observacion LIKE ?
        """, (f'%{criterio}%', f'%{criterio}%', f'%{criterio}%'))
        registros = cursor.fetchall()
        conn.close()
        actualizar_treeview(registros)
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"No se pudo buscar el elemento: {e}")

def mostrar_ventana_edicion(valores=None):
    ventana_edicion = tk.Toplevel()
    ventana_edicion.title("Editar Producto" if valores else "Añadir Producto")
    ventana_edicion.geometry("400x400")
    ventana_edicion.configure(bg="lightblue")
    
    campos = ["Cod_Prod", "Descripcion", "Unidad", "Precio_Unit", "Precio_Iva", "Paga_Impuesto", "Existencia", "Observacion"]
    entradas = []
    
    for i, campo in enumerate(campos):
        tk.Label(ventana_edicion, text=campo, font=("Arial", 10, "bold"), bg="lightblue").grid(row=i, column=0, padx=10, pady=5)
        entrada = tk.Entry(ventana_edicion)
        entrada.grid(row=i, column=1, padx=10, pady=5)
        if valores:
            entrada.insert(0, valores[i])
        entradas.append(entrada)
    
    def guardar_datos():
        nuevos_valores = [entrada.get() for entrada in entradas]
        try:
            conn = sqlite3.connect('inventario_nepos.db')
            cursor = conn.cursor()
            if valores:
                cursor.execute("""
                    UPDATE PRODUCTOS SET Descripcion=?, Unidad=?, Precio_Unit=?, Precio_Iva=?, Paga_Impuesto=?, Existencia=?, Observacion=? WHERE Cod_Prod=?
                """, (nuevos_valores[1], nuevos_valores[2], nuevos_valores[3], nuevos_valores[4], nuevos_valores[5], nuevos_valores[6], nuevos_valores[7], nuevos_valores[0]))
            else:
                cursor.execute("""
                    INSERT INTO PRODUCTOS (Cod_Prod, Descripcion, Unidad, Precio_Unit, Precio_Iva, Paga_Impuesto, Existencia, Observacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, nuevos_valores)
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Producto actualizado correctamente." if valores else "Producto añadido correctamente.")
            cargar_datos()
            ventana_edicion.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo actualizar el producto: {e}")
    
    tk.Button(ventana_edicion, text="Guardar", command=guardar_datos, bg="green", fg="white").grid(row=len(campos), column=0, columnspan=2, pady=10)

def editar_elemento():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Selecciona un elemento para editar.")
        return
    valores = tree.item(selected_item, 'values')
    solicitar_contraseña(lambda: mostrar_ventana_edicion(valores))

def agregar_elemento():
    solicitar_contraseña(mostrar_ventana_edicion)

def eliminar_elemento():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Selecciona un elemento para eliminar.")
        return
    cod_prod = tree.item(selected_item, 'values')[0]
    respuesta = messagebox.askyesno("Eliminar Producto", f"¿Estás seguro de que deseas eliminar el producto con código {cod_prod}?")
    if respuesta:
        try:
            conn = sqlite3.connect('inventario_nepos.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM PRODUCTOS WHERE Cod_Prod=?", (cod_prod,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            cargar_datos()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")

def mostrar_ventana_principal():
    global tree, entrada_busqueda
    ventana = tk.Tk()
    ventana.title("Visualizador de Base de Datos SQLite")
    ventana.geometry("900x550")
    
    frame_busqueda = tk.Frame(ventana)
    frame_busqueda.pack(fill=tk.X, padx=10, pady=5)
    tk.Label(frame_busqueda, text="Buscar:").pack(side=tk.LEFT)
    entrada_busqueda = tk.Entry(frame_busqueda)
    entrada_busqueda.pack(side=tk.LEFT)
    tk.Button(frame_busqueda, text="Buscar", command=buscar_elemento).pack(side=tk.LEFT)
    tk.Button(frame_busqueda, text="Restablecer", command=cargar_datos).pack(side=tk.LEFT)
    
    frame = tk.Frame(ventana)
    frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
    
    global tree
    tree = ttk.Treeview(frame, columns=("Cod_Prod", "Descripcion", "Unidad", "Precio_Unit", "Precio_Iva", "Paga_Impuesto", "Existencia", "Observacion"), show="headings")
    for col in ["Cod_Prod", "Descripcion", "Unidad", "Precio_Unit", "Precio_Iva", "Paga_Impuesto", "Existencia", "Observacion"]:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill=tk.BOTH, expand=True)
    
    cargar_datos()
    
    btn_frame = tk.Frame(ventana)
    btn_frame.pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text="Editar Seleccionado", command=editar_elemento).pack(side=tk.LEFT)
    tk.Button(btn_frame, text="Añadir Producto", command=agregar_elemento).pack(side=tk.LEFT)
    tk.Button(btn_frame, text="Eliminar Producto", command=eliminar_elemento).pack(side=tk.LEFT)

    ventana.mainloop()

# Mostrar directamente la ventana principal sin login
mostrar_ventana_principal()
