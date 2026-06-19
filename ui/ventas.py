import sqlite3
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from datetime import datetime
from logica.rf import mover_a_rf_registros  
from utils.impresora_pos_profesional import imprimir_ticket_pos
from ui.movimientos_inventario import MovimientosInventario
import sys
import os

class Ventas(tk.Frame):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    db_name = os.path.join(base_path, "database.db")

    def __init__(self, parent):
        super().__init__(parent)
        self.numero_factura_actual = self.obtener_numero_factura_actual()  # Llamar función factura
        self.toplevel_listbox = None
        self.lector_habilitado = True 
        self.widgets()
        self.mostrar_numero_factura()

    def rutas(self, ruta):
        try:
            rutabase = sys._MEIPASS
        except Exception:
            rutabase=os.path.abspath(".")
        return os.path.join(rutabase,ruta)  

      

    def widgets(self):
        frame1 = tk.Frame(self, bg="#dddddd", highlightbackground="gray", highlightthickness=1)
        frame1.pack()
        frame1.place(x=0, y=0, width=1100, height=100)

        titulo = tk.Label(self, text="VENTAS", bg="#dddddd", font="sans 30 bold", anchor="center")
        titulo.pack()
        titulo.place(x=5, y=0, width=1090, height=90)

        frame2 = tk.Frame(self, bg="#c6d9e3", highlightbackground="gray", highlightthickness=1)
        frame2.place(x=0, y=100, width=1100, height=550)

        lblframe = LabelFrame(frame2, text="Informacion de la venta", bg="#c6d9e3", font="sans 16 bold")
        lblframe.place(x=10, y=10, width=1060, height=80)

        label_numero_factura = tk.Label(lblframe, text="Numero de \nfactura", bg="#c6d9e3", font="sans 12 bold")
        label_numero_factura.place(x=10, y=5)
        self.numero_factura = tk.StringVar()

        self.entry_numero_factura = ttk.Entry(lblframe, textvariable=self.numero_factura, state="readonly", font="sans 12 bold")
        self.entry_numero_factura.place(x=100, y=5, width=80)

        label_nombre = tk.Label(lblframe, text="Productos: ", bg="#c6d9e3", font="sans 12 bold")
        label_nombre.place(x=200, y=12)
        self.entry_nombre = ttk.Combobox(lblframe, font="sans 12 bold")        
        self.entry_nombre.place(x=280, y=10, width=180)
        self.entry_nombre.bind("<KeyRelease>", self.abrir_listbox_filtro)
        self.entry_nombre.bind("<FocusOut>", self.verificar_producto_manual)

        
        self.cargar_productos()

        label_valor = tk.Label(lblframe, text="Precio: ", bg="#c6d9e3", font="sans 12 bold")
        label_valor.place(x=470, y=12)
        self.entry_valor = ttk.Entry(lblframe, font="sans 12 bold")
        self.entry_valor.place(x=540, y=10, width=180)

        self.entry_nombre.bind("<<ComboboxSelected>>", self.actualizar_precio)

        label_cantidad = tk.Label(lblframe, text="Cantidad: ", font="sans 12 bold", bg="#c6d9e3")
        label_cantidad.place(x=730, y=12)
        self.entry_cantidad = ttk.Entry(lblframe, font="sans 12 bold")
        self.entry_cantidad.place(x=820, y=10)

        treFrame = tk.Frame(frame2, bg="#c6d9e3")
        treFrame.place(x=150, y=120, width=800, height=200)

        scrol_y = ttk.Scrollbar(treFrame, orient=VERTICAL)
        scrol_y.pack(side=RIGHT, fill=Y)

        scrol_x = ttk.Scrollbar(treFrame, orient=HORIZONTAL)
        scrol_x.pack(side=BOTTOM, fill=X)

        self.tree = ttk.Treeview(treFrame, columns=("Producto", "Precio", "Cantidad", "Subtotal"),
                                 show="headings", height=10, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set)
        scrol_y.config(command=self.tree.yview)
        scrol_x.config(command=self.tree.xview)

        self.tree.heading("#1", text="Producto")
        self.tree.heading("#2", text="Precio")
        self.tree.heading("#3", text="Cantidad")
        self.tree.heading("#4", text="Subtotal")

        self.tree.column("Producto", anchor="center")
        self.tree.column("Precio", anchor="center")
        self.tree.column("Cantidad", anchor="center")
        self.tree.column("Subtotal", anchor="center")

        self.tree.pack(expand=True, fill=BOTH)

        lblframe1 = LabelFrame(frame2, text="Opciones", bg="#c6d9e3", font="sans 12 bold")
        lblframe1.place(x=10, y=380, width=1060, height=150)

        boton_agregar = tk.Button(lblframe1, text="Agregar Articulo", bg="#dddddd", font="sans 12 bold", command=self.registrar)
        boton_agregar.place(x=50, y=10, width=240, height=50)

        boton_pagar = tk.Button(lblframe1, text="Pagar", bg="#dddddd", font="sans 12 bold", command=self.abrir_ventana_pago)
        boton_pagar.place(x=400, y=10, width=240, height=50)

        boton_ver_facturas = tk.Button(lblframe1, text="Venta Diaria", bg="#dddddd", font="sans 12 bold", 
                                        command=self.abrir_ventana_resumen_dia)
        boton_ver_facturas.place(x=750, y=10, width=240, height=50)

        self.label_suma_total = tk.Label(frame2, text="Total a pagar: $ 0", bg="#c6d9e3", font="sans 25 bold")
        self.label_suma_total.place(x=360, y=335)

        # Botón RF para eliminar productos o cancelar venta
        boton_rf = tk.Button(lblframe1, text="Cancelar Venta (RF)", bg="red", fg="white", font="sans 12 bold",
                            command=lambda: mover_a_rf_registros(self.tree, self.actualizar_total))
        boton_rf.place(x=400, y=70, width=240, height=50)

       #CODIGO DE BARRAS
        self.entry_codigo_oculto = ttk.Entry(self)
        self.entry_codigo_oculto.place(x=-100, y=-100, width=1, height=1)  # Fuera de vista
        self.entry_codigo_oculto.bind("<Return>", self.leer_codigo_barras)
        self.entry_codigo_oculto.focus_set()
        self.after(1000, self.reestablecer_foco_lector)

           
    def recalcular_total(self):
        total = 0
        for item in self.tree.get_children():
            valores = self.tree.item(item, "values")
            precio = float(valores[1])  # Suponiendo que el precio está en la tercera columna
            cantidad = int(valores[2])  # Suponiendo que la cantidad está en la segunda columna
            total += precio * cantidad
            

        self.label_suma_total.config(text=f"Total: ${total:,.2f}")

    def actualizar_ventas(self):
        # Función para actualizar la lista de ventas en la interfaz
        pass
                    
    def verificar_producto_manual(self, event):
        nombre_producto = self.entry_nombre.get().strip().lower()

        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()

        # Traer precio, es_servicio y stock en una sola consulta
            c.execute("SELECT precio, es_servicio, stock FROM inventario WHERE LOWER(nombre) = ?", (nombre_producto,))
            resultado = c.fetchone()
            conn.close()

            if resultado:
                precio, es_servicio, stock = resultado

                if stock <= 0:
                    messagebox.showerror("Error", "No hay suficiente stock para este producto.")
                    return

                if es_servicio == 1:
                    self.entry_valor.config(state="normal")
                    self.entry_valor.delete(0, tk.END)
                    self.entry_cantidad.config(state="normal")
                    self.entry_cantidad.delete(0, tk.END)
                    self.entry_valor.focus_set()
                    self.lector_habilitado = False
                else:
                    self.lector_habilitado = True
                    self.actualizar_precio(None)
            else:
            # Producto no registrado
                self.entry_valor.config(state="normal")
                self.entry_valor.delete(0, tk.END)
                self.entry_valor.insert(0, "0")
                self.entry_cantidad.delete(0, tk.END)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al verificar el producto: {e}")    

    def abrir_listbox_filtro(self, event):
        texto = self.entry_nombre.get() 

        if event.keysym in ["Right", "Left"]:
            if self.toplevel_listbox and self.toplevel_listbox.winfo_exists():
                self.listbox_filtro.focus_set()
                self.listbox_filtro.select_set(0) 
                return

        if event.keysym == "Return":
            if self.toplevel_listbox and self.toplevel_listbox.winfo_exists():
                current_selection = self.listbox_filtro.curselection()
                if not current_selection and self.listbox_filtro.size()>0:
                    self.listbox_filtro.select_set(0)
                    current_selection = self.listbox_filtro.curselection()

                if current_selection:
                    producto_seleccionado = self.listbox_filtro.get(current_selection)
                    self.entry_nombre.set(producto_seleccionado)
                    self.toplevel_listbox.destroy()

                    self.actualizar_precio(None)
            return           

        if not texto:
            if self.toplevel_listbox and self.toplevel_listbox.winfo_exists():
                self.toplevel_listbox.destroy()
            return
            
        if not self.toplevel_listbox or not self.toplevel_listbox.winfo_exists():  
            self.toplevel_listbox = Toplevel(self)
            self.toplevel_listbox.title("Filtrar productos")
            self.toplevel_listbox.geometry("300x200+400+250")
            self.toplevel_listbox.transient(self)
            self.toplevel_listbox.resizable(False, False)

            self.listbox_filtro = Listbox(self.toplevel_listbox, font="sans 12")
            self.listbox_filtro.pack(fill=BOTH, expand=True)

            self.vincular_eventos_listbox()

            self.listbox_filtro.bind("<Down>", self.mover_abajo_listbox)
            self.listbox_filtro.bind("<Up>", self.mover_arriba_listbox)
            self.listbox_filtro.bind("<Return>", self.seleccionar_producto)
            self.listbox_filtro.bind("<Button-1>", self.seleccionar_producto)

        self.listbox_filtro.delete(0, END)
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT nombre FROM inventario WHERE nombre LIKE ?", (f"%{texto}%",))
            productos = c.fetchall()
            for producto in productos:   
                self.listbox_filtro.insert(END, producto[0])
            conn.close()  
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al filtrar productos: {e}")    

    #ENTRADA LECTOR CODIGO DE BARRAS
    def leer_codigo_barras(self, event):
        codigo = self.entry_codigo_oculto.get().strip()

        if not self.validar_stock_por_codigo(codigo):
            messagebox.showwarning("Stock insuficiente", "Este producto no tiene stock disponible.")
            self.entry_codigo_oculto.delete(0, tk.END)
            return

        if not codigo:
            return

        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT nombre, precio, es_servicio FROM inventario WHERE codigo_barras = ?", (codigo,))
            resultado = c.fetchone()
            conn.close()

            if not resultado:
                messagebox.showwarning("Código no encontrado", f"El código {codigo} no está registrado.")
                self.entry_codigo_oculto.delete(0, tk.END)
                return

            nombre, precio, es_servicio = resultado

            if es_servicio == 1:
                self.entry_nombre.set(nombre)

                self.entry_valor.config(state="normal")
                self.entry_valor.delete(0, tk.END)

                self.entry_cantidad.config(state="normal")
                self.entry_cantidad.delete(0, tk.END)

                self.entry_codigo_oculto.delete(0, tk.END)

                self.lector_habilitado = False  

    # 🔁 Agregamos un pequeño retraso para que focus no interrumpa la escritura
                self.after(10, lambda: self.entry_valor.focus_force())
                return
        # Revisar si ya está en el Treeview
            for item in self.tree.get_children():
                valores = self.tree.item(item, "values")
                if valores[0] == nombre:
                    cantidad_actual = int(valores[2])
                    nueva_cantidad = cantidad_actual + 1
                    subtotal = nueva_cantidad * precio
                    self.tree.item(item, values=(nombre, f"{precio:,.0f}", nueva_cantidad, f"{subtotal:,.0f}"))
                    self.actualizar_total()
                    self.entry_codigo_oculto.delete(0, tk.END)
                    return

        # Si no está, agregarlo
            self.tree.insert("", "end", values=(nombre, f"{precio:,.0f}", 1, f"{precio:,.0f}"))
            self.actualizar_total()
            self.entry_codigo_oculto.delete(0, tk.END)

            # Guardar en ventas_temp solo si no está repetido
            try:
                with sqlite3.connect(self.db_name) as conn:
                    c = conn.cursor()
                    c.execute("""
                        SELECT COUNT(*) FROM ventas_temp
                        WHERE nombre_articulo = ? AND valor_articulo = ? AND cantidad = ? AND subtotal = ?
                    """, (nombre, precio, 1, precio))  # subtotal = precio x 1
                    existe = c.fetchone()[0]

                    if existe == 0:
                        c.execute("SELECT MAX(factura) FROM ventas_temp")
                        max_factura_result = c.fetchone()
                        max_factura = max_factura_result[0] if max_factura_result and max_factura_result[0] is not None else 0
                        factura = max_factura + 1

                        c.execute("""
                            INSERT INTO ventas_temp (factura, nombre_articulo, valor_articulo, cantidad, subtotal, fecha)
                            VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
                        """, (factura, nombre, precio, 1, precio))
                        conn.commit()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo guardar el producto en ventas_temp: {e}")


        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo buscar el producto: {e}")

    def reestablecer_foco_lector(self):
        if not self.winfo_ismapped():  # ❌ No está visible, no hacer nada
            return

        if self.lector_habilitado:
            try:
                widget_actual = self.focus_get()
                if widget_actual not in [self.entry_valor, self.entry_cantidad, self.entry_nombre]:
                    self.entry_codigo_oculto.focus_set()
            except:
                pass

        self.after(1000, self.reestablecer_foco_lector)  

     
    def mover_abajo_listbox(self, event):
        if hasattr(self, 'listbox_filtro'):
            current_selection = self.listbox_filtro.curselection()
            if not current_selection:
                 index = 0
                 
            else:
                 index = current_selection[0]
                 if index < self.listbox_filtro.size() - 1:
                     self.listbox_filtro.select_clear(index)
                     index +=1
                     self.listbox_filtro.select_set(index)
                     self.listbox_filtro.activate(index)  

    def mover_arriba_listbox(self, event):
        if hasattr(self, 'listbox_filtro'):
             current_selection = self.listbox_filtro.curselection()
             if not current_selection:
                   index = 0
             else:
                 index = current_selection[0]
                 if index > 0:
                    self.listbox_filtro.select_clear(index)
                    index -= 1
                    self.listbox_filtro.select_set(index)
                    self.listbox_filtro.activate(index)

    def vincular_eventos_listbox(self):
        self.listbox_filtro.bind("<Right>", self.enfocar_entry_nombre)
        self.listbox_filtro.bind("<Left>", self.enfocar_entry_nombre)    

    def enfocar_entry_nombre(self, event):
        self.entry_nombre.focus_set()                

    def seleccionar_producto(self, event):
        if hasattr(self, 'listbox_filtro'):
             current_selection = self.listbox_filtro.curselection()
             if current_selection:
                producto_seleccionado = self.listbox_filtro.get(current_selection)
                self.entry_nombre.set(producto_seleccionado)  # Insertar en el combobox
                self.toplevel_listbox.destroy()  # Cerrar el Toplevel 

                self.actualizar_precio(None)      
                                         
  
    def cargar_productos(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT nombre FROM inventario")
            productos = c.fetchall()
            self.entry_nombre["values"] = [producto[0] for producto in productos]
            if not productos:
                print("No se encontraron productos en la base de datos")
            conn.close()
        except sqlite3.Error as e:
            print("Error al cargar productos desde la base de datos: ", e)

    def actualizar_precio(self, event):
        nombre_producto = self.entry_nombre.get()
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT precio FROM inventario WHERE nombre = ?", (nombre_producto,))
            precio = c.fetchone()
            if precio:
                self.entry_valor.config(state="normal")
                self.entry_valor.delete(0, tk.END)
                self.entry_valor.insert(0, f"{precio[0]:,}")
                self.entry_valor.config(state="readonly")
            else:
                self.entry_valor.config(state="normal")
                self.entry_valor.delete(0, tk.END)
                self.entry_valor.insert(0, "Precio no disponible")
                self.entry_valor.config(state="readonly")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener el precio: {e}")
        finally:
            conn.close()

    def actualizar_total(self):
        total = 0.0
        for child in self.tree.get_children():
            subtotal = float(self.tree.item(child, "values")[3].replace(",", ""))
            total += subtotal
        self.label_suma_total.config(text=f"Total a pagar: $ {total:,.0f}")

    def registrar(self):
        producto = self.entry_nombre.get()
        precio = self.entry_valor.get().replace(",", "")
        cantidad = self.entry_cantidad.get()

        if not producto or not precio or not cantidad:
            messagebox.showerror("Error", "Debe completar todos los campos")
            return
        try:
            cantidad = int(cantidad)
            precio = float(precio)
            subtotal = cantidad * precio

            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT stock, es_servicio FROM inventario WHERE nombre = ?", (producto,))
            resultado = c.fetchone()
            conn.close()

            if resultado:
                stock_info, es_servicio = resultado


                if es_servicio == 0 and cantidad > stock_info:
                    messagebox.showerror("Error", "Stock insuficiente para el producto seleccionado")
                    return
               
                        
            subtotal_recalculado = cantidad * precio
            self.tree.insert("", "end", values=(producto, f"{precio:,.0f}", cantidad, f"{subtotal_recalculado:,.0f}"))

            self.guardar_en_ventas_temp(producto, precio, cantidad, subtotal)

            self.entry_nombre.set("")
            self.entry_valor.config(state="normal")
            self.entry_valor.delete(0, tk.END)
            self.entry_valor.config(state="readonly")
            self.entry_cantidad.delete(0, tk.END)

            self.actualizar_total()

            self.lector_habilitado = True  # 🔄 CAMBIO: volver a activar el foco del lector
            self.entry_codigo_oculto.focus_set()  
        except ValueError:
                messagebox.showerror("Error", "Cantidad o precio no válidos")
#/////////////////////////////////////////////////////////////////////////////////////
    def guardar_en_ventas_temp(self, producto, precio, cantidad, subtotal):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()

                c.execute("SELECT MAX(factura) FROM ventas_temp")
                max_factura = c.fetchone()[0]
                factura = max_factura + 1 if max_factura else 1  

                c.execute("""
                    INSERT INTO ventas_temp (factura, nombre_articulo, valor_articulo, cantidad, subtotal, fecha)
                    VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
                """, (factura, producto, precio, cantidad, subtotal))

                conn.commit()
          
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo guardar en ventas_temp: {e}")                               
          #//////////////////////////////////////////  
        

    def verificar_stock(self, nombre_producto, cantidad):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT stock FROM inventario WHERE nombre = ?", (nombre_producto,))
            stock = c.fetchone()
            if stock and stock[0] >= cantidad:
                return True
            return False
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al verificar el stock: {e}")
            return False
        finally:
            conn.close()

    def descontar_componentes_ancheta(self, cursor, nombre_ancheta, cantidad_vendida):
        cursor.execute("SELECT id FROM anchetas WHERE nombre = ?", (nombre_ancheta,))
        resultado = cursor.fetchone()

        if not resultado:
            return  # No es una ancheta

        id_ancheta = resultado[0]

        cursor.execute("SELECT id_producto, cantidad FROM ancheta_detalle WHERE id_ancheta = ?", (id_ancheta,))
        componentes = cursor.fetchall()

        for id_producto, cantidad_en_ancheta in componentes:
            cantidad_total = cantidad_en_ancheta * cantidad_vendida
            cursor.execute("UPDATE inventario SET stock = stock - ? WHERE id = ?", (cantidad_total, id_producto))  

    def es_ancheta(self, cursor, nombre_ancheta: str) -> bool:
        """
        Devuelve True si 'nombre_ancheta' existe en la tabla 'anchetas' (ignora mayúsculas/minúsculas y espacios).
        """
        cursor.execute(
            "SELECT 1 FROM anchetas WHERE TRIM(nombre) = TRIM(?) COLLATE NOCASE LIMIT 1",
            (nombre_ancheta,)
        )
        return cursor.fetchone() is not None              

    def obtener_total(self):
        total = 0.0
        for child in self.tree.get_children():
            subtotal = float(self.tree.item(child, "values")[3].replace(",", ""))
            total += subtotal
        return total

    def abrir_ventana_pago(self):
        if not self.tree.get_children():
            messagebox.showerror("Error", "No hay artículos para pagar")
            return
        
        self.lector_habilitado = False  

        ventana_pago = Toplevel(self)
        ventana_pago.title("Realizar pago")
        ventana_pago.geometry("1000x600")
        ventana_pago.config(bg="#c6d9e3")
        ventana_pago.resizable(False, False)

        ventana_pago.transient(self)
        ventana_pago.grab_set()
        ventana_pago.focus_force()

        ventana_pago.protocol("WM_DELETE_WINDOW", lambda: (setattr(self, "lector_habilitado", True), ventana_pago.destroy()))

        label_total = tk.Label(ventana_pago, bg="#c6d9e3", text=f"Total a pagar: ${self.obtener_total():,.0f}", font="sans 18 bold")
        label_total.place(x=380, y=20)

        label_cantidad_pagada = tk.Label(ventana_pago, bg="#c6d9e3", text="Cantidad pagada:", font="sans 14 bold")
        label_cantidad_pagada.place(x=410, y=90)

        var_cantidad_pagada = tk.StringVar()

        def formatear_con_coma(*args):
            widget = entry_cantidad_pagada
            texto = var_cantidad_pagada.get().replace(",", "").strip()

            if texto.isdigit():
                texto_formateado = "{:,}".format(int(texto))
                widget.delete(0, tk.END)
                widget.insert(0, texto_formateado)
                widget.icursor(tk.END)
            elif not texto:
                var_cantidad_pagada.set("")

        var_cantidad_pagada.trace_add("write", formatear_con_coma)

        entry_cantidad_pagada = ttk.Entry(ventana_pago, font="sans 14 bold", justify="center", textvariable=var_cantidad_pagada)
        entry_cantidad_pagada.place(x=380, y=130, width=240, height=40)

        label_cambio = tk.Label(ventana_pago, bg="#c6d9e3", text="", font="sans 14 bold")
        label_cambio.place(x=430, y=190)

        #FUNCION DE BOTONES NUEVOS

        def usar_billete(valor):
            entry_cantidad_pagada.delete(0, tk.END)
            entry_cantidad_pagada.insert(0, str(valor))

        valores_billetes = [5000, 10000, 20000, 50000, 100000]
        x_inicial = 90
        espacio = 175
        y_billetes = 250

        for i, valor in enumerate(valores_billetes):
            btn = tk.Button(ventana_pago, text=f"${valor:,}", font="sans 13 bold", fg="white", bg="#222222",activebackground="#222222",
                        command=lambda v=valor: usar_billete(v))
            btn.place(x=x_inicial + i * espacio, y=y_billetes, width=150, height=50)   


        def calcular_cambio():
            try:
                cantidad_pagada = float(entry_cantidad_pagada.get().replace(",", ""))
                total = self.obtener_total()
                cambio = cantidad_pagada - total
                if cambio < 0:
                    messagebox.showerror("Error", "La cantidad pagada es insuficiente")
                    return
                label_cambio.config(text=f"Vuelto: $ {cambio:,.0f}")
            except ValueError:
                messagebox.showerror("Error", "Cantidad pagada no válida")

        boton_calcular = tk.Button(ventana_pago, text="Calcular Vuelto", bg="white", font="sans 12 bold", command=calcular_cambio)
        boton_calcular.place(x=400, y=330, width=200, height=50)

        # BOTÓN: Efectivo
        boton_pagar_efectivo = tk.Button(
            ventana_pago,
            text="Pagar Efectivo",
            fg="white",
            bg="#2e8b57",  # Verde oscuro
            font="sans 12 bold",
            command=lambda: self.bloquear_calcular_y_pagar(boton_pagar_efectivo, ventana_pago, entry_cantidad_pagada, label_cambio, "Efectivo", calcular_cambio)

        )
        boton_pagar_efectivo.place(x=100, y=420, width=200, height=50)

# BOTÓN: QR
        boton_pagar_qr = tk.Button(
            ventana_pago,
            text="Pagar QR",
            bg="#3366cc",  # Azul (el que usabas para "Crédito")
            fg="white",
            font="sans 12 bold",
            command=lambda: self.bloquear_calcular_y_pagar(boton_pagar_qr,ventana_pago,entry_cantidad_pagada,  label_cambio,  "QR", lambda: self.completar_si_vacio(entry_cantidad_pagada, label_total))


        )
        boton_pagar_qr.place(x=400, y=420, width=200, height=50)

# BOTÓN: Tarjeta
        boton_pagar_tarjeta = tk.Button(
            ventana_pago,
            text="Pagar Tarjeta",
            bg="#e67e22",  # Naranja profesional
            fg="white",
            font="sans 12 bold",
            command=lambda: self.bloquear_calcular_y_pagar(boton_pagar_tarjeta, ventana_pago, entry_cantidad_pagada, label_cambio, "Tarjeta", lambda: self.completar_si_vacio(entry_cantidad_pagada, label_total))


        )
        boton_pagar_tarjeta.place(x=700, y=420, width=200, height=50)

        #boton dividido
        boton_pago_dividido = tk.Button(
            ventana_pago,
            text="Pago Dividido",
            bg="#8e44ad",  # Morado oscuro
            fg="white",
            font="sans 12 bold",
            command=lambda: self.abrir_pago_dividido(ventana_pago)
        )
        boton_pago_dividido.place(x=400, y=490, width=200, height=50)

    def bloquear_calcular_y_pagar(self, boton, ventana_pago, entry_cantidad_pagada, label_cambio, tipo_pago, calcular_func):
        boton.config(state="disabled")  # Bloquea el botón al primer clic
        calcular_func()  # Ejecuta primero calcular_cambio()
        self.pagar(ventana_pago, entry_cantidad_pagada, label_cambio, tipo_pago)

    


    #//////////////////////////

    def abrir_pago_dividido(self, ventana_padre):
        ventana_dividido = Toplevel(self)
        ventana_dividido.title("Pago Dividido")
        ventana_dividido.geometry("400x350")
        ventana_dividido.config(bg="#f0f0f0")
        ventana_dividido.resizable(False, False)
        ventana_dividido.transient(self)
        ventana_dividido.grab_set()
        ventana_dividido.focus_force()

        tk.Label(ventana_dividido, text="Ingrese los montos:", font="sans 14 bold", bg="#f0f0f0").pack(pady=10)

        frame_campos = Frame(ventana_dividido, bg="#f0f0f0")
        frame_campos.pack(pady=10)

        tk.Label(frame_campos, text="💵 Efectivo:", font="sans 12 bold", bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=5)
        entry_efectivo = ttk.Entry(frame_campos, font="sans 12", justify="center")
        entry_efectivo.grid(row=0, column=1, pady=5)

        tk.Label(frame_campos, text="📱 QR:", font="sans 12 bold", bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=5)
        entry_qr = ttk.Entry(frame_campos, font="sans 12", justify="center")
        entry_qr.grid(row=1, column=1, pady=5)

        tk.Label(frame_campos, text="💳 Tarjeta:", font="sans 12 bold", bg="#f0f0f0").grid(row=2, column=0, sticky="w", pady=5)
        entry_tarjeta = ttk.Entry(frame_campos, font="sans 12", justify="center")
        entry_tarjeta.grid(row=2, column=1, pady=5)

    
        boton_finalizar = tk.Button(
            ventana_dividido,
            text="Finalizar Pago Dividido",
            command=lambda: self.procesar_pago_dividido(
                ventana_dividido,
                entry_efectivo,
                entry_qr,
                entry_tarjeta
            ),
            bg="green",
            fg="white"
        )
        boton_finalizar.pack(pady=10)

    def completar_si_vacio(self, entry_widget, label_widget):
        if not entry_widget.get().strip():
            texto_label = label_widget.cget("text").replace("Total a pagar: $", "").replace(",", "").strip()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, texto_label)    

#////////////////////////////////////////////////////////////////////////
    def pagar(self, ventana_pago, entry_cantidad_pagada, label_cambio, tipo_pago):
        try:
            if entry_cantidad_pagada:
                cantidad_pagada = float(entry_cantidad_pagada.get().replace(",", ""))

            else:
                cantidad_pagada = self.obtener_total() 

            total = self.obtener_total()
            cambio = cantidad_pagada - total
            if cambio < 0 and tipo_pago == "Efectivo":
                messagebox.showerror("Error", "La cantidad pagada es insuficiente")
                return
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            try:
                productos = []
                for child in self.tree.get_children():
                    item = self.tree.item(child, "values")
                    producto = item[0]
                    precio = float(item[1].replace(",", ""))
                    cantidad_vendida = int(item[2])
                    subtotal = float(item[3].replace(",", ""))
                    productos.append([producto, precio, cantidad_vendida, subtotal])

                    fecha_actual = datetime.now().isoformat(" ") 
                    
                    c.execute("""
                        INSERT INTO ventas (factura, nombre_articulo, valor_articulo, cantidad, subtotal, tipo_pago, fecha)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (self.numero_factura_actual, producto, precio, cantidad_vendida, subtotal, tipo_pago, fecha_actual))

                    c.execute("""
                        INSERT INTO ventas_historico (factura, nombre_articulo, valor_articulo, cantidad, subtotal, tipo_pago, fecha)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (self.numero_factura_actual, producto, precio, cantidad_vendida, subtotal, tipo_pago, fecha_actual))


                    
                    if self.es_ancheta(c, producto):
    # Es una ancheta: descontar componentes según ancheta_detalle
                        self.descontar_componentes_ancheta(c, producto, cantidad_vendida)
                    else:
    # Producto normal: descontar stock del propio producto
                        c.execute("UPDATE inventario SET stock = stock - ? WHERE nombre = ?", (cantidad_vendida, producto))   

                conn.commit()
                

                self.numero_factura_actual += 1
                self.mostrar_numero_factura()

                for child in self.tree.get_children():
                    self.tree.delete(child)
                self.label_suma_total.config(text="Total a pagar: $ 0")

                # 🔁 NUEVO BLOQUE: reiniciar campos manuales (precio, cantidad, producto, lector)
                self.entry_valor.config(state="normal")
                self.entry_valor.delete(0, tk.END)
                self.entry_valor.config(state="readonly")

                self.entry_cantidad.config(state="normal")
                self.entry_cantidad.delete(0, tk.END)

                self.entry_nombre.set("")

                self.entry_codigo_oculto.delete(0, tk.END)
                self.entry_codigo_oculto.focus_set()
            # 🔁 FIN BLOQUE NUEVO


                
                self.lector_habilitado = True
                self.entry_codigo_oculto.delete(0, tk.END)
                self.entry_codigo_oculto.focus_set()
                ventana_pago.destroy()

                fecha = datetime.now().strftime("%Y-%m-%d   %H:%M:%S ")
                self.generar_factura_pdf(productos, total, self.numero_factura_actual - 1, fecha, tipo_pago, vuelto=cambio if tipo_pago == "Efectivo" else None,cantidad_pagada=cantidad_pagada)
 
                # 🔥 Nueva impresión térmica profesional
                
                imprimir_ticket_pos(
                productos,
                total,
                tipo_pago,
                cambio if tipo_pago == "Efectivo" else None,
                cantidad_pagada,
                self.numero_factura_actual - 1,
                fecha
            )



            except sqlite3.Error as e:
                conn.rollback()
                messagebox.showerror("Error", f"Error al registrar la venta: {e}")
            finally:
                conn.close()

        except ValueError:
            messagebox.showerror("Error", "Cantidad pagada no válida")

    def procesar_pago_dividido(self, ventana_pago, entry_efectivo, entry_qr, entry_tarjeta):
        try:
            efectivo = float(entry_efectivo.get().replace(",", "") or 0)
            qr = float(entry_qr.get().replace(",", "") or 0)
            tarjeta = float(entry_tarjeta.get().replace(",", "") or 0)
            total_pago = efectivo + qr + tarjeta
            total = self.obtener_total()

            if total_pago < total:
                messagebox.showerror("Error", "La suma de los pagos es menor al total de la venta.")
                return

            tipo_pago = f"Dividido (E: {efectivo:,.0f} / QR: {qr:,.0f} / T: {tarjeta:,.0f})"
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()

            fecha_actual = datetime.now().isoformat(" ")
            productos = []

            montos = {
                "Efectivo": efectivo,
                "QR": qr,
                "Tarjeta": tarjeta
            }

            for child in self.tree.get_children():
                item = self.tree.item(child, "values")
                producto = item[0]
                precio = float(item[1].replace(",", ""))
                cantidad = int(item[2])
                subtotal = float(item[3].replace(",", ""))
                productos.append([producto, precio, cantidad, subtotal])

                for metodo, monto in montos.items():
                    if monto == 0:
                        continue
                    proporcion = monto / total_pago
                    subtotal_parcial = round(subtotal * proporcion)
                    cantidad_parcial = round(cantidad * proporcion, 2)  # Puedes redondear a 2 decimales si es decimal

                    c.execute("""
                        INSERT INTO ventas (factura, nombre_articulo, valor_articulo, cantidad, subtotal, tipo_pago, fecha)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (self.numero_factura_actual, producto, precio, cantidad_parcial, subtotal_parcial, metodo, fecha_actual))


                    c.execute("""
                        INSERT INTO ventas_historico (factura, nombre_articulo, valor_articulo, cantidad, subtotal, tipo_pago, fecha)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (self.numero_factura_actual, producto, precio, cantidad, subtotal_parcial, metodo, fecha_actual))

                if self.es_ancheta(c, producto):
    # Es una ancheta: descontar componentes según ancheta_detalle
                    self.descontar_componentes_ancheta(c, producto, cantidad)
                else:
    # Producto normal: descontar stock del propio producto
                    c.execute("UPDATE inventario SET stock = stock - ? WHERE nombre = ?", (cantidad, producto))

            conn.commit()
            imprimir_ticket_pos(
               productos,
                total,
                tipo_pago,
                None,  # No hay vuelto en pagos divididos
                total_pago,
                self.numero_factura_actual,
                fecha_actual
            )
            self.numero_factura_actual += 1
            self.tree.delete(*self.tree.get_children())
            self.actualizar_total()
            ventana_pago.destroy()
            messagebox.showinfo("Éxito", "Pago dividido registrado correctamente.")

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"No se pudo registrar el pago dividido:\n{e}")
        


#GENERAR COMO VA  A SER LA FACTURA //////////////////////////////////

    def generar_factura_pdf(self, productos, total, factura_numero, fecha, tipo_pago, vuelto=None, cantidad_pagada=None):
        
        width = 3.15 * inch  # 80 mm de ancho de papel
        base_height = 3.5 * inch  # Altura base más pequeña para que no quede tan abajo
        height = base_height + (len(productos) * 0.35 * inch)  # Aumenta el alto según los productos

        base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
        ruta_facturas = os.path.join(base_path, "facturas")
        os.makedirs(ruta_facturas, exist_ok=True)

        

        archivo_pdf = os.path.join(ruta_facturas, f"factura_{factura_numero}.pdf")

        c = canvas.Canvas(archivo_pdf, pagesize=(width, height))

    

        y = height - 70  # Iniciar un poco más arriba

    # --- INFORMACION DEL LOCAL ---
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(width / 2, y, "MORLI GIFTSTORE")
        y -= 10

        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(width / 2, y, "NIT: 1085258600-8")
        y -= 10

        c.drawCentredString(width / 2, y, "Cra 98 # 16-50 Local J1045")
        y -= 10

        c.drawCentredString(width / 2, y, "Tel: (+57) 3223265508")
        y -= 10

        c.drawCentredString(width / 2, y, "Cali - Colombia")
        y -= 10

        c.drawCentredString(width / 2, y, "Régimen Simple de Tributación")
        y -= 20

    # --- INFORMACION DE LA VENTA ---
        c.setFont("Helvetica-Bold", 8)
        c.drawString(10, y, f"REG: {fecha}")
        y -= 12

        c.drawString(10, y, f"Factura: {factura_numero:05d}")
        y -= 18

    # --- DETALLE DE PRODUCTOS ---
        c.setFont("Helvetica-Bold", 8)
        c.drawString(10, y, "Detalle de Productos:")
        y -= 12

        data = [["Producto", "Precio", "Cant", "Subtotal"]] + productos
        colWidths = [width * 0.45, width * 0.18, width * 0.18, width * 0.19]
        rowHeights = [12] * len(data)

        table = Table(data, colWidths=colWidths, rowHeights=rowHeights)

        table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Todo alineado a la izquierda
        # No GRID
    ]))

        table_height = len(data) * 12
        y_table = y - table_height

        table.wrapOn(c, width, height)
        table.drawOn(c, 2, y_table)  # Margen pequeño de 2px

        y = y_table - 20

    # --- TOTALES ---
        c.setFont("Helvetica-Bold", 9)
        c.drawString(10, y, f"TOTAL: ${total:,.0f}")
        y -= 12

        if cantidad_pagada is not None:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(10, y, f"CAJA: ${cantidad_pagada:,.0f}")
            y -= 12

        if tipo_pago == "Efectivo" and vuelto is not None:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(10, y, f"CAMBIO: ${vuelto:,.0f}")
            y -= 12

        c.setFont("Helvetica-Bold", 8)
        c.drawString(10, y, f"METODO PAGO: {tipo_pago}")
        y -= 20

    # --- MENSAJE FINAL ---
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(width / 2, y, "¡GRACIAS POR SU COMPRA!")

    # --- ESPACIO EXTRA PARA DESPEGAR FACILMENTE ---
        y -= 20
        c.drawString(10, y, " ")  # Línea en blanco
        y -= 10
        c.drawString(10, y, " ")  # O

        c.save()

        from tkinter import messagebox
        

        

# FUNCION FACTURA ACTUAL
    def obtener_numero_factura_actual(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT MAX(factura) FROM ventas")
            max_factura = c.fetchone()[0]
            return max_factura + 1 if max_factura else 1
          
       
# NUEVA FUNCION MOSTRAR NUMERO FACTURA
    def mostrar_numero_factura(self):
        self.numero_factura.set(self.numero_factura_actual)

    @classmethod
    def resetear_numero_factura(cls):
        cls.numero_factura_actual = 1    

    #CLAVE VER FACTURAS
    def validar_password_facturas(self):
        password = tk.simpledialog.askstring(
            "Autenticación",
            "Ingrese la contraseña para ver facturas:",
            show="*"
        )

        if password == "1716":  # 🔒 Cambia aquí la contraseña que tú quieras
            self.abrir_ventana_factura()
        elif password is not None:
            messagebox.showerror("Acceso denegado", "Contraseña incorrecta.")

#  NUEVA VENTANA 

    def abrir_ventana_resumen_dia(self):
        import datetime
        self.lector_habilitado = False

        ventana_dia = Toplevel(self)
        ventana_dia.title("Ventas del Día")
        ventana_dia.geometry("1100x700")
        ventana_dia.config(bg="#c6d9e3")
        ventana_dia.resizable(False, False)

        ventana_dia.transient(self)
        ventana_dia.grab_set()
        ventana_dia.protocol("WM_DELETE_WINDOW", lambda: (setattr(self, "lector_habilitado", True), ventana_dia.destroy()))

        titulo = tk.Label(ventana_dia, text="VENTAS DEL DÍA", font="sans 36 bold", bg="#c6d9e3")
        titulo.place(x=300, y=5)

        fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
        label_fecha = tk.Label(ventana_dia, text=f"📅 Ventas del {fecha_actual}", font="sans 14 bold", bg="#c6d9e3")
        label_fecha.place(x=60, y=70)

        tk.Label(ventana_dia, text="Tipo de Producto:", font="sans 12 bold", bg="#c6d9e3").place(x=400, y=70)
        combo_tipo = ttk.Combobox(ventana_dia, font="sans 12", state="readonly")
        combo_tipo.place(x=540, y=70, width=180)

        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT DISTINCT tipo_producto FROM inventario")
            tipos = c.fetchall()
            conn.close()
            combo_tipo["values"] = [""] + [t[0] for t in tipos]
        except:
            combo_tipo["values"] = [""]

        frame_tree = tk.Frame(ventana_dia, bg="#c6d9e3")
        frame_tree.place(x=35, y=130, width=1030, height=395)

        scrol_y = ttk.Scrollbar(frame_tree, orient=VERTICAL)
        scrol_y.pack(side=RIGHT, fill=Y)

        scrol_x = ttk.Scrollbar(frame_tree, orient=HORIZONTAL)
        scrol_x.pack(side=BOTTOM, fill=X)

        tree = ttk.Treeview(frame_tree, columns=("ID", "Factura", "Producto", "Tipo", "Fecha", "Precio", "Cantidad", "Subtotal", "Tipo Pago"),
                        show="headings", height=10, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set)
        scrol_y.config(command=tree.yview)
        scrol_x.config(command=tree.xview)

        tree.heading("ID", text="ID")
        tree.heading("Factura", text="Factura")
        tree.heading("Producto", text="Producto")
        tree.heading("Tipo", text="Tipo")
        tree.heading("Fecha", text="Fecha")
        tree.heading("Precio", text="Precio")
        tree.heading("Cantidad", text="Cantidad")
        tree.heading("Subtotal", text="Subtotal")
        tree.heading("Tipo Pago", text="Tipo Pago")

        for col in ("ID", "Factura", "Producto", "Tipo", "Fecha", "Precio", "Cantidad", "Subtotal", "Tipo Pago"):
            tree.column(col, anchor="center")

        tree.pack(expand=True, fill=BOTH)

        label_cantidad_total = tk.Label(ventana_dia, text="Cantidad total vendida: 0", font="sans 12 bold", bg="#c6d9e3")
        label_cantidad_total.place(x=70, y=570)

        label_total_vendido = tk.Label(ventana_dia, text="Total vendido: $0", font="sans 12 bold", bg="#c6d9e3")
        label_total_vendido.place(x=870, y=570)

        label_total_efectivo = tk.Label(ventana_dia, text="Efectivo: $0", font="sans 12 bold", bg="#c6d9e3")
        label_total_efectivo.place(x=350, y=570)

        label_total_qr = tk.Label(ventana_dia, text="QR: $0", font="sans 12 bold", bg="#c6d9e3")
        label_total_qr.place(x=540, y=570)

        label_total_tarjeta = tk.Label(ventana_dia, text="Tarjeta: $0", font="sans 12 bold", bg="#c6d9e3")
        label_total_tarjeta.place(x=700, y=570)

        boton_ver_facturas = tk.Button(ventana_dia, text="Ver Facturas", font="sans 12 bold", bg="#dddddd",
                                    command=lambda: self.validar_password_facturas())
        boton_ver_facturas.place(x=880, y=610, width=180, height=30)

        boton_movimientos = tk.Button(
            ventana_dia, text="Movimientos", font="sans 12 bold", bg="#dddddd",
            command=self.validar_password_movimientos
        )
        boton_movimientos.place(x=680, y=610, width=180, height=30)

        def cargar_ventas_dia(tipo_filtro=""):
            try:
                conn = sqlite3.connect(self.db_name)
                c = conn.cursor()

                hoy = datetime.datetime.now().strftime("%Y-%m-%d")
                query = """
                    SELECT vh.id, vh.factura, vh.nombre_articulo, i.tipo_producto,
                            vh.fecha, vh.valor_articulo, vh.cantidad, vh.subtotal, vh.tipo_pago
                    FROM ventas_historico vh
                    LEFT JOIN inventario i ON vh.nombre_articulo = i.nombre
                    WHERE DATE(vh.fecha) = ?
                """
                params = [hoy]

                if tipo_filtro:
                    query += " AND i.tipo_producto LIKE ?"
                    params.append(f"%{tipo_filtro}%")

                c.execute(query, params)
                ventas = c.fetchall()
                conn.close()

                tree.delete(*tree.get_children())
                vistos = set()
                cantidad_real = 0
                for v in ventas:
                    clave = (v[1], v[2])  # (factura, nombre_articulo)
                    if clave not in vistos:
                        cantidad_real += int(v[6])
                        vistos.add(clave)

                total_cantidad = cantidad_real
                total_vendido = sum(float(v[7]) for v in ventas)
                total_efectivo = sum(float(v[7]) for v in ventas if v[8] == "Efectivo")
                total_qr = sum(float(v[7]) for v in ventas if v[8] == "QR")
                total_tarjeta = sum(float(v[7]) for v in ventas if v[8] == "Tarjeta")

                for venta in ventas:
                    tree.insert("", "end", values=venta)

                label_cantidad_total.config(text=f"Cantidad total vendida: {total_cantidad}")
                label_total_vendido.config(text=f"Total vendido: ${total_vendido:,.0f}")
                label_total_efectivo.config(text=f"Efectivo: ${total_efectivo:,.0f}")
                label_total_qr.config(text=f"QR: ${total_qr:,.0f}")
                label_total_tarjeta.config(text=f"Tarjeta: ${total_tarjeta:,.0f}")

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo cargar las ventas del día:\n{e}")

        combo_tipo.bind("<<ComboboxSelected>>", lambda e: cargar_ventas_dia(combo_tipo.get()))
        cargar_ventas_dia()
    

    def validar_password_movimientos(self):
        password = tk.simpledialog.askstring(
            "Autenticación",
            "Ingrese la contraseña para ver Movimientos:",
            show="*"
        )

        if password == "Imagine":
            self.abrir_ventana_movimientos()
        elif password is not None:
            messagebox.showerror("Acceso denegado", "Contraseña incorrecta.")
        

# SE CONSTRUYE VENTANA PARA VER
    def abrir_ventana_factura(self):
        self.lector_habilitado = False

        ventana_facturas = Toplevel(self)
        ventana_facturas.title("Factura")
        ventana_facturas.geometry("1100x650")
        ventana_facturas.config(bg="#c6d9e3")
        ventana_facturas.resizable(False, False)
        
        ventana_facturas.transient(self)  # Mantener sobre la ventana principal
        ventana_facturas.grab_set()       # Bloquear interacción con otras ventanas
        ventana_facturas.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana_facturas(ventana_facturas))

        facturas = Label(ventana_facturas, bg="#c6d9e3", text="Facturas registradas", font="sans 36 bold")
        facturas.place(x=300, y=5)
#Filtro ///////////////////////////////////////////////
        Label(ventana_facturas, text="Proveedor:", font="sans 12 bold", bg="#c6d9e3").place(x=20, y=70)
        self.combo_proveedor = ttk.Combobox(ventana_facturas, font="sans 12", state="readonly")
        self.combo_proveedor.place(x=120, y=70, width=180)

        Label(ventana_facturas, text="Tipo de Producto:", font="sans 12 bold", bg="#c6d9e3").place(x=320, y=70)
        self.combo_tipo_producto = ttk.Combobox(ventana_facturas, font="sans 12", state="readonly")
        self.combo_tipo_producto.place(x=470, y=70, width=180)
                #FECHA DESDE
        Label(ventana_facturas, text="Desde:", font="sans 12 bold", bg="#c6d9e3").place(x=20, y=110)
        self.fecha_desde = DateEntry(ventana_facturas, font="sans 12", width=12, background="darkblue", foreground="white", borderwidth=2)
        self.fecha_desde.place(x=80, y=110)

        Label(ventana_facturas, text="Hasta:", font="sans 12 bold", bg="#c6d9e3").place(x=220, y=110)
        self.fecha_hasta = DateEntry(ventana_facturas, font="sans 12", width=12, background="darkblue", foreground="white", borderwidth=2)
        self.fecha_hasta.place(x=280, y=110)

        btn_filtrar = Button(ventana_facturas, text="Filtrar", font="sans 12 bold", bg="#dddddd",
                            command=lambda: self.cargar_facturas(tree_facturas, self.combo_proveedor.get(), self.combo_tipo_producto.get(), self.fecha_desde.get(), self.fecha_hasta.get()))
        btn_filtrar.place(x=735, y=75, width=100, height=30)

        btn_todas = Button(ventana_facturas, text="Mostrar Todo", font="sans 12 bold", bg="#dddddd", 
                           command=lambda: self.cargar_facturas(tree_facturas, "", "", "", ""))
        btn_todas.place(x=870, y=75, width=120, height=30)

        treFrame = tk.Frame(ventana_facturas, bg="#c6d9e3")
        treFrame.place(x=35, y=150, width=1050, height=395)

        scrol_y = ttk.Scrollbar(treFrame, orient=VERTICAL)
        scrol_y.pack(side=RIGHT, fill=Y)

        scrol_x = ttk.Scrollbar(treFrame, orient=HORIZONTAL)
        scrol_x.pack(side=BOTTOM, fill=X)

        tree_facturas = ttk.Treeview(treFrame, columns=("ID", "Factura", "Producto", "Proveedor", "Tipo", "Fecha", "Precio", "Cantidad", "Subtotal","Tipo Pago"),
                                     show="headings", height=10, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set)
        scrol_y.config(command=tree_facturas.yview)
        scrol_x.config(command=tree_facturas.xview)

        tree_facturas.heading("#1", text="ID")
        tree_facturas.heading("#2", text="Factura")
        tree_facturas.heading("#3", text="Producto")
        tree_facturas.heading("#4", text="Proveedor")
        tree_facturas.heading("#5", text="Tipo")
        tree_facturas.heading("#6", text="Fecha")
        tree_facturas.heading("#7", text="Precio")
        tree_facturas.heading("#8", text="Cantidad")
        tree_facturas.heading("#9", text="Subtotal")
        tree_facturas.heading("#10", text="Tipo Pago")  

        tree_facturas.column("ID", width=70, anchor="center")
        tree_facturas.column("Factura", width=100, anchor="center")        
        tree_facturas.column("Producto", width=200, anchor="center")
        tree_facturas.column("Proveedor", width=200, anchor="center")
        tree_facturas.column("Tipo", width=120, anchor="center")
        tree_facturas.column("Fecha", width=100, anchor="center")
        tree_facturas.column("Precio", width=130, anchor="center")
        tree_facturas.column("Cantidad", width=130, anchor="center")
        tree_facturas.column("Subtotal", width=130, anchor="center")
        tree_facturas.column("Tipo Pago", width=100, anchor="center")


        tree_facturas.pack(expand=True, fill=BOTH)

        self.label_cantidad_total = Label(ventana_facturas, text="Cantidad total vendida: 0", font="sans 12 bold", bg="#c6d9e3")
        self.label_cantidad_total.place(x=70, y=570)

        self.label_total_vendido = Label(ventana_facturas, text="Total vendido: $0", font="sans 12 bold", bg="#c6d9e3")
        self.label_total_vendido.place(x=870, y=570)

        self.label_ventas_netas = Label(ventana_facturas, text="Ventas netas: $0", font="sans 12 bold", bg="#c6d9e3")
        self.label_ventas_netas.place(x=870, y=600)


        self.label_total_efectivo = Label(ventana_facturas, text="Efectivo: $0", font="sans 12 bold", bg="#c6d9e3")
        self.label_total_efectivo.place(x=350, y=570)

        self.label_total_qr = Label(ventana_facturas, text="QR: $0", font="sans 12 bold", bg="#c6d9e3")
        self.label_total_qr.place(x=540, y=570)

        self.label_total_tarjeta = Label(ventana_facturas, text="Tarjeta: $0", font="sans 12 bold", bg="#c6d9e3")
        self.label_total_tarjeta.place(x=700, y=570)

        self.cargar_proveedores()
        self.cargar_tipos_productos()
        self.cargar_facturas(tree_facturas, "" , "" , "" ,"")

    def cerrar_ventana_facturas(self, ventana):
        self.lector_habilitado = True
        ventana.destroy()    

    def cargar_tipos_productos(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT DISTINCT tipo_producto FROM inventario")
            tipos = c.fetchall()
            conn.close()

            self.combo_tipo_producto["values"] = [""] + [tipo[0] for tipo in tipos]  
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar los tipos de producto: {e}")    

    def cargar_proveedores(self):
        try:
            conn = sqlite3.connect(self.db_name)   
            c = conn.cursor() 
            c.execute("SELECT DISTINCT Proveedor FROM inventario")
            proveedores = c.fetchall()
            conn.close()

            self.combo_proveedor["values"] = [""] + [prov[0] for prov in proveedores] 
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar proveedores: {e}")    

    def cargar_facturas(self, tree, proveedor, tipo_producto, fecha_desde, fecha_hasta):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            query = """
              SELECT vh.id, vh.factura, vh.nombre_articulo, i.proveedor, i.tipo_producto, 
                 vh.fecha, vh.valor_articulo, vh.cantidad, vh.subtotal, vh.tipo_pago
          FROM ventas_historico vh
          LEFT JOIN inventario i ON vh.nombre_articulo = i.nombre
        """   
                
                
            params = []
            condiciones = []    

            if proveedor:
                condiciones.append("i.proveedor LIKE ?")
                params.append(f"%{proveedor}%")

            if tipo_producto:
                condiciones.append("i.tipo_producto LIKE ?")
                params.append(f"%{tipo_producto}%") 
 

            if fecha_desde and fecha_hasta:
                try:
                     
                    fecha_desde = datetime.strptime(fecha_desde, "%m/%d/%y").strftime("%Y-%m-%d 00:00:00")
                    fecha_hasta = datetime.strptime(fecha_hasta, "%m/%d/%y").strftime("%Y-%m-%d 23:59:59")
                    
                    

                    condiciones.append("vh.fecha BETWEEN ? AND ?")
                    params.extend([fecha_desde, fecha_hasta])
                except ValueError:
                    messagebox.showerror("Error", "Formato de fecha incorrecto")
                    return    

            if condiciones:
                query += " WHERE " + " AND ".join(condiciones)                     

            c.execute(query, params)
            facturas_crudas = c.fetchall()
            conn.close()

            if not facturas_crudas:
                messagebox.showwarning("Aviso", "No se encontraron resultados con los filtros aplicados.")
                return

            facturas = facturas_crudas
            
            
            for item in tree.get_children():
                tree.delete(item)

            # Evitar duplicados: agrupar por (factura, producto)
            vistos = set()
            cantidad_real = 0
            for f in facturas_crudas:
                clave = (f[1], f[2])  # (factura, nombre_articulo)
                if clave not in vistos:
                    cantidad_real += int(f[7])
                    vistos.add(clave)

            total_cantidad = cantidad_real

            total_vendido = sum(float(f[8]) for f in facturas_crudas)
            total_efectivo = sum(float(f[8]) for f in facturas_crudas if f[9] and f[9] == "Efectivo")
            total_qr       = sum(float(f[8]) for f in facturas_crudas if f[9] and f[9] == "QR")
            total_tarjeta  = sum(float(f[8]) for f in facturas_crudas if f[9] and f[9] == "Tarjeta")

            for factura in facturas:
                tree.insert("", "end", values=factura)
                    
            self.label_cantidad_total.config(text=f"Cantidad total vendida: {total_cantidad}")
            self.label_total_vendido.config(text=f"Total vendido: ${total_vendido:,.0f}") 
            ventas_netas = total_vendido - (total_vendido * 0.30)
            self.label_ventas_netas.config(text=f"Ventas netas: ${ventas_netas:,.0f}")
            self.label_total_efectivo.config(text=f"Efectivo: ${total_efectivo:,.0f}")
            self.label_total_qr.config(text=f"QR: ${total_qr:,.0f}")
            self.label_total_tarjeta.config(text=f"Tarjeta: ${total_tarjeta:,.0f}")

            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar las facturas: {e}") 

    def validar_stock_por_codigo(self, codigo):
        """
        Verifica si un producto escaneado tiene stock suficiente antes de agregarse.
        Retorna False si es producto normal con stock <= 0.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT stock, es_servicio FROM inventario WHERE codigo_barras = ?", (codigo,))
            resultado = c.fetchone()
            conn.close()

            if resultado:
                stock, es_servicio = resultado
                if es_servicio == 0 and stock <= 0:
                    return False
            return True
        except:
            return True  # Permitir por defecto si hay error para no bloquear
        
    def abrir_ventana_movimientos(self):
        try:
            MovimientosInventario(self, self.db_name)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Movimientos de Inventario:\n{e}")    
            

