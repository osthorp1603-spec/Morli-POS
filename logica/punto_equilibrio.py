import tkinter as tk
from tkinter import messagebox
import sqlite3
import sys
import os

def rutas(self, ruta):
        try:
            rutabase = sys._MEIPASS
        except Exception:
            rutabase=os.path.abspath(".")
        return os.path.join(rutabase,ruta) 

class PuntoEquilibrio:
    def __init__(self, master):
        self.master = master
        self.master.title("Punto de Equilibrio")
        self.master.geometry("800x500")
        self.master.config(bg="#f5f7fa")
        self.master.resizable(False, False)

        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        self.conn = sqlite3.connect(os.path.join(base_path, "database.db"))
        self.cursor = self.conn.cursor()

        tk.Label(master, text="Cálculo del Punto de Equilibrio", font=("Arial", 20, "bold"), bg="#f5f7fa").pack(pady=15)

        contenedor = tk.Frame(master, bg="#f5f7fa")
        contenedor.pack(pady=10)

        # 🔵 MODO MANUAL
        frame_manual = tk.LabelFrame(contenedor, text="Modo Manual", font=("Arial", 12, "bold"), bg="#e3f2fd", padx=10, pady=10)
        frame_manual.grid(row=0, column=0, padx=20)

        tk.Label(frame_manual, text="Precio de venta unitario:", bg="#e3f2fd").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_precio_venta = tk.Entry(frame_manual, width=25)
        self.entry_precio_venta.grid(row=1, column=0, pady=5)

        tk.Label(frame_manual, text="Costo variable unitario:", bg="#e3f2fd").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_costo_variable = tk.Entry(frame_manual, width=25)
        self.entry_costo_variable.grid(row=3, column=0, pady=5)

        btn_manual = tk.Button(frame_manual, text="Calcular Manual", bg="#1976d2", fg="white", font=("Arial", 10, "bold"),
                               width=25, command=self.calcular_manual)
        btn_manual.grid(row=4, column=0, pady=10)

        self.resultado_manual = tk.Label(frame_manual, text="", font=("Arial", 10), bg="#e3f2fd", justify="left")
        self.resultado_manual.grid(row=5, column=0, pady=10)

        # 🟠 MODO MULTIPRODUCTO AUTOMÁTICO
        frame_auto = tk.LabelFrame(contenedor, text="Modo Multiproducto (Automático)", font=("Arial", 12, "bold"), bg="#fff3e0", padx=10, pady=10)
        frame_auto.grid(row=0, column=1, padx=20)

        btn_auto = tk.Button(frame_auto, text="Calcular Automático", bg="#ff6f00", fg="white", font=("Arial", 10, "bold"),
                             width=25, command=self.calcular_automatico)
        btn_auto.grid(row=0, column=0, pady=5)

        self.resultado_auto = tk.Label(frame_auto, text="", font=("Arial", 10), bg="#fff3e0", justify="left")
        self.resultado_auto.grid(row=1, column=0, pady=10)

    def calcular_manual(self):
        try:
            precio_venta = float(self.entry_precio_venta.get())
            costo_variable = float(self.entry_costo_variable.get())

            if precio_venta <= costo_variable:
                messagebox.showerror("Error", "El precio de venta debe ser mayor al costo variable.")
                return

            self.cursor.execute("SELECT SUM(valor) FROM gastos_fijos")
            resultado = self.cursor.fetchone()
            costos_fijos = resultado[0] if resultado[0] else 0

            if costos_fijos == 0:
                messagebox.showwarning("Sin gastos fijos", "No hay registros en gastos fijos.")
                return

            punto_equilibrio = costos_fijos / (precio_venta - costo_variable)

            self.resultado_manual.config(
                text=f"Costos fijos: ${costos_fijos:,.2f}\n"
                     f"Fórmula: {costos_fijos:.2f} / ({precio_venta:.2f} - {costo_variable:.2f})\n"
                     f"👉 Punto de Equilibrio: {punto_equilibrio:.2f} unidades"
            )
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos.")

    def calcular_automatico(self):
        self.cursor.execute("SELECT SUM(valor) FROM gastos_fijos")
        total_fijos = self.cursor.fetchone()[0]
        if not total_fijos or total_fijos == 0:
            messagebox.showwarning("Atención", "No hay gastos fijos registrados.")
            return

        self.cursor.execute("""
            SELECT v.nombre_articulo, v.cantidad, i.precio, i.costo
            FROM ventas_historico v
            JOIN inventario i ON v.nombre_articulo = i.nombre
            WHERE v.cantidad > 0 AND i.precio > 0 AND i.costo >= 0
        """)
        filas = self.cursor.fetchall()

        if not filas:
            messagebox.showwarning("Sin datos", "No se encontraron coincidencias entre ventas e inventario.")
            return

        total_unidades = 0
        total_ventas = 0
        total_costos = 0

        for nombre, cantidad, precio, costo in filas:
            try:
                cantidad = float(cantidad)
                precio = float(precio)
                costo = float(costo)
            except (ValueError, TypeError):
                continue  # Ignora esta fila si hay datos inválidos

            if cantidad <= 0 or precio <= 0 or costo < 0:
                continue  # Ignora registros inválidos

            total_unidades += cantidad
            total_ventas += cantidad * precio
            total_costos += cantidad * costo

        if total_unidades == 0:
            messagebox.showerror("Error", "No hay unidades válidas registradas.")
            return

        precio_promedio = total_ventas / total_unidades
        costo_promedio = total_costos / total_unidades
        utilidad_promedio = precio_promedio - costo_promedio

        if utilidad_promedio <= 0:
            messagebox.showerror("Error", "La utilidad promedio por unidad es cero o negativa.")
            return

        punto_equilibrio = total_fijos / utilidad_promedio

        self.resultado_auto.config(
            text=f"Costos fijos: ${total_fijos:,.2f}\n"
                 f"Precio promedio: ${precio_promedio:,.2f}\n"
                 f"Costo promedio: ${costo_promedio:,.2f}\n"
                 f"Utilidad promedio: ${utilidad_promedio:,.2f}\n"
                 f"👉 Punto de Equilibrio: {punto_equilibrio:.2f} unidades"
        )
