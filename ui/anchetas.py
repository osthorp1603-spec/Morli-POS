import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os

class Anchetas(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Crear Ancheta")
        self.geometry("1000x650")
        self.config(bg="white")

        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        self.db_name = os.path.join(base_path, "database.db")

        self.productos_añadidos = []
        self.lector_habilitado = True

        self.crear_tablas_si_no_existen()

        # Entradas
        tk.Label(self, text="Buscar producto:", bg="white").place(x=20, y=20)
        self.entry_busqueda = tk.Entry(self, width=30)
        self.entry_busqueda.place(x=150, y=20)
        self.entry_busqueda.bind("<KeyRelease>", self.filtrar_productos)

        tk.Label(self, text="Nombre de la Ancheta:", bg="white").place(x=20, y=60)
        self.entry_nombre = tk.Entry(self, width=30)
        self.entry_nombre.place(x=180, y=60)

        tk.Label(self, text="Precio de Venta:", bg="white").place(x=20, y=100)
        self.entry_precio = tk.Entry(self, width=15)
        self.entry_precio.place(x=180, y=100)

        tk.Label(self, text="Proveedor:", bg="white").place(x=400, y=60)
        self.entry_proveedor = tk.Entry(self, width=20)
        self.entry_proveedor.insert(0, "Morli")
        self.entry_proveedor.place(x=500, y=60)

        tk.Label(self, text="Tipo Producto:", bg="white").place(x=400, y=100)
        self.entry_tipo = tk.Entry(self, width=20)
        self.entry_tipo.insert(0, "decoracion")
        self.entry_tipo.place(x=500, y=100)

        # Treeview de productos
        tk.Label(self, text="Seleccionar productos:", bg="white").place(x=20, y=140)
        frame_tree = tk.Frame(self)
        frame_tree.place(x=20, y=170, width=700, height=200)
        self.tree_inventario = ttk.Treeview(frame_tree, columns=("ID", "Nombre", "Stock", "Precio"), show="headings", height=8)
        self.tree_inventario.pack(side="left", fill="both", expand=True)

        scroll_y = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree_inventario.yview)
        scroll_y.pack(side="right", fill="y")
        self.tree_inventario.configure(yscrollcommand=scroll_y.set)

        for col in ("ID", "Nombre", "Stock", "Precio"):
            self.tree_inventario.heading(col, text=col)
            self.tree_inventario.column(col, width=120)

        self.cargar_productos()

        tk.Label(self, text="Cantidad:", bg="white").place(x=740, y=170)
        self.entry_cantidad = tk.Entry(self, width=5)
        self.entry_cantidad.place(x=810, y=170)

        btn_agregar = tk.Button(self, text="Agregar", command=self.agregar_producto)
        btn_agregar.place(x=870, y=165)

        # Treeview de añadidos
        self.tree_añadidos = ttk.Treeview(self, columns=("Nombre", "Cantidad", "Precio"), show="headings", height=8)
        self.tree_añadidos.place(x=20, y=390)
        for col in ("Nombre", "Cantidad", "Precio"):
            self.tree_añadidos.heading(col, text=col)
            self.tree_añadidos.column(col, width=200)

        # Etiquetas de costos
        self.label_costo_total = tk.Label(self, text="Precio Total: $0", bg="white", font=("Arial", 10, "bold"))
        self.label_costo_total.place(x=20, y=580)

        self.label_costo_real = tk.Label(self, text="Costo real de componentes: $0", bg="white", font=("Arial", 10))
        self.label_costo_real.place(x=20, y=600)

        btn_guardar = tk.Button(self, text="Guardar Ancheta", command=self.guardar_ancheta, bg="#B0E57C")
        btn_guardar.place(x=850, y=570)

        # Escáner oculto
        self.entry_codigo_oculto = tk.Entry(self)
        self.entry_codigo_oculto.place(x=-100, y=-100)
        self.entry_codigo_oculto.bind("<Return>", self.procesar_codigo_barras)
        self.entry_codigo_oculto.focus_set()

        self.after(1000, self.reestablecer_foco_lector)

    def crear_tablas_si_no_existen(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anchetas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                precio REAL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ancheta_detalle (
                id_ancheta INTEGER,
                id_producto INTEGER,
                cantidad INTEGER,
                FOREIGN KEY (id_ancheta) REFERENCES anchetas(id),
                FOREIGN KEY (id_producto) REFERENCES inventario(id)
            )
        """)
        conn.commit()
        conn.close()

    def cargar_productos(self, filtro=""):
        self.tree_inventario.delete(*self.tree_inventario.get_children())
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        if filtro:
            cursor.execute("SELECT id, nombre, stock, precio FROM inventario WHERE es_servicio = 0 AND nombre LIKE ?", (f"%{filtro}%",))
        else:
            cursor.execute("SELECT id, nombre, stock, precio FROM inventario WHERE es_servicio = 0")
        for row in cursor.fetchall():
            self.tree_inventario.insert("", tk.END, values=row)
        conn.close()

    def filtrar_productos(self, event):
        texto = self.entry_busqueda.get().strip()
        self.cargar_productos(texto)

    def agregar_producto(self):
        selected = self.tree_inventario.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un producto.")
            return
        try:
            cantidad = int(self.entry_cantidad.get())
        except:
            messagebox.showerror("Error", "Cantidad inválida.")
            return

        item = self.tree_inventario.item(selected)
        id_producto, nombre, stock, precio = item['values']
        if cantidad > stock:
            messagebox.showerror("Error", "Cantidad supera stock disponible.")
            return

        for i, (id_p, nom, cant, prec) in enumerate(self.productos_añadidos):
            if id_p == id_producto:
                self.productos_añadidos[i] = (id_p, nom, cant + cantidad, prec)
                self.refrescar_añadidos()
                self.actualizar_costo_total()
                return

        self.productos_añadidos.append((id_producto, nombre, cantidad, float(precio)))
        self.refrescar_añadidos()
        self.actualizar_costo_total()

    def refrescar_añadidos(self):
        self.tree_añadidos.delete(*self.tree_añadidos.get_children())
        for _, nombre, cantidad, precio in self.productos_añadidos:
            self.tree_añadidos.insert("", tk.END, values=(nombre, cantidad, f"${precio}"))

    def actualizar_costo_total(self):
        total_venta = sum(int(cant) * float(precio) for _, _, cant, precio in self.productos_añadidos)
        self.label_costo_total.config(text=f"Precio Total (venta): ${total_venta:,.2f}")

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        total_costo = 0
        for id_producto, _, cantidad, _ in self.productos_añadidos:
            cursor.execute("SELECT costo FROM inventario WHERE id = ?", (id_producto,))
            resultado = cursor.fetchone()
            if resultado:
                costo_unitario = resultado[0]
                total_costo += int(cantidad) * float(costo_unitario)
        conn.close()

        self.label_costo_real.config(text=f"Costo real de componentes: ${total_costo:,.2f}")

    def procesar_codigo_barras(self, event):
        codigo = self.entry_codigo_oculto.get().strip()
        if not codigo:
            return
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, stock, precio FROM inventario WHERE codigo_barras = ?", (codigo,))
        resultado = cursor.fetchone()
        conn.close()

        if not resultado:
            messagebox.showerror("No encontrado", "Código no registrado.")
            return

        id_producto, nombre, stock, precio = resultado

        for i, (id_p, nom, cant, prec) in enumerate(self.productos_añadidos):
            if id_p == id_producto:
                self.productos_añadidos[i] = (id_p, nom, cant + 1, prec)
                self.refrescar_añadidos()
                self.actualizar_costo_total()
                self.entry_codigo_oculto.delete(0, tk.END)
                return

        self.productos_añadidos.append((id_producto, nombre, 1, float(precio)))
        self.refrescar_añadidos()
        self.actualizar_costo_total()
        self.entry_codigo_oculto.delete(0, tk.END)

    def reestablecer_foco_lector(self):
        if not self.winfo_ismapped():
            return
        if self.lector_habilitado:
            try:
                widget_actual = self.focus_get()
                if widget_actual not in [self.entry_precio, self.entry_cantidad, self.entry_nombre, self.entry_busqueda]:
                    self.entry_codigo_oculto.focus_set()
            except:
                pass
        self.after(1000, self.reestablecer_foco_lector)

    def guardar_ancheta(self):
        nombre = self.entry_nombre.get().strip()
        precio = self.entry_precio.get().strip()
        proveedor = self.entry_proveedor.get().strip()
        tipo = self.entry_tipo.get().strip()

        if not nombre or not precio or not proveedor or not tipo:
            messagebox.showwarning("Campos incompletos", "Todos los campos son obligatorios.")
            return
        if not self.productos_añadidos:
            messagebox.showerror("Error", "Debe agregar productos a la ancheta.")
            return
        try:
            precio = float(precio)
        except:
            messagebox.showerror("Error", "Precio inválido.")
            return

        # Calcular costo total de componentes
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        costo_real = 0
        for id_producto, _, cantidad, _ in self.productos_añadidos:
            cursor.execute("SELECT costo FROM inventario WHERE id = ?", (id_producto,))
            resultado = cursor.fetchone()
            if resultado:
                costo_unitario = resultado[0]
                costo_real += int(cantidad) * float(costo_unitario)

        cursor.execute("INSERT INTO anchetas (nombre, precio) VALUES (?, ?)", (nombre, precio))
        id_ancheta = cursor.lastrowid

        for id_producto, _, cantidad, _ in self.productos_añadidos:
            cursor.execute("INSERT INTO ancheta_detalle (id_ancheta, id_producto, cantidad) VALUES (?, ?, ?)",
                           (id_ancheta, id_producto, cantidad))

        cursor.execute("INSERT INTO inventario (nombre, proveedor, tipo_producto, precio, costo, stock, es_servicio, umbral_stock, codigo_barras) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (nombre, proveedor, tipo, precio, costo_real, 999999, 0, 0, f"ANC{id_ancheta:04d}"))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Ancheta guardada correctamente.")
        self.destroy()
