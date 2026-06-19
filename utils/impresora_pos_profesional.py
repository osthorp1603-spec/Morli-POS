# impresora_pos_profesional.py
# -----------------------------
# Impresora térmica profesional para Morli Giftstore (Modo RAW ancho mejorado)

import win32print
import win32ui
import sys
import os

def rutas(self, ruta):
        try:
            rutabase = sys._MEIPASS
        except Exception:
            rutabase=os.path.abspath(".")
        return os.path.join(rutabase,ruta) 

def imprimir_ticket_pos(productos, total, tipo_pago, vuelto, cantidad_pagada, factura_numero, fecha):
    """
    Imprime un ticket de venta profesional directamente en una impresora POS térmica en modo RAW (texto puro).
    """

    nombre_impresora = "POSPrinter POS80"  # Nombre exacto de tu impresora

    # --- Construcción del ticket (puro texto, mejor aprovechando el ancho) ---
    ticket = ""

    # --- Comando para abrir cajón de dinero (EPSON ESC/POS) ---
    if tipo_pago == "Efectivo": 
        ticket += "\x1B\x70\x00\x19\xFA"

    ticket += "========================================\n"
    ticket += "           MORLI GIFTSTORE\n"
    ticket += "         NIT: 1085258600-8\n"
    ticket += "   Cra 98 # 16-50 Local J1045\n"
    ticket += "     Tel: (+57) 3223265508\n"
    ticket += "         Cali - Colombia\n"
    ticket += "========================================\n"
    ticket += f"Factura: {factura_numero:05d}\n"
    ticket += f"Fecha: {fecha}\n"
    ticket += "----------------------------------------\n"
    ticket += "Producto              Cant      Subtotal\n"
    ticket += "----------------------------------------\n"

    for producto, precio, cantidad, subtotal in productos:
        producto_str = str(producto)[:18].ljust(18)  # Más espacio para nombre
        cantidad_str = str(cantidad).rjust(4)
        subtotal_str = f"${subtotal:,.0f}".rjust(10)
        ticket += f"{producto_str} {cantidad_str} {subtotal_str}\n"

    ticket += "----------------------------------------\n"
    ticket += f"TOTAL:                ${total:,.0f}\n"

    if cantidad_pagada is not None:
        ticket += f"CAJA:                 ${cantidad_pagada:,.0f}\n"

    if tipo_pago == "Efectivo" and vuelto is not None:
        ticket += f"CAMBIO:               ${vuelto:,.0f}\n"

    ticket += f"PAGO: {tipo_pago}\n"
    ticket += "========================================\n"
    ticket += "        GRACIAS POR SU COMPRA\n"
    ticket += "========================================\n"
    ticket += "\n\n\n\n\n\n\n\n"  # Saltos para facilitar corte manual

    # --- Enviar a impresora ---
    ticket_bytes = ticket.encode('utf-8')

    try:
        hPrinter = win32print.OpenPrinter(nombre_impresora)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Ticket Morli", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, ticket_bytes)
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        print("[ERROR] Error al imprimir el ticket:", e)
