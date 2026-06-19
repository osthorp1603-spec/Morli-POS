import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import os
from ui.ventas import Ventas
import sys

def rutas(self, ruta):
    try:
        rutabase = sys._MEIPASS
    except Exception:
        rutabase = os.path.abspath(".")
    return os.path.join(rutabase, ruta)

try:
    base_path = sys._MEIPASS
except AttributeError:
    base_path = os.path.abspath(".")

DB_NAME = os.path.join(base_path, "database.db")

def generar_corte_z():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        try:
            c.execute("""
                SELECT inventario.tipo_producto, SUM(ventas.cantidad), SUM(ventas.subtotal)
                FROM ventas
                LEFT JOIN inventario ON ventas.nombre_articulo = inventario.nombre
                WHERE DATE(ventas.fecha) = DATE('now', 'localtime')
                GROUP BY inventario.tipo_producto
                HAVING SUM(ventas.cantidad) IS NOT NULL;
            """)
            resumen_ventas = c.fetchall()

            if not resumen_ventas:
                print("⚠ ADVERTENCIA: No hay datos en resumen_ventas.")
        except sqlite3.Error as e:
            print(f"❌ ERROR al obtener resumen_ventas: {e}")
            resumen_ventas = []

        c.execute("""
            SELECT inventario.tipo_producto, SUM(rf_registros.cantidad), SUM(rf_registros.subtotal)
            FROM rf_registros
            LEFT JOIN inventario ON rf_registros.nombre_articulo = inventario.nombre
            WHERE rf_registros.fecha LIKE ?
            GROUP BY inventario.tipo_producto
        """, (fecha_hoy[:10] + "%",))
        resumen_rf = c.fetchall()

        c.execute("""
            SELECT SUM(subtotal)
            FROM rf_registros
            WHERE rf_registros.fecha LIKE ?
        """, (fecha_hoy[:10] + "%",))
        total_rf = c.fetchone()[0] or 0

        c.execute("SELECT SUM(subtotal) FROM ventas WHERE DATE(fecha) = DATE('now', 'localtime');")
        total_vendido = c.fetchone()[0] or 0

        c.execute("""
            SELECT SUM(subtotal) FROM ventas
            WHERE DATE(fecha) = DATE('now', 'localtime')
            AND LOWER(TRIM(tipo_pago)) = 'efectivo';
        """)
        total_efectivo = c.fetchone()[0] or 0

        c.execute("SELECT SUM(subtotal) FROM ventas WHERE DATE(fecha) = DATE('now', 'localtime') AND tipo_pago = 'QR';")
        total_qr = c.fetchone()[0] or 0

        c.execute("SELECT SUM(subtotal) FROM ventas WHERE DATE(fecha) = DATE('now', 'localtime') AND tipo_pago = 'Tarjeta';")
        total_tarjeta = c.fetchone()[0] or 0

        c.execute("SELECT SUM(cantidad) FROM ventas WHERE DATE(fecha) = DATE('now', 'localtime');")
        total_items_vendidos = c.fetchone()[0] or 0

        c.execute("""
            SELECT SUM(monto) FROM egresos_dia
            WHERE DATE(fecha_hora) = DATE('now', 'localtime') AND metodo = 'Efectivo';
        """)
        total_egresos = c.fetchone()[0] or 0

        generar_corte_z_pdf(resumen_ventas, resumen_rf, total_rf, total_vendido,
                            total_efectivo, total_qr, total_tarjeta, total_items_vendidos,
                            fecha_hoy, total_egresos)

        c.execute("DELETE FROM ventas WHERE DATE(fecha) = DATE('now', 'localtime');")
        c.execute("DELETE FROM sqlite_sequence WHERE name='ventas'")
        c.execute("INSERT INTO corte_z (cerrado, fecha) VALUES (1, ?)", (fecha_hoy,))
        conn.commit()

        c.execute("DELETE FROM ventas_temp WHERE fecha LIKE ?", (fecha_hoy[:10] + "%",))
        c.execute("DELETE FROM rf_registros WHERE fecha LIKE ?", (fecha_hoy[:10] + "%",))
        c.execute("DELETE FROM egresos_dia WHERE DATE(fecha_hora) = DATE('now', 'localtime')")
        c.execute("DELETE FROM ventas")
        c.execute("DELETE FROM sqlite_sequence WHERE name='ventas'")
        c.execute("INSERT INTO corte_z (cerrado, fecha) VALUES (1, ?)", (fecha_hoy,))
        conn.commit()

        Ventas.resetear_numero_factura()

def generar_corte_z_pdf(resumen_ventas, resumen_rf, total_rf, total_vendido,
                        total_efectivo, total_qr, total_tarjeta, total_items_vendidos,
                        fecha_hoy, total_egresos):

    print("📄 Generando PDF de Corte Z...")
    width = 2.25 * inch
    base_height = 6 * inch
    height = base_height
    archivo_pdf = f"corte_z/corte_{fecha_hoy.replace(':', '-')}.pdf"
    if not os.path.exists("corte_z"):
        os.makedirs("corte_z")

    c = canvas.Canvas(archivo_pdf, pagesize=(width, height))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(10, height - 20, f"Corte Z - {fecha_hoy}")

    c.setFont("Helvetica-Bold", 7)
    c.drawString(10, height - 40, "Resumen:")
    y = height - 60
    c.setFont("Helvetica", 6)
    for tipo, cantidad, total in resumen_ventas:
        c.drawString(10, y, f"{tipo}: {cantidad} vendidos - ${total:,.0f}")
        y -= 10

    c.setFont("Helvetica-Bold", 8)
    c.drawString(10, y - 10, f"BRUTO: ${total_vendido:,.0f}")
    c.drawString(10, y - 20, f"Efectivo: ${total_efectivo:,.0f}")
    c.drawString(10, y - 30, f"QR: ${total_qr:,.0f}")
    c.drawString(10, y - 40, f"Tarjeta: ${total_tarjeta:,.0f}")
    c.drawString(10, y - 50, f"TL: {total_items_vendidos}")

    y -= 70
    c.setFont("Helvetica-Bold", 7)
    c.drawString(10, y, f"Salida Efectivo: ${total_egresos:,.0f}")
    y -= 10
    c.drawString(10, y, f"Efectivo Final: ${total_efectivo - total_egresos:,.0f}")
    y -= 20

    c.setFont("Helvetica-Bold", 7)
    c.drawString(10, y, "Ventas Canceladas (RF):")
    y -= 10
    c.setFont("Helvetica", 6)
    for tipo, cantidad, total in resumen_rf:
        c.drawString(10, y, f"{tipo}: {cantidad} cancelados - ${total:,.0f}")
        y -= 10

    c.setFont("Helvetica-Bold", 8)
    c.drawString(10, y, f"Total RF Cancelado: ${total_rf:,.0f}")
    y -= 20

    c.save()
    print(f"Corte Z generado en {archivo_pdf}")

    # --- Abrir cajón de dinero ---
    try:
        import win32print
        nombre_impresora = "POSPrinter POS80"  # Ajustar si tu impresora tiene otro nombre
        hPrinter = win32print.OpenPrinter(nombre_impresora)
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Abrir Cajón Corte Z", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, b"\x1B\x70\x00\x19\xFA")
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
        win32print.ClosePrinter(hPrinter)
    except Exception as e:
        print("No se pudo abrir el cajón durante el Corte Z:", e)

    os.startfile(os.path.abspath(archivo_pdf))
