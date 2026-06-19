import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import sys
import os

class EstadoResultados(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Estado de Resultados")
        self.geometry("900x560")
        self.config(bg="#f4f4f4")
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        self.db_name = os.path.join(base_path, "database.db")
        self.resizable(False, False)
        self.widgets()

    def rutas(self, ruta):
        try:
            rutabase = sys._MEIPASS
        except Exception:
            rutabase=os.path.abspath(".")
        return os.path.join(rutabase,ruta)    

    def widgets(self):
        tk.Label(self, text="Estado de Resultados", font="sans 16 bold", bg="#f4f4f4").pack(pady=10)

        filtros = tk.Frame(self, bg="#f4f4f4")
        filtros.pack()

        tk.Label(filtros, text="Desde:", bg="#f4f4f4").grid(row=0, column=0, padx=5)
        self.fecha_desde = DateEntry(filtros, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_desde.grid(row=0, column=1, padx=5)

        tk.Label(filtros, text="Hasta:", bg="#f4f4f4").grid(row=0, column=2, padx=5)
        self.fecha_hasta = DateEntry(filtros, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_hasta.grid(row=0, column=3, padx=5)

        tk.Button(filtros, text="Generar", command=self.generar_resultado, bg="#2e7d32", fg="white", font="sans 10 bold").grid(row=0, column=4, padx=10)

        self.tree = ttk.Treeview(self, columns=("concepto", "valor"), show="headings", height=15)
        self.tree.pack(pady=20, padx=20)

        self.tree.heading("concepto", text="Concepto")
        self.tree.column("concepto", width=450, anchor="center")

        self.tree.heading("valor", text="Valor")
        self.tree.column("valor", width=400, anchor="center")

    def generar_resultado(self):
        desde = self.fecha_desde.get_date().strftime("%Y-%m-%d")
        hasta = self.fecha_hasta.get_date().strftime("%Y-%m-%d")

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Ventas totales
            cursor.execute("""
                SELECT SUM(subtotal) FROM ventas_historico
                WHERE DATE(fecha) BETWEEN ? AND ?
            """, (desde, hasta))
            ventas_totales = cursor.fetchone()[0] or 0

            # Costo de ventas
            cursor.execute("""
                SELECT v.nombre_articulo, v.cantidad, i.costo
                FROM ventas_historico v
                JOIN inventario i ON v.nombre_articulo = i.nombre
                WHERE DATE(v.fecha) BETWEEN ? AND ?
            """, (desde, hasta))
            rows = cursor.fetchall()
            costo_total = sum(cantidad * costo for _, cantidad, costo in rows)

            # Gastos variables (egresos)
            cursor.execute("""
                SELECT SUM(monto) FROM egresos_historial
                WHERE DATE(fecha_hora) BETWEEN ? AND ?
            """, (desde, hasta))
            gastos_variables_egresos = cursor.fetchone()[0] or 0

            # Comisiones por tarjeta
            cursor.execute("""
                SELECT COUNT(*) FROM ventas_historico
                WHERE tipo_pago = 'tarjeta' AND DATE(fecha) BETWEEN ? AND ?
            """, (desde, hasta))
            total_tarjeta = cursor.fetchone()[0]
            comisiones = total_tarjeta * 1000

            # Gastos Fijos (NO dependen de fecha)
            cursor.execute("SELECT SUM(valor) FROM gastos_fijos")
            gastos_fijos = cursor.fetchone()[0] or 0

            # Gastos Variables (registrados manualmente)
            cursor.execute("""
                SELECT SUM(valor) FROM gastos_variables
                WHERE DATE(fecha) BETWEEN ? AND ?
            """, (desde, hasta))
            gastos_variables_registrados = cursor.fetchone()[0] or 0

            conn.close()

            utilidad_bruta = ventas_totales - costo_total
            total_gastos = gastos_variables_egresos + comisiones + gastos_fijos + gastos_variables_registrados
            utilidad_neta = utilidad_bruta - total_gastos

            for item in self.tree.get_children():
                self.tree.delete(item)

            resultados = [
                ("Ventas Totales", ventas_totales),
                ("Costo de Ventas", -costo_total),
                ("Utilidad Bruta", utilidad_bruta),
                ("Gastos Variables (egresos)", -gastos_variables_egresos),
                ("Gastos Variables (registrados)", -gastos_variables_registrados),
                ("Gastos Fijos", -gastos_fijos),
                ("Comisiones por Tarjeta", -comisiones),
                ("Utilidad Neta", utilidad_neta)
            ]

            for concepto, valor in resultados:
                self.tree.insert("", "end", values=(concepto, f"${valor:,.2f}"))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el estado de resultados:\n{e}")
