import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from ui.flujo_caja_ventana import FlujoCaja
from logica.estado_resultados import EstadoResultados
from logica.balance_general import BalanceGeneral
from logica.deudas_proveedores import DeudasProveedores
from ui.prestamos_ventana import PrestamosVentana
from logica.historial_contable_mes import HistorialContableMes
from logica.punto_equilibrio import PuntoEquilibrio
from logica.gastos import GastosVentana
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import os

class ReporteUtilidad(tk.Toplevel):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    db_name = os.path.join(base_path, "database.db")

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reporte de Utilidad")
        self.geometry("1000x600")
        self.config(bg="#c6d9e3")
        self.resizable(False, False)

        self.master.lector_habilitado = False  # 🔴 DESACTIVAR EL LECTOR DE CÓDIGO DE BARRAS
        self.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

         

        self.widgets()

    def rutas(self, ruta):
        try:
            rutabase = sys._MEIPASS
        except Exception:
            rutabase=os.path.abspath(".")
        return os.path.join(rutabase,ruta)    

    def widgets(self):
        titulo = tk.Label(self, text="Reporte de Ventas y Utilidad", bg="#c6d9e3", font="sans 20 bold")
        titulo.pack(pady=10)

        filtros_frame = tk.Frame(self, bg="#c6d9e3")
        filtros_frame.pack()

        tk.Label(filtros_frame, text="Desde:", bg="#c6d9e3", font="sans 12 bold").grid(row=0, column=0, padx=5)
        self.fecha_desde = DateEntry(filtros_frame, font="sans 12", width=12, background="darkblue", foreground="white", borderwidth=2)
        self.fecha_desde.grid(row=0, column=1, padx=5)

        tk.Label(filtros_frame, text="Hasta:", bg="#c6d9e3", font="sans 12 bold").grid(row=0, column=2, padx=5)
        self.fecha_hasta = DateEntry(filtros_frame, font="sans 12", width=12, background="darkblue", foreground="white", borderwidth=2)
        self.fecha_hasta.grid(row=0, column=3, padx=5)

        self.btn_filtrar = tk.Button(filtros_frame, text="Filtrar", font="sans 12 bold", bg="#dddddd", command=self.cargar_reporte)
        self.btn_filtrar.grid(row=0, column=4, padx=10)

        self.tree_frame = tk.Frame(self, bg="#c6d9e3")
        self.tree_frame.pack(pady=10)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("Producto", "Proveedor", "Cantidad", "Ventas", "Utilidad", "% Utilidad"),
            show="headings",
            height=10
        )

        for col in ("Producto", "Proveedor", "Cantidad", "Ventas", "Utilidad", "% Utilidad"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=140)

        self.tree.pack()

        self.label_total_ventas = tk.Label(self, text="Total Ventas: $0", bg="#c6d9e3", font="sans 14 bold")
        self.label_total_ventas.pack()

        self.label_total_utilidad = tk.Label(self, text="Total Utilidad: $0", bg="#c6d9e3", font="sans 14 bold")
        self.label_total_utilidad.pack()

        self.btn_grafico = tk.Button(self, text="Ver Gráfico", font="sans 12 bold", bg="green", fg="white", command=self.mostrar_grafico)
        self.btn_grafico.pack(pady=10)

        self.btn_contabilidad = tk.Button(self, text="Contabilidad", font="sans 12 bold", bg="#4444aa", fg="white", command=self.abrir_menu_contabilidad)
        self.btn_contabilidad.pack(pady=10)


    def cargar_reporte(self):
        try:
            fecha_desde = self.fecha_desde.get_date().strftime("%Y-%m-%d")
            fecha_hasta = self.fecha_hasta.get_date().strftime("%Y-%m-%d")

            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()

            query = '''
                SELECT 
                    v.nombre_articulo, 
                    i.proveedor, 
                    SUM(v.cantidad), 
                    SUM(v.subtotal), 
                    SUM(v.subtotal - (v.cantidad * i.costo))  -- 💡 FORMULA UTILIDAD ABSOLUTA
                FROM ventas_historico v
                JOIN inventario i ON v.nombre_articulo = i.nombre
                WHERE i.costo > 0 AND DATE(v.fecha) BETWEEN ? AND ?
                GROUP BY v.nombre_articulo, i.proveedor
            '''

            c.execute(query, (fecha_desde, fecha_hasta))
            resultados = c.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            total_ventas = 0
            total_utilidad = 0

            for nombre, proveedor, cantidad, ventas, utilidad in resultados:
                total_ventas += ventas
                total_utilidad += utilidad

                # 📊 FORMULA PORCENTAJE DE UTILIDAD
                porcentaje_utilidad = (utilidad / ventas * 100) if ventas != 0 else 0
                porcentaje_utilidad = round(porcentaje_utilidad, 2)

                self.tree.insert("", "end", values=(
                    nombre, proveedor, cantidad, f"${ventas:,.2f}", f"${utilidad:,.2f}", f"{porcentaje_utilidad:.2f}%"
                ))

            self.label_total_ventas.config(text=f"Total Ventas: ${total_ventas:,.2f}")
            self.label_total_utilidad.config(text=f"Total Utilidad: ${total_utilidad:,.2f}")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar el reporte: {e}")

    def mostrar_grafico(self):
        productos = []
        utilidades = []

        for item in self.tree.get_children():
            valores = self.tree.item(item, "values")
            productos.append(valores[0])
            utilidades.append(float(valores[4].replace("$", "").replace(",", "")))

        if not productos:
            messagebox.showinfo("Información", "No hay datos para mostrar en el gráfico.")
            return

        plt.figure(figsize=(10, 5))
        plt.barh(productos, utilidades, color='skyblue')
        plt.xlabel("Utilidad ($)")
        plt.ylabel("Producto")
        plt.title("Productos más rentables")
        plt.gca().invert_yaxis()
        plt.show()

        #CONTABILIDAD

    def abrir_menu_contabilidad(self):
        ventana = tk.Toplevel(self)
        ventana.title("Módulo de Contabilidad")
        ventana.config(bg="#f5f7fa")
        ventana.resizable(False, False)

    # --- Centrar la ventana ---
        ventana.update_idletasks()
        width = 420
        height = 620
        x = (ventana.winfo_screenwidth() // 2) - (width // 2)
        y = (ventana.winfo_screenheight() // 2) - (height // 2)
        ventana.geometry(f"{width}x{height}+{x}+{y}")

    # --- Control lector ---
        self.master.lector_habilitado = False
        def cerrar_menu():
            self.master.lector_habilitado = True
            ventana.destroy()
        ventana.protocol("WM_DELETE_WINDOW", cerrar_menu)

    # --- Título ---
        tk.Label(ventana, text="Menú Contable", font=("Arial", 20, "bold"), bg="#f5f7fa", fg="#222831").pack(pady=20)

    # --- Contenedor botones ---
        frame_botones = tk.Frame(ventana, bg="#f5f7fa")
        frame_botones.pack()

        botones = [
            ("Balance General", "#2c3e90"),
            ("Estado de Resultados", "#20877c"),
            ("Flujo de Caja", "#3ba69c"),
            ("Deudas a Proveedores", "#e97429"),
            ("Préstamos", "#cc4a3d"),
            ("Gastos Fijos y Variables", "#607d8b"),
            ("Punto de Equilibrio", "#4caf50"),
            ("Historial Contable por Mes", "#673ab7"),
        ]

        for texto, color in botones:
            if texto == "Flujo de Caja":
                accion = lambda v=ventana: self.abrir_flujo_caja(v)
            elif texto == "Estado de Resultados":
                accion = lambda v=ventana: self.abrir_estado_resultados(v)
            elif texto == "Balance General":
                accion = lambda v=ventana: self.abrir_balance_general(v)
            elif texto == "Deudas a Proveedores":
                accion = lambda v=ventana: self.abrir_deudas_proveedores(v)
            elif texto == "Préstamos":
                accion = lambda v=ventana: self.abrir_prestamos(v)
            elif texto == "Historial Contable por Mes":
                accion = lambda v=ventana: self.abrir_historial_contable_mes(v)
            elif texto == "Gastos Fijos y Variables":
                accion = lambda v=ventana: self.abrir_gastos(v)     
            elif texto == "Punto de Equilibrio":
                accion = lambda v=ventana: self.abrir_punto_equilibrio(v)    


            btn = tk.Button(
                frame_botones,
                text=texto,
                font=("Arial", 12, "bold"),
                bg=color,
                fg="white",
                width=30,
                height=2,
                activebackground=color,
                relief="flat",
                cursor="hand2",
                command=accion  # ✅ Agrega la acción aquí
            )
            btn.pack(pady=8)

        #//////////////////

    def abrir_flujo_caja(self, ventana_menu):
        ventana_menu.destroy()  # Cierra el menú contable antes
        top = tk.Toplevel(self)
        FlujoCaja(top)   

    def abrir_estado_resultados(self, ventana_menu):
        ventana_menu.destroy()
        top = tk.Toplevel(self)
        EstadoResultados(top)

    def abrir_balance_general(self, ventana_menu):
        ventana_menu.destroy()
        top = tk.Toplevel(self)
        BalanceGeneral(top)

    def abrir_deudas_proveedores(self, ventana_menu):
        ventana_menu.destroy()
        top = tk.Toplevel(self)
        DeudasProveedores(top)   

    def abrir_prestamos(self, ventana_menu):
        ventana_menu.destroy()
        top = tk.Toplevel(self)
        PrestamosVentana(top) 

    def abrir_gastos(self, ventana_menu):
        ventana_menu.destroy()
        top = tk.Toplevel(self)
        from logica.gastos import GastosVentana
        GastosVentana(top)    

    def abrir_punto_equilibrio(self, ventana_menu):
        ventana_menu.destroy()
        top = tk.Toplevel(self)
        from logica.punto_equilibrio import PuntoEquilibrio
        PuntoEquilibrio(top)            

    def cerrar_ventana(self):
        self.master.lector_habilitado = True
        self.destroy()

    def abrir_historial_contable_mes(self, ventana_menu):
        ventana_menu.destroy()
        top = tk.Toplevel(self)
        HistorialContableMes(top)
    

# ✅ FUNCIÓN EXTERNA PARA ABRIR EL REPORTE
def abrir_reporte(parent):
    ReporteUtilidad(parent)

def abrir_prestamos(parent):
    PrestamosVentana(parent)    
