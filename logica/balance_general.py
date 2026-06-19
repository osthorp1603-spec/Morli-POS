import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

class BalanceGeneral(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Balance General")
        self.geometry("800x500")
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
        tk.Label(self, text="Balance General", font="sans 16 bold", bg="#f4f4f4").pack(pady=10)

        tk.Button(self, text="Calcular", command=self.calcular_balance, bg="#2e7d32", fg="white", font="sans 10 bold").pack(pady=5)

        self.tree = ttk.Treeview(self, columns=("concepto", "valor"), show="headings", height=15)
        self.tree.pack(pady=20)

        self.tree.heading("concepto", text="Concepto")
        self.tree.column("concepto", width=400, anchor="center")

        self.tree.heading("valor", text="Valor")
        self.tree.column("valor", width=350, anchor="center")

    def calcular_balance(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Caja: último arqueo
            cursor.execute("SELECT monto FROM arqueo_caja ORDER BY fecha_hora DESC LIMIT 1")
            fila = cursor.fetchone()
            caja = fila[0] if fila else 0

            # Total préstamos
            cursor.execute("SELECT SUM(monto) FROM prestamos")
            prestamos = cursor.fetchone()[0] or 0

            # Total deudas proveedores
            cursor.execute("SELECT SUM(monto) FROM deudas_proveedores")
            deudas = cursor.fetchone()[0] or 0

            # Total egresos operativos
            cursor.execute("SELECT SUM(monto) FROM egresos_historial")
            egresos = cursor.fetchone()[0] or 0

            # ✅ Gastos fijos
            cursor.execute("SELECT SUM(valor) FROM gastos_fijos")
            gastos_fijos = cursor.fetchone()[0] or 0

            # ✅ Gastos variables registrados
            cursor.execute("SELECT SUM(valor) FROM gastos_variables")
            gastos_variables = cursor.fetchone()[0] or 0

            conn.close()

            activos = caja
            pasivos = prestamos + deudas
            total_gastos = egresos + gastos_fijos + gastos_variables
            patrimonio = activos - pasivos - total_gastos

            for item in self.tree.get_children():
                self.tree.delete(item)

            datos = [
                ("ACTIVOS", ""),
                ("Caja (último arqueo)", f"${caja:,.2f}"),
                ("", ""),
                ("PASIVOS", ""),
                ("Préstamos", f"${prestamos:,.2f}"),
                ("Deudas a Proveedores", f"${deudas:,.2f}"),
                ("", ""),
                ("EGRESOS Y GASTOS", ""),
                ("Egresos Operativos", f"${egresos:,.2f}"),
                ("Gastos Fijos", f"${gastos_fijos:,.2f}"),
                ("Gastos Variables", f"${gastos_variables:,.2f}"),
                ("", ""),
                ("PATRIMONIO", f"${patrimonio:,.2f}")
            ]

            for concepto, valor in datos:
                self.tree.insert("", "end", values=(concepto, valor))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo calcular el balance:\n{e}")
