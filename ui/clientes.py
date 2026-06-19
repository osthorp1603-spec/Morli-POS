import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import sys

class ClientesVentana(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.config(bg="#f5f7fa")

        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        self.db_path = os.path.join(base_path, "clientes.db")

        self.conectar_bd()
        self.crear_tablas()
        self.agregar_columnas_si_faltan()
        self.interfaz()

    def conectar_bd(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def crear_tablas(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes_registrados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            telefono TEXT,
            correo TEXT,
            observacion TEXT,
            fecha_registro TEXT
        )""")
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes_temporales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            telefono TEXT,
            cantidad_items INTEGER,
            observacion TEXT,
            fecha_entrega TEXT,
            fecha_salida TEXT
        )""")
        self.conn.commit()

    def agregar_columnas_si_faltan(self):
        self.cursor.execute("PRAGMA table_info(clientes_registrados)")
        columnas = [col[1] for col in self.cursor.fetchall()]
        if "fecha_cumple" not in columnas:
            self.cursor.execute("ALTER TABLE clientes_registrados ADD COLUMN fecha_cumple TEXT")
        if "factura_electronica" not in columnas:
            self.cursor.execute("ALTER TABLE clientes_registrados ADD COLUMN factura_electronica TEXT")
        self.conn.commit()

    def interfaz(self):
        self.master.geometry("1150x700")
        tk.Label(self, text="Gestión de Clientes", font=("Arial", 20, "bold"), bg="#f5f7fa").pack(pady=10)

        frame_form = tk.Frame(self, bg="#f5f7fa")
        frame_form.pack(pady=5)

        tk.Label(frame_form, text="Nombre completo:", bg="#f5f7fa").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nombre = tk.Entry(frame_form, width=30)
        self.entry_nombre.grid(row=0, column=1)

        tk.Label(frame_form, text="Teléfono:", bg="#f5f7fa").grid(row=1, column=0, padx=5, pady=5)
        self.entry_telefono = tk.Entry(frame_form, width=30)
        self.entry_telefono.grid(row=1, column=1)

        tk.Label(frame_form, text="Correo:", bg="#f5f7fa").grid(row=2, column=0, padx=5, pady=5)
        self.entry_correo = tk.Entry(frame_form, width=30)
        self.entry_correo.grid(row=2, column=1)

        tk.Label(frame_form, text="Observación:", bg="#f5f7fa").grid(row=3, column=0, padx=5, pady=5)
        self.entry_observacion = tk.Entry(frame_form, width=30)
        self.entry_observacion.grid(row=3, column=1)

        tk.Label(frame_form, text="Fecha cumpleaños (AAAA-MM-DD):", bg="#f5f7fa").grid(row=4, column=0, padx=5, pady=5)
        self.entry_cumple = tk.Entry(frame_form, width=30)
        self.entry_cumple.grid(row=4, column=1)

        tk.Label(frame_form, text="Factura electrónica:", bg="#f5f7fa").grid(row=5, column=0, padx=5, pady=5)
        self.entry_factura = tk.Entry(frame_form, width=30)
        self.entry_factura.grid(row=5, column=1)

        frame_botones = tk.Frame(self, bg="#f5f7fa")
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Registrar Cliente", command=self.registrar_cliente, bg="green", fg="white").grid(row=0, column=0, padx=10)
        tk.Button(frame_botones, text="Dejó Empaque", command=self.abrir_empaque, bg="orange", fg="white").grid(row=0, column=1, padx=10)
        tk.Button(frame_botones, text="Eliminar Cliente", command=self.eliminar_cliente, bg="red", fg="white").grid(row=0, column=2, padx=10)

        columnas = ("Nombre", "Teléfono", "Correo", "Observación", "Cumpleaños", "Factura", "Fecha Registro")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings")
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150)
        self.tree.pack(pady=10, fill="both", expand=True)

        self.cargar_clientes()

    def registrar_cliente(self):
        nombre = self.entry_nombre.get().strip()
        telefono = self.entry_telefono.get().strip()
        correo = self.entry_correo.get().strip()
        observacion = self.entry_observacion.get().strip()
        cumple = self.entry_cumple.get().strip()
        factura = self.entry_factura.get().strip()
        fecha = datetime.now().strftime("%Y-%m-%d")

        if not nombre:
            messagebox.showerror("Error", "Nombre completo es obligatorio.")
            return

        self.cursor.execute("""
        INSERT INTO clientes_registrados 
        (nombre_completo, telefono, correo, observacion, fecha_cumple, factura_electronica, fecha_registro)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (nombre, telefono, correo, observacion, cumple, factura, fecha))
        self.conn.commit()
        self.cargar_clientes()

        self.entry_nombre.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_correo.delete(0, tk.END)
        self.entry_observacion.delete(0, tk.END)
        self.entry_cumple.delete(0, tk.END)
        self.entry_factura.delete(0, tk.END)

    def cargar_clientes(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.cursor.execute("""
        SELECT nombre_completo, telefono, correo, observacion, fecha_cumple, factura_electronica, fecha_registro 
        FROM clientes_registrados ORDER BY id DESC
        """)
        for cliente in self.cursor.fetchall():
            self.tree.insert("", "end", values=cliente)

    def eliminar_cliente(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un cliente para eliminar.")
            return

        confirmacion = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este cliente?")
        if not confirmacion:
            return

        item = self.tree.item(seleccionado)
        nombre = item["values"][0]
        fecha = item["values"][-1]

        self.cursor.execute("""
        DELETE FROM clientes_registrados
        WHERE nombre_completo = ? AND fecha_registro = ?
        """, (nombre, fecha))
        self.conn.commit()

        self.cargar_clientes()
        messagebox.showinfo("Eliminado", "Cliente eliminado correctamente.")

    def abrir_empaque(self):
        ventana = tk.Toplevel(self)
        ventana.title("Registro de Entrega Temporal")
        ventana.geometry("950x550")
        ventana.config(bg="#f5f7fa")

        frame = tk.Frame(ventana, bg="#f5f7fa")
        frame.pack(pady=10)

        tk.Label(frame, text="Nombre completo:", bg="#f5f7fa").grid(row=0, column=0, padx=5, pady=5)
        entry_nombre = tk.Entry(frame, width=30)
        entry_nombre.grid(row=0, column=1)

        tk.Label(frame, text="Teléfono:", bg="#f5f7fa").grid(row=1, column=0, padx=5, pady=5)
        entry_telefono = tk.Entry(frame, width=30)
        entry_telefono.grid(row=1, column=1)

        tk.Label(frame, text="Cantidad de artículos:", bg="#f5f7fa").grid(row=2, column=0, padx=5, pady=5)
        entry_cantidad = tk.Entry(frame, width=30)
        entry_cantidad.grid(row=2, column=1)

        tk.Label(frame, text="Observación:", bg="#f5f7fa").grid(row=3, column=0, padx=5, pady=5)
        entry_observacion = tk.Entry(frame, width=30)
        entry_observacion.grid(row=3, column=1)

        def guardar():
            nombre = entry_nombre.get().strip()
            telefono = entry_telefono.get().strip()
            cantidad = entry_cantidad.get().strip()
            observacion = entry_observacion.get().strip()
            fecha_entrega = datetime.now().strftime("%Y-%m-%d")

            if not nombre or not cantidad:
                messagebox.showerror("Error", "Nombre y cantidad son obligatorios.")
                return

            self.cursor.execute("""
            INSERT INTO clientes_temporales 
            (nombre_completo, telefono, cantidad_items, observacion, fecha_entrega, fecha_salida)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (nombre, telefono, cantidad, observacion, fecha_entrega, "Pendiente"))
            self.conn.commit()
            messagebox.showinfo("Guardado", "Registro almacenado correctamente.")
            entry_nombre.delete(0, tk.END)
            entry_telefono.delete(0, tk.END)
            entry_cantidad.delete(0, tk.END)
            entry_observacion.delete(0, tk.END)
            cargar_tabla()

        tk.Button(frame, text="Guardar", command=guardar, bg="green", fg="white").grid(row=4, column=0, columnspan=2, pady=10)

        columnas = ("ID", "Nombre", "Teléfono", "Cantidad", "Observación", "Entrega", "Estado")
        tree = ttk.Treeview(ventana, columns=columnas, show="headings")
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
        tree.pack(padx=10, pady=10, fill="both", expand=True)

        def cargar_tabla():
            for row in tree.get_children():
                tree.delete(row)
            self.cursor.execute("""
                SELECT id, nombre_completo, telefono, cantidad_items, observacion, fecha_entrega, fecha_salida 
                FROM clientes_temporales ORDER BY id DESC
            """)
            for fila in self.cursor.fetchall():
                tree.insert("", "end", values=fila)

        def marcar_ok():
            seleccionado = tree.selection()
            if not seleccionado:
                messagebox.showwarning("Atención", "Seleccione una fila.")
                return
            item = tree.item(seleccionado)
            id_cliente = item["values"][0]
            estado_actual = item["values"][-1]
            if estado_actual == "OK":
                messagebox.showinfo("Info", "Ya está marcado como OK.")
                return
            self.cursor.execute("UPDATE clientes_temporales SET fecha_salida = ? WHERE id = ?", ("OK", id_cliente))
            self.conn.commit()
            cargar_tabla()
            messagebox.showinfo("Actualizado", "Estado actualizado a OK.")

        tk.Button(ventana, text="Marcar como OK", command=marcar_ok, bg="blue", fg="white").pack(pady=5)

        cargar_tabla()
