import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import sys
import os

class PrestamosVentana(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Préstamos")
        self.geometry("920x600")
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
        # --- Título ---
        tk.Label(self, text="Historial de Préstamos", font="sans 16 bold", bg="#f4f4f4").pack(pady=10)

        # --- Filtros ---
        filtros = tk.Frame(self, bg="#f4f4f4")
        filtros.pack()

        tk.Label(filtros, text="Desde:", bg="#f4f4f4").grid(row=0, column=0, padx=5)
        self.fecha_desde = DateEntry(filtros, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_desde.grid(row=0, column=1, padx=5)

        tk.Label(filtros, text="Hasta:", bg="#f4f4f4").grid(row=0, column=2, padx=5)
        self.fecha_hasta = DateEntry(filtros, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_hasta.grid(row=0, column=3, padx=5)

        tk.Button(filtros, text="Filtrar", command=self.cargar_datos, bg="#2e7d32", fg="white", font="sans 10 bold").grid(row=0, column=4, padx=10)

        # --- Treeview ---
        self.tree = ttk.Treeview(self, columns=("fecha", "descripcion", "monto"), show="headings", height=12)
        self.tree.pack(pady=10)

        self.tree.heading("fecha", text="Fecha")
        self.tree.column("fecha", width=180, anchor="center")

        self.tree.heading("descripcion", text="Descripción")
        self.tree.column("descripcion", width=480, anchor="center")

        self.tree.heading("monto", text="Monto")
        self.tree.column("monto", width=200, anchor="e")

        # --- Registro nuevo préstamo ---
        registro = tk.Frame(self, bg="#f4f4f4")
        registro.pack(pady=10)

        tk.Label(registro, text="Fecha:", bg="#f4f4f4").grid(row=0, column=0, padx=5)
        self.fecha_prestamo = DateEntry(registro, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_prestamo.grid(row=0, column=1, padx=5)

        tk.Label(registro, text="Descripción:", bg="#f4f4f4").grid(row=0, column=2, padx=5)
        self.entry_descripcion = tk.Entry(registro, width=40)
        self.entry_descripcion.grid(row=0, column=3, padx=5)

        tk.Label(registro, text="Monto:", bg="#f4f4f4").grid(row=0, column=4, padx=5)
        self.entry_monto = tk.Entry(registro, width=15)
        self.entry_monto.grid(row=0, column=5, padx=5)

        tk.Button(registro, text="Registrar Préstamo", bg="#1976d2", fg="white", font="sans 10 bold", command=self.registrar_prestamo).grid(row=0, column=6, padx=10)

    def cargar_datos(self):
        desde = self.fecha_desde.get_date().strftime("%Y-%m-%d")
        hasta = self.fecha_hasta.get_date().strftime("%Y-%m-%d")

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prestamos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    monto REAL NOT NULL
                )
            """)

            cursor.execute("""
                SELECT fecha, descripcion, monto
                FROM prestamos
                WHERE DATE(fecha) BETWEEN ? AND ?
            """, (desde, hasta))

            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for fila in rows:
                self.tree.insert("", "end", values=(fila[0], fila[1], f"${fila[2]:,.2f}"))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los préstamos:\n{e}")

    def registrar_prestamo(self):
        fecha = self.fecha_prestamo.get_date().strftime("%Y-%m-%d")
        descripcion = self.entry_descripcion.get().strip()
        monto_str = self.entry_monto.get().replace(",", ".").strip()

        if not descripcion or not monto_str:
            messagebox.showwarning("Campos incompletos", "Por favor, complete todos los campos.")
            return

        try:
            monto = float(monto_str)
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido.")
            return

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO prestamos (fecha, descripcion, monto)
                VALUES (?, ?, ?)
            """, (fecha, descripcion, monto))
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Préstamo registrado correctamente.")
            self.entry_descripcion.delete(0, tk.END)
            self.entry_monto.delete(0, tk.END)
            self.cargar_datos()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el préstamo:\n{e}")
