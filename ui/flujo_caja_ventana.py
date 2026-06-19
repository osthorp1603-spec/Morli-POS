import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import sys
import os

class FlujoCaja(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Flujo de Caja - Contabilidad")
        self.geometry("900x560")
        self.config(bg="#eaf4fc")
        self.resizable(False, False)
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        self.db_name = os.path.join(base_path, "database.db")

        self.widgets()

    def rutas(self, ruta):
        try:
            rutabase = sys._MEIPASS
        except Exception:
            rutabase=os.path.abspath(".")
        return os.path.join(rutabase,ruta)    

    def widgets(self):
        tk.Label(self, text="Flujo de Caja Contable", font="sans 16 bold", bg="#eaf4fc").pack(pady=10)

        filtros = tk.Frame(self, bg="#eaf4fc")
        filtros.pack(pady=5)

        tk.Label(filtros, text="Desde:", bg="#eaf4fc").grid(row=0, column=0, padx=5)
        self.fecha_desde = DateEntry(filtros, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_desde.grid(row=0, column=1, padx=5)

        tk.Label(filtros, text="Hasta:", bg="#eaf4fc").grid(row=0, column=2, padx=5)
        self.fecha_hasta = DateEntry(filtros, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_hasta.grid(row=0, column=3, padx=5)

        tk.Button(filtros, text="Filtrar", command=self.cargar_datos, bg="#4caf50", fg="white", font="sans 10 bold").grid(row=0, column=4, padx=10)

        self.tree = ttk.Treeview(
            self,
            columns=("fecha", "efectivo", "qr", "tarjeta", "egresos", "arqueo", "diferencia"),
            show="headings",
            height=15
        )
        self.tree.pack(pady=10)

        self.tree.heading("fecha", text="Fecha")
        self.tree.column("fecha", width=120, anchor="center")

        self.tree.heading("efectivo", text="Efectivo")
        self.tree.column("efectivo", width=130, anchor="center")

        self.tree.heading("qr", text="QR")
        self.tree.column("qr", width=130, anchor="center")

        self.tree.heading("tarjeta", text="Tarjeta")
        self.tree.column("tarjeta", width=130, anchor="center")

        self.tree.heading("egresos", text="Egresos")
        self.tree.column("egresos", width=130, anchor="center")

        self.tree.heading("arqueo", text="Arqueo")
        self.tree.column("arqueo", width=130, anchor="center")

        self.tree.heading("diferencia", text="Diferencia")
        self.tree.column("diferencia", width=130, anchor="center")

        self.label_total = tk.Label(self, text="", font="sans 12 bold", bg="#eaf4fc")
        self.label_total.pack(pady=10)

    def cargar_datos(self):
        fecha_inicio = self.fecha_desde.get_date().strftime("%Y-%m-%d")
        fecha_fin = self.fecha_hasta.get_date().strftime("%Y-%m-%d")

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DATE(fecha), tipo_pago, SUM(subtotal)
                FROM ventas_historico
                WHERE DATE(fecha) BETWEEN ? AND ?
                GROUP BY DATE(fecha), tipo_pago
            """, (fecha_inicio, fecha_fin))
            ingresos_data = cursor.fetchall()

            cursor.execute("""
                SELECT DATE(fecha_hora), SUM(monto)
                FROM egresos_dia
                WHERE DATE(fecha_hora) BETWEEN ? AND ?
                GROUP BY DATE(fecha_hora)
            """, (fecha_inicio, fecha_fin))
            egresos_data = dict(cursor.fetchall())

            cursor.execute("""
                SELECT DATE(fecha_hora), monto
                FROM arqueo_caja
                WHERE DATE(fecha_hora) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            arqueo_data = dict(cursor.fetchall())

            conn.close()

            ingresos_por_fecha = {}
            for fecha, tipo, valor in ingresos_data:
                if fecha not in ingresos_por_fecha:
                    ingresos_por_fecha[fecha] = {"efectivo": 0, "qr": 0, "tarjeta": 0}
                tipo = tipo.lower()
                if tipo in ingresos_por_fecha[fecha]:
                    ingresos_por_fecha[fecha][tipo] += valor

            for item in self.tree.get_children():
                self.tree.delete(item)

            total_ingresos = total_egresos = total_arqueo = total_diferencia = 0

            for fecha in sorted(ingresos_por_fecha.keys()):
                ingresos = ingresos_por_fecha[fecha]
                efectivo = ingresos.get("efectivo", 0)
                qr = ingresos.get("qr", 0)
                tarjeta = ingresos.get("tarjeta", 0)
                egresos = egresos_data.get(fecha, 0)
                arqueo = arqueo_data.get(fecha, 0)
                diferencia = (efectivo + qr + tarjeta) - egresos - arqueo

                total_ingresos += efectivo + qr + tarjeta
                total_egresos += egresos
                total_arqueo += arqueo
                total_diferencia += diferencia

                self.tree.insert("", "end", values=(
                    fecha,
                    f"${efectivo:,.2f}",
                    f"${qr:,.2f}",
                    f"${tarjeta:,.2f}",
                    f"${egresos:,.2f}",
                    f"${arqueo:,.2f}",
                    f"${diferencia:,.2f}",
                ))

            self.label_total.config(
                text=f"Ingresos: ${total_ingresos:,.2f}   Egresos: ${total_egresos:,.2f}   Arqueo: ${total_arqueo:,.2f}   Diferencia: ${total_diferencia:,.2f}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los datos: {e}")


