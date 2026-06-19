import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime

class MovimientosInventario(tk.Toplevel):
    """
    Ventana de SOLO LECTURA que muestra salidas reales de inventario:
    - Productos normales vendidos (precio/subtotal desde ventas_historico + costo desde inventario)
    - Componentes de ANCHETAS (precio/subtotal = 0; costo = costo de cada componente * cantidad usada)
    Filtros: fecha desde/hasta, tipo de producto, proveedor.
    Totales: vendido, costo, utilidad.
    """
    def __init__(self, parent, db_name: str):
        super().__init__(parent)
        self.title("Movimientos de Inventario")
        self.geometry("1100x650")
        self.config(bg="#c6d9e3")
        self.resizable(False, False)
        self.db_name = db_name

        # ---- Título
        lbl_titulo = tk.Label(self, text="MOVIMIENTOS DE INVENTARIO", font="sans 28 bold", bg="#c6d9e3")
        lbl_titulo.place(x=250, y=5)

        # ---- Filtros
        tk.Label(self, text="Proveedor:", font="sans 12 bold", bg="#c6d9e3").place(x=20, y=70)
        self.combo_proveedor = ttk.Combobox(self, font="sans 12", state="readonly")
        self.combo_proveedor.place(x=120, y=70, width=180)

        tk.Label(self, text="Tipo de Producto:", font="sans 12 bold", bg="#c6d9e3").place(x=320, y=70)
        self.combo_tipo = ttk.Combobox(self, font="sans 12", state="readonly")
        self.combo_tipo.place(x=470, y=70, width=180)

        tk.Label(self, text="Desde:", font="sans 12 bold", bg="#c6d9e3").place(x=670, y=70)
        self.fecha_desde = DateEntry(self, font="sans 12", width=12, background="darkblue",
                                     foreground="white", borderwidth=2)
        self.fecha_desde.place(x=730, y=70)

        tk.Label(self, text="Hasta:", font="sans 12 bold", bg="#c6d9e3").place(x=870, y=70)
        self.fecha_hasta = DateEntry(self, font="sans 12", width=12, background="darkblue",
                                     foreground="white", borderwidth=2)
        self.fecha_hasta.place(x=920, y=70)

        btn_filtrar = tk.Button(self, text="Filtrar", font="sans 12 bold", bg="#dddddd",
                                command=self.cargar_movimientos)
        btn_filtrar.place(x=950, y=110, width=120, height=30)

        btn_todos = tk.Button(self, text="Mostrar Todo", font="sans 12 bold", bg="#dddddd",
                              command=lambda: self.reset_filtros(True))
        btn_todos.place(x=820, y=110, width=120, height=30)

        # ---- Tabla
        frame_tabla = tk.Frame(self, bg="#c6d9e3")
        frame_tabla.place(x=35, y=150, width=1030, height=395)

        scrol_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
        scrol_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrol_x = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)
        scrol_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(
            frame_tabla,
            columns=("Producto", "Proveedor", "Tipo", "Cantidad",
                     "Precio uni", "Subtotal", "Costo uni", "Total costo"),
            show="headings", height=10,
            yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set
        )
        scrol_y.config(command=self.tree.yview)
        scrol_x.config(command=self.tree.xview)

        for col, ancho in [
            ("Producto", 240), ("Proveedor", 160), ("Tipo", 120), ("Cantidad", 90),
            ("Precio uni", 110), ("Subtotal", 120), ("Costo uni", 110), ("Total costo", 120)
        ]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor="center")

        self.tree.pack(expand=True, fill=tk.BOTH)

        # ---- Totales
        self.lbl_total_vendido = tk.Label(self, text="Total vendido: $0", font="sans 12 bold", bg="#c6d9e3")
        self.lbl_total_vendido.place(x=700, y=560)

        self.lbl_total_costo = tk.Label(self, text="Total costo: $0", font="sans 12 bold", bg="#c6d9e3")
        self.lbl_total_costo.place(x=700, y=585)

        self.lbl_utilidad = tk.Label(self, text="Utilidad: $0", font="sans 12 bold", bg="#c6d9e3")
        self.lbl_utilidad.place(x=700, y=610)

        # ---- Cargar filtros + datos
        self.cargar_filtros()
        self.cargar_movimientos()

        # ---- Hacer esta ventana modal respecto al padre (evita bloqueo de botones)
        self.transient(self.master)
        self.grab_set()
        self.focus_force()
        self.lift()

        # Al cerrar, devolver control al padre si estaba modal
        def _cerrar():
            try:
                if self.master and self.master.winfo_exists():
                    self.master.grab_set()
            except:
                pass
            self.destroy()

        self.protocol("WM_DELETE_WINDOW", _cerrar)

    # ----------------- UI helpers -----------------
    def reset_filtros(self, recargar=False):
        self.combo_proveedor.set("")
        self.combo_tipo.set("")
        hoy = datetime.now()
        self.fecha_desde.set_date(hoy)
        self.fecha_hasta.set_date(hoy)
        if recargar:
            self.cargar_movimientos()

    def cargar_filtros(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT DISTINCT proveedor FROM inventario WHERE proveedor IS NOT NULL AND proveedor <> '' ORDER BY proveedor ASC")
            proveedores = [r[0] for r in c.fetchall()]
            c.execute("SELECT DISTINCT tipo_producto FROM inventario WHERE tipo_producto IS NOT NULL AND tipo_producto <> '' ORDER BY tipo_producto ASC")
            tipos = [r[0] for r in c.fetchall()]
            conn.close()
        except sqlite3.Error as e:
            proveedores, tipos = [], []
            messagebox.showerror("Error", f"No se pudieron cargar filtros:\n{e}")

        self.combo_proveedor["values"] = [""] + proveedores
        self.combo_tipo["values"] = [""] + tipos
        self.reset_filtros()

    # ----------------- Carga principal -----------------
    def cargar_movimientos(self):
        # Recolectar filtros
        proveedor = (self.combo_proveedor.get() or "").strip()
        tipo = (self.combo_tipo.get() or "").strip()
        f_desde = self.fecha_desde.get()
        f_hasta = self.fecha_hasta.get()

        # Normalizar fechas a YYYY-MM-DD 00:00:00 / 23:59:59
        rango = []
        where_rango = ""
        try:
            desde_sql = datetime.strptime(f_desde, "%m/%d/%y").strftime("%Y-%m-%d 00:00:00")
            hasta_sql = datetime.strptime(f_hasta, "%m/%d/%y").strftime("%Y-%m-%d 23:59:59")
            where_rango = " WHERE fecha BETWEEN ? AND ? "
            rango = [desde_sql, hasta_sql]
        except:
            where_rango = ""
            rango = []

        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()

            # ---- Productos normales (EXCLUYE anchetas por nombre)
            sql_normales = """
                SELECT
                    COALESCE(i.nombre, vh.nombre_articulo)              AS producto,
                    COALESCE(i.proveedor, '')                           AS proveedor,
                    COALESCE(i.tipo_producto, '')                       AS tipo,
                    vh.cantidad                                         AS cantidad,
                    vh.valor_articulo                                   AS precio_uni,
                    vh.subtotal                                         AS subtotal,
                    COALESCE(i.costo, 0)                                AS costo_uni,
                    COALESCE(i.costo, 0) * vh.cantidad                  AS total_costo,
                    vh.fecha                                            AS fecha
                FROM ventas_historico vh
                LEFT JOIN inventario i ON i.nombre = vh.nombre_articulo
                LEFT JOIN anchetas a  ON a.nombre = vh.nombre_articulo
                WHERE a.id IS NULL
            """

            # ---- Componentes de ANCHETAS (precio/subtotal = 0)
            sql_componentes = """
                SELECT
                    ic.nombre                                                   AS producto,
                    COALESCE(ic.proveedor, '')                                  AS proveedor,
                    COALESCE(ic.tipo_producto, '')                              AS tipo,
                    (vh.cantidad * ad.cantidad)                                 AS cantidad,
                    COALESCE(ic.precio, 0)                                      AS precio_uni,
                    COALESCE(ic.precio, 0) * (vh.cantidad * ad.cantidad)        AS subtotal,
                    COALESCE(ic.costo, 0)                                       AS costo_uni,
                    COALESCE(ic.costo, 0) * (vh.cantidad * ad.cantidad)         AS total_costo,
                    vh.fecha                                                    AS fecha
                FROM ventas_historico vh
                JOIN anchetas a          ON a.nombre = vh.nombre_articulo
                JOIN ancheta_detalle ad  ON ad.id_ancheta = a.id
                JOIN inventario ic       ON ic.id = ad.id_producto
            """

            # Unión y filtros externos
            sql_union = f"""
                SELECT * FROM (
                    {sql_normales}
                    UNION ALL
                    {sql_componentes}
                )
            """

            params = []
            if where_rango:
                sql_union += where_rango
                params.extend(rango)

            filtros_adicionales = []
            if proveedor:
                filtros_adicionales.append(" proveedor LIKE ? ")
                params.append(f"%{proveedor}%")
            if tipo:
                filtros_adicionales.append(" tipo LIKE ? ")
                params.append(f"%{tipo}%")

            if filtros_adicionales:
                if "WHERE" in sql_union.upper():
                    sql_union += " AND " + " AND ".join(filtros_adicionales)
                else:
                    sql_union += " WHERE " + " AND ".join(filtros_adicionales)

            sql_union += " ORDER BY fecha DESC, producto ASC"

            c.execute(sql_union, params)
            filas = c.fetchall()
            conn.close()

            # Poblar tabla
            self.tree.delete(*self.tree.get_children())
            total_vendido = 0.0
            total_costo = 0.0

            for (producto, proveedor, tipo, cantidad, precio_uni, subtotal, costo_uni, total_costo_row, _fecha) in filas:
                total_vendido += float(subtotal or 0)
                total_costo += float(total_costo_row or 0)
                self.tree.insert(
                    "", tk.END,
                    values=(
                        producto,
                        proveedor,
                        tipo,
                        int(cantidad),
                        f"$ {float(precio_uni):,.0f}",
                        f"$ {float(subtotal):,.0f}",
                        f"$ {float(costo_uni):,.0f}",
                        f"$ {float(total_costo_row):,.0f}"
                    )
                )

            utilidad = total_vendido - total_costo
            self.lbl_total_vendido.config(text=f"Total vendido: $ {total_vendido:,.0f}")
            self.lbl_total_costo.config(text=f"Total costo: $ {total_costo:,.0f}")
            self.lbl_utilidad.config(text=f"Utilidad: $ {utilidad:,.0f}")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar movimientos:\n{e}")
