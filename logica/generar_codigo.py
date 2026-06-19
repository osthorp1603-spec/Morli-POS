import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.graphics.barcode import code128
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import sys
import win32print
import subprocess
import re

# Detectar base_path compatible con .py y .exe
try:
    base_path = sys._MEIPASS
except AttributeError:
    base_path = os.path.abspath(".")

# Crear carpeta si no existe
if not os.path.exists("codigos"):
    os.makedirs("codigos")

# Conexiones
conn_codigos = sqlite3.connect(os.path.join(base_path, "codigos.db"))
cursor_codigos = conn_codigos.cursor()
cursor_codigos.execute("""
    CREATE TABLE IF NOT EXISTS codigos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE
    )
""")
conn_codigos.commit()

conn_inv = sqlite3.connect(os.path.join(base_path, "database.db"))
cursor_inv = conn_inv.cursor()

# Ajustar automáticamente el ancho del código de barras
def crear_codigo_barras(codigo, altura_mm=11.5, ancho_etiqueta_mm=30):
    max_width = ancho_etiqueta_mm * mm
    bar_width = 1.0
    while bar_width > 0.3:
        barcode = code128.Code128(codigo, barHeight=altura_mm * mm, barWidth=bar_width, humanReadable=False)
        if barcode.width <= max_width:
            return barcode
        bar_width -= 0.05
    return code128.Code128(codigo, barHeight=altura_mm * mm, barWidth=0.3, humanReadable=False)

# Generar PDF (barra con código, debajo nombre y precio)
def generar_pdf(codigo, nombre_producto, precio):
    etiqueta_ancho = 30 * mm
    etiqueta_alto = 20 * mm
    ancho_total = 60 * mm
    margen_izquierdo = 2 * mm

    nombre_limpio = re.sub(r'[^a-zA-Z0-9_\-]', '', nombre_producto.strip().replace(' ', '_'))[:30]
    nombre_archivo = os.path.join("codigos", f"{nombre_limpio}.pdf")
    c = canvas.Canvas(nombre_archivo, pagesize=(ancho_total, etiqueta_alto))

    y_barra = 6 * mm
    y_nombre = 2.5 * mm
    y_precio = 0.5 * mm

    # Izquierda
    barcode1 = crear_codigo_barras(codigo)
    x_izq = margen_izquierdo + (30 * mm - barcode1.width) / 2
    barcode1.drawOn(c, x_izq, y_barra)
    c.setFont("Helvetica", 5.8)
    c.drawCentredString(margen_izquierdo + 15 * mm, y_nombre, nombre_producto[:22])
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(margen_izquierdo + 15 * mm, y_precio, f"${precio:,.0f}")

    # Derecha
    barcode2 = crear_codigo_barras(codigo)
    x_der = 30 * mm + (30 * mm - barcode2.width) / 2
    barcode2.drawOn(c, x_der, y_barra)
    c.setFont("Helvetica", 5.8)
    c.drawCentredString(30 * mm + 15 * mm, y_nombre, nombre_producto[:22])
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(30 * mm + 15 * mm, y_precio, f"${precio:,.0f}")

    c.save()

    try:
        if sys.platform.startswith("win"):
            os.startfile(nombre_archivo)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", nombre_archivo])
        else:
            subprocess.Popen(["xdg-open", nombre_archivo])
    except Exception as e:
        messagebox.showinfo("PDF generado", f"Etiqueta guardada como:\n{nombre_limpio}.pdf en carpeta 'codigos'\n(No se pudo abrir automáticamente).\n{e}")

# Interfaz completa
def abrir_ventana_generar(parent):
    ventana = tk.Toplevel(parent)
    ventana.title("Gestión de Códigos de Barras")
    ventana.geometry("850x500")
    ventana.config(bg="white")

    tk.Label(ventana, text="Escribe nuevo código:", bg="white").place(x=20, y=10)
    entry_codigo = tk.Entry(ventana)
    entry_codigo.place(x=160, y=10, width=200)

    tk.Label(ventana, text="Buscar producto:", bg="white").place(x=400, y=10)
    entry_buscar = tk.Entry(ventana)
    entry_buscar.place(x=520, y=10, width=200)

    tree = ttk.Treeview(ventana, columns=("ID", "Nombre", "Proveedor", "Precio", "Stock", "Codigo"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Proveedor", text="Proveedor")
    tree.heading("Precio", text="Precio")
    tree.heading("Stock", text="Stock")
    tree.heading("Codigo", text="Código de Barras")
    tree.place(x=20, y=50, width=800, height=360)

    # Scrollbars para Treeview
    scroll_y = tk.Scrollbar(ventana, orient="vertical", command=tree.yview)
    scroll_y.place(x=820, y=50, height=360)

    scroll_x = tk.Scrollbar(ventana, orient="horizontal", command=tree.xview)
    scroll_x.place(x=20, y=410, width=800)

    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)


    def cargar_productos(filtro=""):
        for i in tree.get_children():
            tree.delete(i)
        if filtro:
            cursor_inv.execute("SELECT id, nombre, proveedor, precio, stock, codigo_barras FROM inventario WHERE nombre LIKE ?", (f"%{filtro}%",))
        else:
            cursor_inv.execute("SELECT id, nombre, proveedor, precio, stock, codigo_barras FROM inventario")
        for fila in cursor_inv.fetchall():
            tree.insert("", "end", values=fila)

    def al_seleccionar(event):
        item = tree.focus()
        if item:
            datos = tree.item(item, "values")
            entry_codigo.delete(0, tk.END)
            if datos and datos[5] and datos[5] != "None":
                entry_codigo.insert(0, datos[5])

    tree.bind("<<TreeviewSelect>>", al_seleccionar)
    cargar_productos()
    entry_buscar.bind("<KeyRelease>", lambda e: cargar_productos(entry_buscar.get()))

    def asignar_e_imprimir():
        codigo = entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Advertencia", "Escribe un código.")
            return
        item = tree.focus()
        if not item:
            messagebox.showwarning("Advertencia", "Selecciona un producto del listado.")
            return
        datos = tree.item(item, "values")
        id_producto, nombre, proveedor, precio, stock, codigo_actual = datos

        # Verificar si el código ya está asignado a otro producto
        cursor_inv.execute("SELECT id FROM inventario WHERE codigo_barras = ?", (codigo,))
        resultado = cursor_inv.fetchone()
        if resultado and str(resultado[0]) != str(id_producto):
            messagebox.showerror("Error", f"El código '{codigo}' ya está asignado a otro producto.")
            return

        # Insertar en codigos.db solo si no existe
        cursor_codigos.execute("SELECT COUNT(*) FROM codigos WHERE codigo = ?", (codigo,))
        if cursor_codigos.fetchone()[0] == 0:
            cursor_codigos.execute("INSERT INTO codigos (codigo) VALUES (?)", (codigo,))
            conn_codigos.commit()

        # Actualizar inventario con nuevo código
        cursor_inv.execute("UPDATE inventario SET codigo_barras = ? WHERE id = ?", (codigo, id_producto))
        conn_inv.commit()

        generar_pdf(codigo, nombre, float(precio))
        messagebox.showinfo("Éxito", f"Código '{codigo}' asignado correctamente a '{nombre}'.")

        entry_codigo.delete(0, tk.END)
        cargar_productos(entry_buscar.get())

    def solo_imprimir():
        item = tree.focus()
        if not item:
            messagebox.showwarning("Advertencia", "Selecciona un producto del listado.")
            return
        datos = tree.item(item, "values")
        id_producto, nombre, proveedor, precio, stock, codigo_actual = datos

        if not codigo_actual or codigo_actual == "None":
            messagebox.showwarning("Advertencia", "Este producto no tiene código asignado.")
            return

        generar_pdf(codigo_actual, nombre, float(precio) if precio else 0)
        messagebox.showinfo("Impresión", f"Etiqueta del código '{codigo_actual}' generada.")

    # Botón Asignar e Imprimir
    tk.Button(
        ventana,
        text="Asignar e Imprimir",
        bg="dark green",
        fg="white",
        font=("Arial", 11, "bold"),
        command=asignar_e_imprimir
    ).place(x=340, y=430, width=180, height=40)

    # Botón Solo Imprimir
    tk.Button(
        ventana,
        text="Solo Imprimir",
        bg="blue",
        fg="white",
        font=("Arial", 11, "bold"),
        command=solo_imprimir
    ).place(x=540, y=430, width=180, height=40)

    ventana.transient(parent)
    ventana.grab_set()
    ventana.focus_set()
    ventana.lift()
