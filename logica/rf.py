import sqlite3
from tkinter import messagebox
import sys
import os

def rutas(self, ruta):
        try:
            rutabase = sys._MEIPASS
        except Exception:
            rutabase=os.path.abspath(".")
        return os.path.join(rutabase,ruta) 

try:
    base_path = sys._MEIPASS
except AttributeError:
    base_path = os.path.abspath(".")
DB_NAME = os.path.join(base_path, "database.db")

def mover_a_rf_registros(tree, actualizar_total):
    """Mueve la venta seleccionada de ventas_temp a rf_registros y la elimina del Treeview."""
    seleccion = tree.selection()
    
    if not seleccion:
        messagebox.showwarning("Cancelar Venta", "Seleccione un producto para cancelar.")
        return

    # Obtener los datos del producto seleccionado en el Treeview
    item = tree.item(seleccion)["values"]
    if not item:
        messagebox.showerror("Error", "No se pudo obtener la información del producto.")
        return

    producto = item[0]  # Nombre del producto
    precio = int(item[1].replace(",", ""))  # Convertir a número
    cantidad = int(item[2])  # Cantidad
    subtotal = int(item[3].replace(",", ""))  # Subtotal

    # Confirmación antes de cancelar la venta
    confirmar = messagebox.askyesno("Confirmar Cancelación", f"¿Está seguro de cancelar '{producto}'?")
    if not confirmar:
        return  # Si el usuario presiona "No", se cancela la acción

    try:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()

            # Obtener los datos adicionales de la tabla ventas_temp
            c.execute("""
                SELECT factura, fecha FROM ventas_temp
                WHERE nombre_articulo = ? AND valor_articulo = ? AND cantidad = ? AND subtotal = ?
                ORDER BY id DESC LIMIT 1
            """, (producto, precio, cantidad, subtotal))
            datos_venta = c.fetchone()
            
            if datos_venta:
                factura, fecha = datos_venta

                # Insertar en rf_registros
                c.execute("""
                    INSERT INTO rf_registros (factura, nombre_articulo, valor_articulo, cantidad, subtotal, tipo_pago, fecha)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                """, (factura, producto, precio, cantidad, subtotal, "No Pagado"))
                 #inserta a historial rf
                c.execute("""
                    INSERT INTO historial_rf (factura, nombre_articulo, valor_articulo, cantidad, subtotal, tipo_pago, fecha)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                """, (factura, producto, precio, cantidad, subtotal, "No Pagado"))

                # Eliminar SOLO UN registro de ventas_temp usando una subconsulta
                c.execute("""
                    DELETE FROM ventas_temp WHERE id = (
                        SELECT id FROM ventas_temp 
                        WHERE factura = ? AND nombre_articulo = ? 
                        AND valor_articulo = ? AND cantidad = ? AND subtotal = ?
                        ORDER BY id DESC LIMIT 1
                    )
                """, (factura, producto, precio, cantidad, subtotal))

                conn.commit()

                # Eliminar del Treeview
                tree.delete(seleccion)

                # Actualizar total de la venta
                actualizar_total()

                messagebox.showinfo("Venta Cancelada", "El producto ha sido cancelado y enviado a RF Registros.")

            else:
                messagebox.showerror("Error", "No se encontró el producto en ventas_temp.")

    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error al cancelar la venta: {e}")