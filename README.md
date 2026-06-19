# Control de Asistencia de Trabajadores
## Descripción
Sistema de punto de venta (POS) para la gestión integral de una tienda de regalos. 
Permite registrar ventas con lector de código de barras, controlar el inventario, 
gestionar clientes, crear anchetas/decoraciones, generar facturas e imprimir tickets 
en impresora térmica. Incluye un módulo contable completo con reportes de utilidad, 
flujo de caja, estado de resultados, balance general y más.

## Tecnologías utilizadas

- Python
- Tkinter (interfaz gráfica)
- SQLite (base de datos local)
- ReportLab (generación de facturas y etiquetas en PDF)
- win32print (impresión térmica POS y apertura de cajón)
- Matplotlib (gráficos de reportes)
- Arquitectura modular (UI, Lógica y Utilidades)

## Estructura del proyecto
```
MorliPOS/

│

├── index.py

├── manager.py

├── MorliPOS.spec

├── icono.ico

│

├── database.db

├── clientes.db

├── codigos.db

│

├── ui/

│   ├── ventas.py

│   ├── inventario.py

│   ├── container.py

│   ├── clientes.py

│   ├── anchetas.py

│   ├── movimientos_inventario.py

│   ├── prestamos_ventana.py

│   └── flujo_caja_ventana.py

│

├── logica/

│   ├── corte_z.py

│   ├── rf.py

│   ├── generar_codigo.py

│   ├── reporte_utilidad.py

│   ├── balance_general.py

│   ├── estado_resultados.py

│   ├── punto_equilibrio.py

│   ├── deudas_proveedores.py

│   ├── gastos.py

│   └── historial_contable_mes.py

│

├── utils/

│   └── impresora_pos_profesional.py

│

├── imagenes/

│   └── logo e imágenes del sistema

│

├── facturas/

├── corte_z/

└── codigos/

└── evidencias/
```
## Explicación técnica

El sistema fue desarrollado utilizando Python con interfaz gráfica en Tkinter y 
una base de datos SQLite local.

El proyecto sigue una arquitectura modular separando responsabilidades:

- **UI:** contiene las ventanas del sistema: ventas, inventario, clientes, anchetas, 
  movimientos de inventario y las ventanas contables de interfaz.
- **Lógica:** contiene las operaciones de negocio y reportes: corte Z, cancelaciones (RF), 
  generación de códigos de barras, y todos los cálculos contables (utilidad, balance, 
  estado de resultados, punto de equilibrio, etc.).
- **Utilidades:** herramientas auxiliares como la impresión de tickets en la impresora térmica.


El flujo general del sistema es:

1. El vendedor registra los productos mediante el lector de código de barras o búsqueda manual.
2. Al cobrar, el sistema acepta pago en efectivo, QR, tarjeta o pago dividido.
3. La venta se guarda en la base de datos, se descuenta el stock y se genera la factura en PDF.
4. El ticket se imprime en la impresora térmica y, si el pago es en efectivo, se abre el cajón.
5. Al final del día se realiza el Corte Z, que genera el resumen de caja y cierra la jornada.
6. El administrador puede consultar reportes de utilidad, inventario y la contabilidad completa.

## Evidencias

![ventana_principal](evidencias/ventanaprincipal.png)
![ventana_de_compra](evidencias/ventanaventa.png)
![ventana_de_pago](evidencias/ventanapago.png)
![visualizar_ventas_diarias-mes](evidencias/filtroventas.png)
![ventana_inventario](evidencias/inventario.png)
![ventana_contable](evidencias/contable.png)