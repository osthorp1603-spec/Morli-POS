from tkinter import simpledialog, messagebox
from tkinter import *
import tkinter as tk
from ui.ventas import Ventas
from ui.inventario import Inventario
from ui.anchetas import Anchetas 
from logica.generar_codigo import abrir_ventana_generar
from logica.reporte_utilidad import abrir_reporte
from ui.clientes import ClientesVentana
from PIL import Image, ImageTk
import sys
import os

class Container(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre)
        self.controlador = controlador
        self.pack()
        self.place(x=0,y=0,width=800,height=480)
        self.config(bg="#c6d9e3")

       

        self.widgets()

    def rutas(self, ruta):
        try:
            rutabase = sys._MEIPASS
        except Exception:
            rutabase=os.path.abspath(".")
        return os.path.join(rutabase,ruta)    
       
 #FUNCION QUE MUESTRA LAS VENTANAS
    def show_frames(self, container, geometry="1300x720+140+40"):
        top_level = tk.Toplevel(self)
        frame = container(top_level)
        frame.config(bg="#c6d9e3")
        frame.pack(fill="both",expand=True)

        top_level.geometry(geometry)
        top_level.resizable(False, False)

        ruta=self.rutas(r"icono.ico")
        top_level.iconbitmap(ruta)

        top_level.transient(self.master)
        top_level.grab_set()
        top_level.focus_set()
        top_level.lift()

    def ventas(self):
        """Abrir Ventas con tamaño específico."""
        self.show_frames(Ventas, "1100x650+140+40") 

    def abrir_clientes(self):
        self.show_frames(ClientesVentana, "1100x600+150+60")
            

    def inventario(self):
        """Abrir Inventario con tamaño específico."""
        self.show_frames(Inventario, "1300x730+140+40")

    def reportes(self):
        """Abrir Reportes."""
        clave = simpledialog.askstring("Acceso restringido", "Ingresa la clave:", show="*")
    
        if clave is None:
            return

        if clave.strip() == "Imagine":
            abrir_reporte(self)
        else:
            messagebox.showerror("Error", "Clave incorrecta.")

    def widgets(self):
        frame1 = tk.Frame(self, bg="#c6d9e3")
        frame1.pack()
        frame1.place(x=0,y=0,width=800,height=480)

        btnventas = Button(frame1, bg="violet red", fg="white",font="sans 18 bold", text="VENTAS",command=self.ventas)
        btnventas.place(x=500,y=30,width=240,height=60)

        btninventario = Button(frame1, bg="turquoise1", fg="white",font="sans 18 bold",text="INVENTARIO",command=self.inventario)
        btninventario.place(x=500,y=130,width=240,height=60) 

        btnreportes = Button(frame1, bg="blue", fg="white", font="sans 18 bold", text="REPORTES", command=self.reportes)
        btnreportes.place(x=500, y=230, width=240, height=60)

        btngenerar = Button(frame1, bg="dark green", fg="white", font="sans 10 bold",
                            text="COD_BARRA", command=lambda: abrir_ventana_generar(self))
        btngenerar.place(x=500,  y=320, width=120, height=38)

        btnclientes = Button(frame1, bg="dark orange", fg="white", font="sans 10 bold", text="CLIENTES", command=self.abrir_clientes)
        btnclientes.place(x=673, y=420, width=120, height=38)

        btn_anchetas = tk.Button(frame1, text="DECORACIONES",fg="white", command=Anchetas,font="sans 10 bold" , bg="#DDA0DD")
        btn_anchetas.place(x=673, y=372,width=120, height=38) 

        btn_arqueo = Button(frame1, bg="#3A6EA5", fg="white", font="sans 10 bold",
                            text="ARQUEO", command=self.abrir_arqueo)
        btn_arqueo.place(x=500, y=370, width=120, height=38)

        btn_egresos = Button(frame1, bg="#cc4a3d", fg="white", font="sans 9 bold",
                             text="SALIDA EFECTIVO", command=self.abrir_egresos)
        btn_egresos.place(x=500, y=420, width=120, height=38)
         
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        ruta_logo = os.path.join(base_path, "imagenes", "logolocal.png")

        self.logo_image = Image.open(ruta_logo)
        self.logo_image = self.logo_image.resize((280, 280))
        self.logo_image = ImageTk.PhotoImage(self.logo_image)

        self.logo_label = tk.Label(frame1, image=self.logo_image, bg="#c6d9e3")
        self.logo_label.place(x=100, y=30)


        copyright_label = tk.Label(frame1 ,text="© 2025 MorliGiftstore. Todos los derechos reservados",font="sans 12 bold",
                               bg="#C6D9E3",fg="gray")
        copyright_label.place(x=40, y=350)

    def abrir_arqueo(self):
        ventana = tk.Toplevel(self)
        ventana.title("Arqueo de Caja")
        ventana.geometry("400x300")
        ventana.resizable(False, False)
        ventana.config(bg="#f4f4f4")

        tk.Label(ventana, text="Arqueo de Caja", font=("Arial", 16, "bold"), bg="#f4f4f4").pack(pady=20)

        tk.Label(ventana, text="Monto contado en caja:", font=("Arial", 12), bg="#f4f4f4").pack()

        entry_monto = tk.Entry(ventana, font=("Arial", 12), justify="center")
        entry_monto.pack(pady=10)

        def guardar_arqueo():
            try:
                monto = float(entry_monto.get())
                from datetime import datetime
                fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                try:
                    base_path = sys._MEIPASS
                except AttributeError:
                    base_path = os.path.abspath(".")
                db_path = os.path.join(base_path, "database.db")

                import sqlite3
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute("""
                    CREATE TABLE IF NOT EXISTS arqueo_caja (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha_hora TEXT,
                        monto REAL
                    )
                """)
                c.execute("INSERT INTO arqueo_caja (fecha_hora, monto) VALUES (?, ?)", (fecha_hora, monto))
                conn.commit()
                conn.close()

                messagebox.showinfo("Éxito", "Arqueo de caja registrado correctamente.")
                ventana.destroy()

            except ValueError:
                messagebox.showerror("Error", "Ingresa un número válido.")

        tk.Button(ventana, text="Guardar", bg="#3A6EA5", fg="white", font=("Arial", 11, "bold"),
                  command=guardar_arqueo).pack(pady=20)

        ventana.transient(self.master)
        ventana.grab_set()
        ventana.focus_set()
        ventana.lift()

    def abrir_egresos(self):
        ventana = tk.Toplevel(self)
        ventana.title("Registrar Gasto Operativo")
        ventana.geometry("400x300")
        ventana.resizable(False, False)
        ventana.config(bg="#f4f4f4")

        tk.Label(ventana, text="Registrar Gasto Operativo", font=("Arial", 16, "bold"), bg="#f4f4f4").pack(pady=15)

        tk.Label(ventana, text="Motivo del gasto:", font=("Arial", 12), bg="#f4f4f4").pack()
        entry_motivo = tk.Entry(ventana, font=("Arial", 12), justify="center")
        entry_motivo.pack(pady=5)

        tk.Label(ventana, text="Monto:", font=("Arial", 12), bg="#f4f4f4").pack()
        entry_monto = tk.Entry(ventana, font=("Arial", 12), justify="center")
        entry_monto.pack(pady=5)

        def guardar_egreso():
            motivo = entry_motivo.get().strip()
            try:
                monto = float(entry_monto.get())
                if not motivo:
                    raise ValueError("Motivo vacío.")

                from datetime import datetime
                fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                try:
                    base_path = sys._MEIPASS
                except AttributeError:
                    base_path = os.path.abspath(".")
                db_path = os.path.join(base_path, "database.db")

                import sqlite3
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute("""
                    CREATE TABLE IF NOT EXISTS egresos_dia (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha_hora TEXT,
                        motivo TEXT,
                        monto REAL,
                        metodo TEXT
                    )
                """)
                c.execute("INSERT INTO egresos_dia (fecha_hora, motivo, monto, metodo) VALUES (?, ?, ?, ?)",
                          (fecha_hora, motivo, monto, "Efectivo"))
                
                c.execute("INSERT INTO egresos_historial (fecha_hora, motivo, monto, metodo) VALUES (?, ?, ?, ?)",
                        (fecha_hora, motivo, monto, "Efectivo"))
                
                conn.commit()
                conn.close()


                # --- Enviar comando ESC/POS para abrir cajón ---
                try:
                    import win32print
                    nombre_impresora = "POSPrinter POS80"  # Cambia este nombre si tu impresora se llama diferente
                    hPrinter = win32print.OpenPrinter(nombre_impresora)
                    hJob = win32print.StartDocPrinter(hPrinter, 1, ("Abrir Cajón", None, "RAW"))
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, b"\x1B\x70\x00\x19\xFA")
                    win32print.EndPagePrinter(hPrinter)
                    win32print.EndDocPrinter(hPrinter)
                    win32print.ClosePrinter(hPrinter)
                except Exception as e:
                    print("No se pudo abrir el cajón:", e)

                messagebox.showinfo("Éxito", "Gasto operativo registrado correctamente.")
                ventana.destroy()

            except ValueError:
                messagebox.showerror("Error", "Por favor ingresa un motivo y un monto válido.")

        tk.Button(ventana, text="Guardar", bg="#cc4a3d", fg="white", font=("Arial", 11, "bold"),
                  command=guardar_egreso).pack(pady=15)

        ventana.transient(self.master)
        ventana.grab_set()
        ventana.focus_set()
        ventana.lift()

   
    
