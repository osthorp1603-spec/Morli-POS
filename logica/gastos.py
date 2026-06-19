import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import sys
import os

def rutas(self, ruta):
        try:
            rutabase = sys._MEIPASS
        except Exception:
            rutabase=os.path.abspath(".")
        return os.path.join(rutabase,ruta) 

class GastosVentana:
    def __init__(self, master):
        self.master = master
        self.master.title("Registro de Gastos Fijos y Variables")
        self.master.config(bg="#f5f7fa")
        self.master.geometry("1230x600")
        self.master.resizable(False, False)

        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        self.conn = sqlite3.connect(os.path.join(base_path, "database.db"))

        self.cursor = self.conn.cursor()
        self.crear_tablas()

        tk.Label(master, text="Registrar Gastos", font=("Arial", 18, "bold"), bg="#f5f7fa").pack(pady=10)

        frame_contenedor = tk.Frame(master, bg="#f5f7fa")
        frame_contenedor.pack(pady=10)

        # ------------------------
        # Frame Gastos Fijos
        # ------------------------
        frame_fijos = tk.LabelFrame(frame_contenedor, text="Gastos Fijos", font=("Arial", 12, "bold"), bg="#e3f2fd")
        frame_fijos.grid(row=0, column=0, padx=20, pady=10)

        tk.Label(frame_fijos, text="Concepto:", bg="#e3f2fd").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_concepto_fijo = tk.Entry(frame_fijos, width=25)
        self.entry_concepto_fijo.grid(row=1, column=0, padx=10)

        tk.Label(frame_fijos, text="Cantidad:", bg="#e3f2fd").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entry_cantidad_fijo = tk.Entry(frame_fijos, width=25)
        self.entry_cantidad_fijo.grid(row=3, column=0, padx=10)

        btn_fijo = tk.Button(frame_fijos, text="Guardar Gasto Fijo", bg="#1976d2", fg="white",
                             font=("Arial", 10, "bold"), command=self.guardar_fijo)
        btn_fijo.grid(row=4, column=0, pady=10)

        # ------------------------
        # Frame Gastos Variables
        # ------------------------
        frame_variables = tk.LabelFrame(frame_contenedor, text="Gastos Variables", font=("Arial", 12, "bold"), bg="#fce4ec")
        frame_variables.grid(row=0, column=1, padx=20, pady=10)

        tk.Label(frame_variables, text="Concepto:", bg="#fce4ec").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_concepto_variable = tk.Entry(frame_variables, width=25)
        self.entry_concepto_variable.grid(row=1, column=0, padx=10)

        tk.Label(frame_variables, text="Cantidad:", bg="#fce4ec").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entry_cantidad_variable = tk.Entry(frame_variables, width=25)
        self.entry_cantidad_variable.grid(row=3, column=0, padx=10)

        btn_variable = tk.Button(frame_variables, text="Guardar Gasto Variable", bg="#c2185b", fg="white",
                                 font=("Arial", 10, "bold"), command=self.guardar_variable)
        btn_variable.grid(row=4, column=0, pady=10)

        # ------------------------
        # Tablas para mostrar gastos
        # ------------------------
        frame_tablas = tk.Frame(master, bg="#f5f7fa")
        frame_tablas.pack(pady=10)

        # Tabla Fijos
        tk.Label(frame_tablas, text="Gastos Fijos Registrados", font=("Arial", 12, "bold"), bg="#f5f7fa").grid(row=0, column=0, padx=20)
        self.tree_fijos = ttk.Treeview(frame_tablas, columns=("Descripción", "Valor", "Fecha"), show="headings", height=8)
        for col in ("Descripción", "Valor", "Fecha"):
            self.tree_fijos.heading(col, text=col)
            self.tree_fijos.column(col, width=180)
        self.tree_fijos.grid(row=1, column=0, padx=20)

        # Tabla Variables
        tk.Label(frame_tablas, text="Gastos Variables Registrados", font=("Arial", 12, "bold"), bg="#f5f7fa").grid(row=0, column=1, padx=20)
        self.tree_variables = ttk.Treeview(frame_tablas, columns=("Descripción", "Valor", "Fecha"), show="headings", height=8)
        for col in ("Descripción", "Valor", "Fecha"):
            self.tree_variables.heading(col, text=col)
            self.tree_variables.column(col, width=180)
        self.tree_variables.grid(row=1, column=1, padx=20)

        self.cargar_gastos()

    def crear_tablas(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos_fijos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL,
                valor REAL NOT NULL,
                fecha TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos_variables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL,
                valor REAL NOT NULL,
                fecha TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def guardar_fijo(self):
        concepto = self.entry_concepto_fijo.get().strip()
        cantidad = self.entry_cantidad_fijo.get().strip()
        fecha = datetime.now().strftime("%Y-%m-%d")

        if not concepto or not cantidad:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos del gasto fijo.")
            return

        try:
            valor = float(cantidad)
            self.cursor.execute("INSERT INTO gastos_fijos (descripcion, valor, fecha) VALUES (?, ?, ?)",
                                (concepto, valor, fecha))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Gasto fijo registrado correctamente.")
            self.entry_concepto_fijo.delete(0, tk.END)
            self.entry_cantidad_fijo.delete(0, tk.END)
            self.cargar_gastos()
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número.")

    def guardar_variable(self):
        concepto = self.entry_concepto_variable.get().strip()
        cantidad = self.entry_cantidad_variable.get().strip()
        fecha = datetime.now().strftime("%Y-%m-%d")

        if not concepto or not cantidad:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos del gasto variable.")
            return

        try:
            valor = float(cantidad)
            self.cursor.execute("INSERT INTO gastos_variables (descripcion, valor, fecha) VALUES (?, ?, ?)",
                                (concepto, valor, fecha))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Gasto variable registrado correctamente.")
            self.entry_concepto_variable.delete(0, tk.END)
            self.entry_cantidad_variable.delete(0, tk.END)
            self.cargar_gastos()
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número.")

    def cargar_gastos(self):
        # Limpiar tablas
        for row in self.tree_fijos.get_children():
            self.tree_fijos.delete(row)
        for row in self.tree_variables.get_children():
            self.tree_variables.delete(row)

        # Cargar gastos fijos
        self.cursor.execute("SELECT descripcion, valor, fecha FROM gastos_fijos ORDER BY fecha DESC")
        for fila in self.cursor.fetchall():
            self.tree_fijos.insert("", tk.END, values=fila)

        # Cargar gastos variables
        self.cursor.execute("SELECT descripcion, valor, fecha FROM gastos_variables ORDER BY fecha DESC")
        for fila in self.cursor.fetchall():
            self.tree_variables.insert("", tk.END, values=fila)
