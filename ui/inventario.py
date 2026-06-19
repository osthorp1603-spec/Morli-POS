import sqlite3 
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

class Inventario(tk.Frame):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    db_name = os.path.join(base_path, "database.db")

    def __init__(self, padre):
        super().__init__(padre)
        self.pack()
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.widgets()

    def rutas(self, ruta):
        try:
            rutabase = sys._MEIPASS
        except Exception:
            rutabase=os.path.abspath(".")
        return os.path.join(rutabase,ruta)     
#FUNCION CLASIFICA LOS WIDGETS  ES INTERFAZ GRAFICA
    def widgets(self):

        frame1 = tk.Frame(self, bg="#dddddd",highlightbackground="gray",highlightthickness=1)  
        frame1.pack()
        frame1.place(x=0,y=0,width=1300, height=190)

        titulo = tk.Label(self, text="INVENTARIOS",bg="#dddddd",font="sans 30 bold", anchor="center") #LABEL PARTE TITULO
        titulo.pack()
        titulo.place(x=5,y=0,width=1300, height=90)

        frame2 = tk.Frame(self,bg="#c6d9e3",highlightbackground="gray", highlightthickness=1)
        frame2.place(x=0,y=100,width=1300,height=630)      #DONDE CAMBIA TAMANO TABLA
       #///////////////////UMBRAL-STOCK
        label_editar_umbral = tk.Label(self, text="Editar Min:", font="sans 14 bold", bg="#c6d9e3")
        label_editar_umbral.place(x=750, y=650)

        self.entry_editar_umbral = ttk.Entry(self, font="sans 12")
        self.entry_editar_umbral.place(x=870, y=648, width=70)

        boton_actualizar_umbral = tk.Button(self, text="Actualizar Min", font="sans 12 bold",
                                        command=self.actualizar_umbral)
        boton_actualizar_umbral.place(x=950, y=650, width=180, height=30)


       #/////////////////////////////////////////////////////

        # ======= CAMPO DE BÚSQUEDA =======
        lbl_buscar = Label(frame2, text="Buscar Producto:", font="sans 12 bold", bg="#c6d9e3")
        lbl_buscar.place(x=420, y=10)

        self.entry_buscar = ttk.Entry(frame2, font="sans 14 bold")
        self.entry_buscar.place(x=570, y=10, width=180, height=30)
        self.entry_buscar.bind("<KeyRelease>", self.buscar_producto)

        btn_limpiar = Button(frame2, text="Limpiar", font="sans 12 bold", command=self.mostrar)
        btn_limpiar.place(x=760, y=10, width=100, height=30)

        # ======= CAMPO DE BÚSQUEDA POR PROVEEDOR =======
        lbl_proveedor = Label(frame2, text="Proveedor:", font="sans 10 bold", bg="#c6d9e3")
        lbl_proveedor.place(x=243, y=10)

        self.entry_filtro_proveedor = ttk.Entry(frame2, font="sans 10")
        self.entry_filtro_proveedor.place(x=320, y=10, width=80, height=30)
        self.entry_filtro_proveedor.bind("<KeyRelease>", self.buscar_por_proveedor)

        # Botón para eliminar producto
        boton_eliminar = tk.Button(self, text="Eliminar", font="sans 14 bold", bg="#dddddd", command=self.eliminar_producto)
        boton_eliminar.place(x=150, y=680, width=130, height=40) 

        # NUEVA BARRA PARA ASIGNAR CÓDIGO (Encima del Treeview, aprovechando espacio libre)
        label_editar_codigo = tk.Label(frame2, text="Asignar Código:", font="sans 11 bold", bg="#c6d9e3")
        label_editar_codigo.place(x=880, y=10)

        self.entry_editar_codigo = ttk.Entry(frame2, font="sans 12")
        self.entry_editar_codigo.place(x=1000, y=10, width=120)

        boton_actualizar_codigo = tk.Button(frame2, text="Guardar Código", font="sans 12 bold",
                                    command=self.actualizar_codigo_barras)
        boton_actualizar_codigo.place(x=1130, y=10, width=126, height=30)       


#CREACION DE LOS WIDGETS DE LALDO LATERAL
        labelframe = LabelFrame(frame2, text="Productos",font="sans 22 bold",bg="#c6d9e3")
        labelframe.place(x=20,y=30,width=380,height=594)
#CREACION ETIQUETA ////////////
        lblnombre = Label(labelframe, text="Nombre: ",font="sans 14 bold",bg="#c6d9e3")
        lblnombre.place(x=10,y=20)
        self.nombre = ttk.Entry(labelframe, font="sans 14 bold")
        self.nombre.place(x=140,y=20,width=230,height=40)
#//////////////////////////////////////////////////////////
        lblproveedor = Label(labelframe, text="Proveedor: ",font="sans 14 bold",bg="#c6d9e3")
        lblproveedor.place(x=10,y=80)
        self.proveedor = ttk.Entry(labelframe, font="sans 14 bold")
        self.proveedor.place(x=140,y=80,width=230,height=40)

        lblprecio = Label(labelframe, text="Precio: ",font="sans 14 bold",bg="#c6d9e3")
        lblprecio.place(x=10,y=140)
        self.precio = ttk.Entry(labelframe, font="sans 14 bold")
        self.precio.place(x=140,y=140,width=230,height=40)

        lblcosto = Label(labelframe, text="Costo: ",font="sans 14 bold",bg="#c6d9e3")
        lblcosto.place(x=10,y=200)
        self.costo = ttk.Entry(labelframe, font="sans 14 bold")
        self.costo.place(x=140,y=200,width=230,height=40)

        lblstock = Label(labelframe, text="Stock: ",font="sans 14 bold",bg="#c6d9e3")
        lblstock.place(x=10,y=260)
        self.stock = ttk.Entry(labelframe, font="sans 14 bold")
        self.stock.place(x=140,y=260,width=230,height=40)

        lbltipo_producto = Label(labelframe, text="Tipo Prod: ",font="sans 14 bold",bg="#c6d9e3")
        lbltipo_producto.place(x=10,y=320)
        self.tipo_producto = ttk.Entry(labelframe, font="sans 14 bold")
        self.tipo_producto.place(x=140,y=320,width=230,height=40)

        lblservicio = Label(labelframe, text="Servicio?: ",font="sans 14 bold",bg="#c6d9e3")
        lblservicio.place(x=10,y=380)
        self.servicio = ttk.Entry(labelframe, font="sans 14 bold")
        self.servicio.place(x=140,y=380,width=230,height=40)


#AGREGAR BOTON////////////////////
        boton_agregar = tk.Button(labelframe, text="Ingresar",font="sans 14 bold",bg="#dddddd",command=self.registrar)
        boton_agregar.place(x=20,y=450,width=130,height=40)

        boton_editar = tk.Button(labelframe,text="Editar",font="sans 14 bold",bg="#dddddd",command=self.editar_producto)
        boton_editar.place(x=230,y=450,width=130,height=40)

    #CREAR TABLA    
        treFrame = Frame(frame2, bg="white")
        treFrame.place(x=410,y=50, width=850,height=470)

     #SCROLL BAR ///////
        scrol_y = ttk.Scrollbar(treFrame, orient=VERTICAL)
        scrol_y.pack(side=RIGHT, fill=Y)

        scrol_x = ttk.Scrollbar(treFrame, orient=HORIZONTAL)
        scrol_x.pack(side=BOTTOM, fill=X)

        self.tre = ttk.Treeview(treFrame, columns=("ID", "PRODUCTO","PROVEEDOR","PRECIO","COSTO","STOCK", "TIPO PRODUCTO","SERVICIO","UMBRAL STOCK", "CODIGO BARRAS"),
                                show="headings",height=40,yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set)
        self.tre.pack(expand=True,fill=BOTH)
        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)   

        self.tre.heading("ID",text="Id")
        self.tre.heading("PRODUCTO",text="Producto")
        self.tre.heading("PROVEEDOR",text="Proveedor")
        self.tre.heading("PRECIO",text="Precio")
        self.tre.heading("COSTO",text="Costo")
        self.tre.heading("STOCK",text="Stock")
        self.tre.heading("TIPO PRODUCTO",text="Tipo Producto")
        self.tre.heading("SERVICIO",text="Servicio")
        self.tre.heading("UMBRAL STOCK", text="Umbral Stock")
        self.tre.heading("CODIGO BARRAS", text="Código Barras")

        self.tre.column("ID", width=70, anchor="center")
        self.tre.column("PRODUCTO", width=100, anchor="center")
        self.tre.column("PROVEEDOR", width=100, anchor="center")
        self.tre.column("PRECIO", width=100, anchor="center")
        self.tre.column("COSTO", width=100, anchor="center")
        self.tre.column("STOCK", width=70, anchor="center")
        self.tre.column("TIPO PRODUCTO", width=70, anchor="center")
        self.tre.column("SERVICIO", width=70, anchor="center")
        self.tre.column("UMBRAL STOCK", width=100, anchor="center")
        self.tre.column("CODIGO BARRAS", width=150, anchor="center")

        self.mostrar()

        btn_actualizar = Button(frame2, text="Actualizar Inventario",font="sans 14 bold", command=self.actualizar_inventario)
        btn_actualizar.place(x=410,y=535,width=260,height=50)

    def eje_consulta(self, consulta, parametros=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(consulta, parametros)
            conn.commit()
        return result    

    def validacion(self, nombre, prov, precio, costo, stock, tipo_producto, servicio):
        if servicio == "1":
            return True  # No exige ningún campo si es servicio

        if not (nombre and prov and precio and costo and stock and tipo_producto and servicio):
            return False
        try:
            float(precio)
            float(costo)
            float(stock)
        except ValueError:
            return False
        return True
# DONDE CUADRO LA COMA DE MILES     
    def mostrar(self):                                                
        consulta = "SELECT * FROM inventario ORDER BY tipo_producto ASC, proveedor ASC, nombre ASC"
        result = self.eje_consulta(consulta)
        for elem in result:
            try:
                precio_cop = "{:,.0f}".format(float(elem[3])) if elem[3] else ""
                costo_cop  = "{:,.0f}".format(float(elem[4])) if elem[4] else ""  
            except ValueError:
                precio_cop = elem[3]
                costo_cop = elem[4]
            self.tre.insert("", "0", text=elem[0], values=(elem[0], elem[1], elem[2], precio_cop, costo_cop, elem[5], elem[6], elem[7], elem[8], elem[9]))    

    def actualizar_inventario(self):
        for item in self.tre.get_children():
            self.tre.delete(item)
        self.mostrar()
        messagebox.showinfo("Actualizacion", "El inventario ha sido actualizado correctamente.") 


    def actualizar_umbral(self):
        seleccionado = self.tre.selection()

        if not seleccionado:
           messagebox.showerror("Error", "Seleccione un producto para actualizar su umbral de stock.")
           return

        nuevo_umbral = self.entry_editar_umbral.get()

        if not nuevo_umbral.isdigit():
           messagebox.showerror("Error", "Ingrese un número válido para el umbral de stock.")
           return

        nuevo_umbral = int(nuevo_umbral)
        producto_id = self.tre.item(seleccionado, "values")[0]  # Obtiene el ID del producto seleccionado

        try:
            consulta = "UPDATE inventario SET umbral_stock = ? WHERE id = ?"
            self.eje_consulta(consulta, (nuevo_umbral, producto_id))

            messagebox.showinfo("Éxito", "Umbral de stock actualizado correctamente.")
            self.actualizar_inventario()  # Recarga la tabla para reflejar los cambios

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al actualizar umbral: {e}")       

    def buscar_producto(self, event):
        """Filtra la tabla en tiempo real por el nombre del producto."""
        texto = self.entry_buscar.get().strip().lower()
        for item in self.tre.get_children():
            self.tre.delete(item)

        if not texto:
            self.mostrar()
            return
        
        if event.keysym == "Return":
        # --- Buscar primero por código de barras ---
            consulta_codigo = "SELECT * FROM inventario WHERE codigo_barras = ?"
            result = self.eje_consulta(consulta_codigo, (texto,))
            productos = result.fetchall()

            if productos:
                for elem in productos:
                    try:
                        precio_cop = "{:,.0f}".format(float(elem[3])) if elem[3] else ""
                        costo_cop = "{:,.0f}".format(float(elem[4])) if elem[4] else ""
                    except ValueError:
                        precio_cop = elem[3]
                        costo_cop = elem[4]

                self.tre.insert("", 0, text=elem[0], values=(
                        elem[0], elem[1], elem[2], precio_cop, costo_cop,
                        elem[5], elem[6], elem[7], elem[8], elem[9] if len(elem) > 9 else ""
                    ))

            else:
                messagebox.showinfo("Búsqueda", "No se encontró el producto.")
        else:  
            # Si es cualquier otra tecla, buscar dinámicamente por nombre
            texto = texto.lower()      
            consulta_nombre = "SELECT * FROM inventario WHERE LOWER(nombre) LIKE ? ORDER BY id DESC"
            result = self.eje_consulta(consulta_nombre, ('%' + texto + '%',))
            productos = result.fetchall()        

        
        
            for elem in productos:
                try:
                    precio_cop = "{:,.0f}".format(float(elem[3])) if elem[3] else ""
                    costo_cop  = "{:,.0f}".format(float(elem[4])) if elem[4] else ""  
                except ValueError:
                    precio_cop = elem[3]
                    costo_cop = elem[4]
                self.tre.insert("", 0, text=elem[0], values=(elem[0], elem[1], elem[2], precio_cop, costo_cop, elem[5], elem[6], elem[7],elem[8], elem[9] if len(elem) > 9 else ""
                                                        )) 
           
     

    def registrar(self):
        result = self.tre.get_children()
        for i in result:
            self.tre.delete(i)
        nombre = self.nombre.get()
        prov = self.proveedor.get()
        precio = self.precio.get()
        costo = self.costo.get()
        stock = self.stock.get()
        tipo_producto = self.tipo_producto.get()
        servicio = self.servicio.get()
        if self.validacion(nombre, prov, precio, costo, stock, tipo_producto, servicio):
            try:
                conn = sqlite3.connect(self.db_name)
                c = conn.cursor()

                # 🔥 AGREGADO: Obtener el umbral de stock del producto desde la base de datos
                c.execute("SELECT umbral_stock FROM inventario WHERE nombre = ?", (nombre,))
                umbral_result = c.fetchone()

                if umbral_result:
                   umbral_stock = umbral_result[0]  # Obtiene el umbral del producto
                else:
                   umbral_stock = 5  # Si no tiene umbral, usa el valor por defecto

                # 🔥 AGREGADO: Verificar si el stock ingresado está por debajo del umbral
                if int(stock) < umbral_stock:
                     messagebox.showwarning("Advertencia", f"Stock bajo: El producto '{nombre}' tiene solo {stock} unidades disponibles. (Umbral: {umbral_stock})")
                           
                codigo_barras = "" 
                consulta = "INSERT INTO inventario VALUES(?,?,?,?,?,?,?,?,?,?)"  
                parametros = (None, nombre, prov, precio, costo, stock, tipo_producto, servicio, umbral_stock, codigo_barras)
                self.eje_consulta(consulta, parametros)   
                self.mostrar()
                self.nombre.delete(0, END)
                self.proveedor.delete(0, END)     
                self.precio.delete(0, END)     
                self.costo.delete(0, END) 
                self.stock.delete(0, END) 
                self.tipo_producto.delete(0, END)
                self.servicio.delete(0, END)
            except Exception as e:
                messagebox.showwarning(title="Eror", message=f"Error al registrar el producto: {e}")
        else:
            messagebox.showwarning(title="Error",message="Rellene todos los campos correctamente")
            self.mostrar()

    def editar_producto(self):
        seleccion = self.tre.selection()
        if not seleccion:
            messagebox.showwarning("Editar producto", "Seleccione un producto para editar.")
            return

        item_id = self.tre.item(seleccion)["text"]     
        item_values = self.tre.item(seleccion)["values"]

        ventana_editar = Toplevel(self)
        ventana_editar.title("Editar producto")
        ventana_editar.geometry("400x425")
        ventana_editar.config(bg="#c6d9e3")

        lbl_nombre = Label(ventana_editar, text="Nombre: ",font="sans 14 bold",bg="#c6d9e3")
        lbl_nombre.grid(row=0, column=0,padx=10,pady=10)
        entry_nombre = Entry(ventana_editar, font="sans 14 bold")
        entry_nombre.grid(row=0,column=1,padx=10,pady=10)
        entry_nombre.insert(0, item_values[1])

        lbl_proveedor = Label(ventana_editar, text="Proveedor: ",font="sans 14 bold",bg="#c6d9e3")
        lbl_proveedor.grid(row=1, column=0,padx=10,pady=10)
        entry_proveedor = Entry(ventana_editar, font="sans 14 bold")
        entry_proveedor.grid(row=1,column=1,padx=10,pady=10)
        entry_proveedor.insert(0, item_values[2])

        lbl_precio = Label(ventana_editar, text="Precio: ",font="sans 14 bold",bg="#c6d9e3")
        lbl_precio.grid(row=2, column=0,padx=10,pady=10)
        entry_precio = Entry(ventana_editar, font="sans 14 bold")
        entry_precio.grid(row=2,column=1,padx=10,pady=10)
        entry_precio.insert(0, item_values[3].replace(",", ""))

        lbl_costo = Label(ventana_editar, text="Costo: ",font="sans 14 bold",bg="#c6d9e3")
        lbl_costo.grid(row=3, column=0,padx=10,pady=10)
        entry_costo = Entry(ventana_editar, font="sans 14 bold")
        entry_costo.grid(row=3,column=1,padx=10,pady=10)
        entry_costo.insert(0, str(item_values[4]).replace(",", ""))

        lbl_stock = Label(ventana_editar, text="Stock: ",font="sans 14 bold",bg="#c6d9e3")
        lbl_stock.grid(row=4, column=0,padx=10,pady=10)
        entry_stock = Entry(ventana_editar, font="sans 14 bold")
        entry_stock.grid(row=4,column=1,padx=10,pady=10)
        entry_stock.insert(0, item_values[5])

        lbl_tipo_producto = Label(ventana_editar, text="Tipo Prod: ",font="sans 14 bold",bg="#c6d9e3")
        lbl_tipo_producto.grid(row=5, column=0,padx=10,pady=10)
        entry_tipo_producto = Entry(ventana_editar, font="sans 14 bold")
        entry_tipo_producto.grid(row=5,column=1,padx=10,pady=10)
        entry_tipo_producto.insert(0, item_values[6])

        lbl_servicio = Label(ventana_editar, text="Tipo Prod: ",font="sans 14 bold",bg="#c6d9e3")
        lbl_servicio.grid(row=6, column=0,padx=10,pady=10)
        entry_servicio = Entry(ventana_editar, font="sans 14 bold")
        entry_servicio.grid(row=6,column=1,padx=10,pady=10)
        entry_servicio.insert(0, item_values[7])

        def guardar_cambios():
            nombre = entry_nombre.get()
            proveedor = entry_proveedor.get()
            precio = entry_precio.get()
            costo = entry_costo.get()
            stock = entry_stock.get()
            tipo_producto = entry_tipo_producto.get()
            servicio = entry_servicio.get()

            if not (nombre and proveedor and precio and costo and stock and tipo_producto and servicio):
                messagebox.showwarning("Guardar cambios", "Rellene todos los campos.")
                return
            
            try:
                precio = float(precio.replace(",", ""))
                costo = float(costo.replace(",", ""))
                stock = int(stock)  # 🔥 AGREGADO: Convertir stock a entero para comparaciones
            except ValueError:
                messagebox.showwarning("Guardar cambios", "Ingrese valores numericos validos para precio y costo.")
                return
            
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()

             # 🔥 AGREGADO: Obtener el umbral de stock del producto editado
            c.execute("SELECT umbral_stock FROM inventario WHERE id = ?", (item_id,))
            umbral_result = c.fetchone()

            if umbral_result:
                umbral_stock = umbral_result[0]  # Obtiene el umbral del producto
            else:
                umbral_stock = 5  # Si no tiene umbral, usa el valor por defecto 

            if stock < umbral_stock:
                messagebox.showwarning("Advertencia", f"Stock bajo: El producto '{nombre}' tiene solo {stock} unidades disponibles. (Umbral: {umbral_stock})")

            # 🔥 AGREGADO: Cerrar conexión después de obtener el umbral
            conn.close()    


            consulta = "UPDATE inventario SET nombre=?, Proveedor=?, precio=?, costo=?, stock=?, tipo_producto=?, es_servicio=? WHERE id=?"
            parametros = (nombre, proveedor, precio,costo,stock,tipo_producto,servicio ,item_id)
            self.eje_consulta(consulta,parametros)

            self.actualizar_inventario()

            ventana_editar.destroy()

        btn_guardar = Button(ventana_editar, text="Guardar cambios",font="sans 14 bold",command=guardar_cambios) 
        btn_guardar.place(x=80,y=350, width=240, height=40)

    def eliminar_producto(self):
        seleccion = self.tre.selection()
        if not seleccion:
            messagebox.showwarning("Eliminar producto", "Seleccione un producto para eliminar.")
            return

        item_id = self.tre.item(seleccion)["text"]  # Obtener el ID del producto seleccionado
        nombre_producto = self.tre.item(seleccion)["values"][1]  # Obtener el nombre del producto

        confirmacion = messagebox.askyesno("Confirmar eliminación", f"¿Está seguro de eliminar '{nombre_producto}'?")
        if not confirmacion:
            return

        try:
            consulta = "DELETE FROM inventario WHERE id = ?"
            self.eje_consulta(consulta, (item_id,))
            self.actualizar_inventario()
            messagebox.showinfo("Producto eliminado", f"El producto '{nombre_producto}' ha sido eliminado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")


    # --- FUNCIÓN PARA ACTUALIZAR CÓDIGO DE BARRAS SIN VALIDACIÓN DE SELECCIÓN ---
    def actualizar_codigo_barras(self):
        seleccionado = self.tre.selection()

        if not seleccionado:
            return  # Silencioso si no hay selección

        producto_id = self.tre.item(seleccionado, "values")[0]
        nuevo_codigo = self.entry_editar_codigo.get().strip()

        if not nuevo_codigo:
            messagebox.showerror("Error", "Ingrese un código de barras válido.")
            return

        try:
        # Verificamos si ese código ya está en otro producto
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT nombre FROM inventario WHERE codigo_barras = ? AND id != ?", (nuevo_codigo, producto_id))
            resultado = c.fetchone()
            conn.close()

            if resultado:
                messagebox.showwarning("Código existente", f"El código {nuevo_codigo} ya está asignado al producto: '{resultado[0]}'.")
                return

        # Si no está duplicado, actualizamos
            consulta = "UPDATE inventario SET codigo_barras = ? WHERE id = ?"
            self.eje_consulta(consulta, (nuevo_codigo, producto_id))

            messagebox.showinfo("Éxito", f"Código de barras actualizado correctamente para el producto ID {producto_id}")
            self.entry_editar_codigo.delete(0, tk.END)
            self.actualizar_inventario()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el código de barras: {e}")

    def buscar_por_proveedor(self, event):
        texto = self.entry_filtro_proveedor.get().strip().lower()
        for item in self.tre.get_children():
            self.tre.delete(item)

        if not texto:
            self.mostrar()
            return

        consulta = "SELECT * FROM inventario WHERE LOWER(proveedor) LIKE ? ORDER BY nombre ASC"
        result = self.eje_consulta(consulta, ('%' + texto + '%',))
        productos = result.fetchall()

        for elem in productos:
            try:
                precio_cop = "{:,.0f}".format(float(elem[3])) if elem[3] else ""
                costo_cop = "{:,.0f}".format(float(elem[4])) if elem[4] else ""  
            except ValueError:
                precio_cop = elem[3]
                costo_cop = elem[4]
            self.tre.insert("", 0, text=elem[0], values=(
                elem[0], elem[1], elem[2], precio_cop, costo_cop,
                elem[5], elem[6], elem[7], elem[8], elem[9] if len(elem) > 9 else ""
            ))
