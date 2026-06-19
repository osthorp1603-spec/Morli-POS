import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import calendar
import sys
import os

class HistorialContableMes(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Historial Contable por Mes")
        self.geometry("1000x550")
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
        tk.Label(self, text="Historial Contable por Mes", font="sans 16 bold", bg="#f4f4f4").pack(pady=10)

        filtro_frame = tk.Frame(self, bg="#f4f4f4")
        filtro_frame.pack(pady=5)

        tk.Label(filtro_frame, text="Desde:", bg="#f4f4f4").grid(row=0, column=0, padx=5)
        self.fecha_desde = DateEntry(filtro_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_desde.grid(row=0, column=1, padx=5)

        tk.Label(filtro_frame, text="Hasta:", bg="#f4f4f4").grid(row=0, column=2, padx=5)
        self.fecha_hasta = DateEntry(filtro_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_hasta.grid(row=0, column=3, padx=5)

        tk.Button(filtro_frame, text="Filtrar", command=self.cargar_datos, bg="#2e7d32", fg="white", font="sans 10 bold").grid(row=0, column=4, padx=10)

        columnas = ("mes", "ventas", "egresos", "g_fijos", "g_variables", "prestamos", "deudas", "arqueo", "utilidad")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings", height=18)
        self.tree.pack(pady=15)

        encabezados = [
            "Mes", "Ventas", "Egresos", "Gastos Fijos", "Gastos Variables",
            "Préstamos", "Deudas", "Arqueo Final", "Utilidad Estimada"
        ]
        anchos = [120, 100, 100, 100, 110, 100, 100, 110, 130]

        for col, text, ancho in zip(columnas, encabezados, anchos):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=ancho, anchor="center")

    def cargar_datos(self):
        desde = self.fecha_desde.get_date().strftime("%Y-%m-%d")
        hasta = self.fecha_hasta.get_date().strftime("%Y-%m-%d")

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Ventas por mes
            cursor.execute("""
                SELECT strftime('%Y', fecha), strftime('%m', fecha), SUM(subtotal)
                FROM ventas_historico
                WHERE DATE(fecha) BETWEEN ? AND ?
                GROUP BY 1, 2
            """, (desde, hasta))
            ventas = {(y, m): v for y, m, v in cursor.fetchall()}

            def sumar_por_mes(tabla, campo_fecha, campo_monto):
                cursor.execute(f"""
                    SELECT strftime('%Y', {campo_fecha}), strftime('%m', {campo_fecha}), SUM({campo_monto})
                    FROM {tabla}
                    WHERE DATE({campo_fecha}) BETWEEN ? AND ?
                    GROUP BY 1, 2
                """, (desde, hasta))
                return {(y, m): v for y, m, v in cursor.fetchall()}

            egresos = sumar_por_mes("egresos_historial", "fecha_hora", "monto")
            prestamos = sumar_por_mes("prestamos", "fecha", "monto")
            deudas = sumar_por_mes("deudas_proveedores", "fecha", "monto")
            arqueo = sumar_por_mes("arqueo_caja", "fecha_hora", "monto")
            g_fijos = sumar_por_mes("gastos_fijos", "fecha", "valor")
            g_variables = sumar_por_mes("gastos_variables", "fecha", "valor")

            conn.close()

            # Limpiar tabla
            for i in self.tree.get_children():
                self.tree.delete(i)

            # Combinar todas las claves (año, mes)
            meses_todos = set(ventas) | set(egresos) | set(prestamos) | set(deudas) | set(arqueo) | set(g_fijos) | set(g_variables)

            for y, m in sorted(meses_todos):
                nombre_mes = calendar.month_name[int(m)]
                mes_str = f"{nombre_mes} {y}"

                v = ventas.get((y, m), 0)
                e = egresos.get((y, m), 0)
                gf = g_fijos.get((y, m), 0)
                gv = g_variables.get((y, m), 0)
                p = prestamos.get((y, m), 0)
                d = deudas.get((y, m), 0)
                a = arqueo.get((y, m), 0)

                utilidad = v - (e + gf + gv + p + d)

                self.tree.insert("", "end", values=(
                    mes_str,
                    f"${v:,.2f}",
                    f"${e:,.2f}",
                    f"${gf:,.2f}",
                    f"${gv:,.2f}",
                    f"${p:,.2f}",
                    f"${d:,.2f}",
                    f"${a:,.2f}",
                    f"${utilidad:,.2f}"
                ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial contable:\n{e}")
