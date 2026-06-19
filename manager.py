from tkinter import Tk, Frame, Button, messagebox
from ui.container import Container
from ttkthemes import ThemedStyle
from tkinter import Tk, Frame, Button
from ui.ventas import Ventas
from logica.corte_z import generar_corte_z
import sqlite3
import sys
import os  

class Manager(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Sistema POS MORLI V 1.0")
        self.resizable(False, False)
        self.configure(bg="#c6d9e3")
        self.geometry("800x480+120+20")
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        self.db_name = os.path.join(base_path, "database.db")
        ruta=self.rutas(r"icono.ico")
        self.iconbitmap(ruta)

        self.container = Frame(self, bg="#c6d9e3")
        self.container.pack(fill="both", expand=True)

        self.ventas_frame = Ventas(self.container)
        self.ventas_frame.pack(fill="both", expand=True)

        self.boton_corte_z = Button(self, text=" Z ", font="sans 14 bold", bg="red", fg="white",
                                    command=self.confirmar_corte_z)  # Ejecuta la función de Corte Z
        self.boton_corte_z.place(x=695, y=320, width=80, height=38)  #x=500,y=130,width=240,height=60

        self.frames = {
            Container: None
        }
        
        self.load_frames()

        self.show_frame(Container)
        
        self.set_theme()
    
    def confirmar_corte_z(self):
        respuesta = messagebox.askyesno("Confirmación", "¿Estás seguro de realizar el CORTE Z?\nEsto eliminará el historial del día.")
        
        if respuesta:
            generar_corte_z()

    def rutas(self, ruta):
        try:
            rutabase = sys._MEIPASS
        except Exception:
            rutabase=os.path.abspath(".")
        return os.path.join(rutabase,ruta)       

# PRIMERA FUNCION GUARDAR INSTANCIAS EN LA PARTE SUPERIOR
    def load_frames(self):
        for FrameClass in self.frames.keys():
            frame = FrameClass(self.container,self)
            self.frames[FrameClass] = frame
# SEGUNDA FUNCION
    def show_frame(self, frame_class):    
        frame = self.frames[frame_class]
        frame.tkraise()

 #NUEVA FUNCION CAMBIAR ESTILO 
    def set_theme(self):
        style = ThemedStyle(self)
        style.set_theme("breeze")          
# DEFINIR UNA INSTANCIA CLASE MANAGER LA QUE INICIA BUCLE DE LA APLICACION
if __name__ == "__main__":    
        app = Manager()
        app.mainloop()

   