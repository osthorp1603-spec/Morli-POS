import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import sys
import os

class DeudasProveedores(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Deudas a Proveedores")
        self.geometry("850x610")
        self.config(bg="#f7f7f7")
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        self.db_name = os.path.join(base_path, "database.db")

        self.resizable(False, False)

        self.crear_tablas()
        self.widgets()
        self.cargar_deudas()

    def rutas(self, ruta):
        try:
            rutabase = sys._MEIPASS
        except Exception:
            rutabase = os.path.abspath(".")
        return os.path.join(rutabase, ruta)

    def crear_tablas(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Tabla de deudas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deudas_proveedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proveedor TEXT NOT NULL,
                motivo TEXT,
                monto REAL NOT NULL,
                fecha TEXT NOT NULL,
                estado TEXT DEFAULT 'pendiente'
            )
        """)

        # Tabla de egresos con columnas reales
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS egresos_dia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT,
                motivo TEXT,
                monto REAL,
                metodo TEXT
            )
        """)

        conn.commit()
        conn.close()

    def widgets(self):
        titulo = tk.Label(self, text="Registro de Deudas a Proveedores", font="sans 16 bold", bg="#f7f7f7")
        titulo.pack(pady=10)

        frame_form = tk.Frame(self, bg="#f7f7f7")
        frame_form.pack(pady=10)

        tk.Label(frame_form, text="Proveedor:", bg="#f7f7f7").grid(row=0, column=0, padx=5, pady=5)
        self.entry_proveedor = tk.Entry(frame_form, width=25)
        self.entry_proveedor.grid(row=0, column=1, padx=5)

        tk.Label(frame_form, text="Motivo:", bg="#f7f7f7").grid(row=1, column=0, padx=5, pady=5)
        self.entry_motivo = tk.Entry(frame_form, width=25)
        self.entry_motivo.grid(row=1, column=1, padx=5)

        tk.Label(frame_form, text="Monto:", bg="#f7f7f7").grid(row=0, column=2, padx=5, pady=5)
        self.entry_monto = tk.Entry(frame_form, width=20)
        self.entry_monto.grid(row=0, column=3, padx=5)

        tk.Label(frame_form, text="Fecha:", bg="#f7f7f7").grid(row=1, column=2, padx=5, pady=5)
        self.entry_fecha = DateEntry(frame_form, width=18, background='darkblue', foreground='white', borderwidth=2)
        self.entry_fecha.grid(row=1, column=3, padx=5)

        self.btn_guardar = tk.Button(self, text="Registrar Deuda", command=self.registrar_deuda, bg="#007acc", fg="white", font="sans 10 bold")
        self.btn_guardar.pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("id", "proveedor", "motivo", "monto", "fecha", "estado"), show="headings", height=12)
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        for col in ("id", "proveedor", "motivo", "monto", "fecha", "estado"):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100, anchor="center")

        frame_botones = tk.Frame(self, bg="#f7f7f7")
        frame_botones.pack(pady=5)

        self.btn_pagar = tk.Button(frame_botones, text="Pagar", bg="lightgreen", font="sans 10 bold", command=self.pagar_deuda)
        self.btn_pagar.grid(row=0, column=0, padx=5)

    def registrar_deuda(self):
        proveedor = self.entry_proveedor.get().strip()
        motivo = self.entry_motivo.get().strip()
        monto = self.entry_monto.get().strip()
        fecha = self.entry_fecha.get_date().strftime("%Y-%m-%d")

        if not proveedor or not monto:
            messagebox.showwarning("Campos obligatorios", "Proveedor y monto son obligatorios.")
            return

        try:
            monto = float(monto)
        except ValueError:
            messagebox.showwarning("Monto inválido", "El monto debe ser un número válido.")
            return

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO deudas_proveedores (proveedor, motivo, monto, fecha, estado)
            VALUES (?, ?, ?, ?, 'pendiente')
        """, (proveedor, motivo, monto, fecha))
        conn.commit()
        conn.close()

        self.entry_proveedor.delete(0, tk.END)
        self.entry_motivo.delete(0, tk.END)
        self.entry_monto.delete(0, tk.END)

        self.cargar_deudas()

    def cargar_deudas(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM deudas_proveedores ORDER BY fecha DESC")
        filas = cursor.fetchall()
        conn.close()

        for fila in filas:
            self.tree.insert("", tk.END, values=fila)

    def pagar_deuda(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una deuda para pagar.")
            return

        item = self.tree.item(seleccion)
        id_deuda = item["values"][0]
        proveedor = item["values"][1]
        motivo = item["values"][2]
        monto = item["values"][3]
        estado = item["values"][5]

        if estado.lower() == "pagado":
            messagebox.showinfo("Info", "Esta deuda ya fue pagada.")
            return

        try:
            monto = float(monto)
        except ValueError:
            messagebox.showerror("Error", "Monto inválido.")
            return

        confirmar = messagebox.askyesno("Confirmar pago", f"¿Deseas marcar como pagada la deuda a {proveedor} por ${monto:,.0f}?")
        if not confirmar:
            return

        fecha_pago = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        motivo_egreso = f"Pago a proveedor: {proveedor}"

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Actualizar estado de la deuda
        cursor.execute("UPDATE deudas_proveedores SET estado='Pagado', fecha=? WHERE id=?", (fecha_pago, id_deuda))

        # Insertar en egresos_dia con nombres de campo correctos
        cursor.execute("""
            INSERT INTO egresos_dia (fecha_hora, motivo, monto, metodo)
            VALUES (?, ?, ?, ?)
        """, (fecha_pago, motivo_egreso, monto, "Operativo"))

        cursor.execute("""
            INSERT INTO egresos_historial (fecha_hora, motivo, monto, metodo)
            VALUES (?, ?, ?, ?)
        """, (fecha_pago, motivo_egreso, monto, "Operativo"))


        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Deuda pagada y registrada como gasto operativo.")
        self.cargar_deudas()

# ✅ FUNCIÓN EXTERNA
def abrir_deudas_proveedores(parent):
    DeudasProveedores(parent)
