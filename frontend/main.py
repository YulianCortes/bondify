import flet as ft
import sys
import os
import requests 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from frontend.bienvenida_view import obtener_bienvenida_view
from frontend.login_view import obtener_login_view
from frontend.registro_view import obtener_registro_view
from frontend.home_view import obtener_home_view
from frontend.familia_view import obtener_familia_view
from frontend.actividades_view import obtener_actividades_view
from frontend.calendario_view import obtener_calendario_view
from frontend.perfil_view import obtener_perfil_view 
from frontend.configuracion_view import obtener_configuracion_view
from frontend.gestion_familia_view import obtener_gestion_familia_view

def main(page: ft.Page):
    page.padding = 0 
    page.spacing = 0
    page.title = "Bondify"
    page.bgcolor = "#D1E8E4"
    page.window_width = 400
    page.window_height = 750
    page.horizontal_alignment = "center"
    page.vertical_alignment = "start"

    # --- MEMORIA DE SESIÓN (Agregamos primer_nombre) ---
    sesion = {"nombre": None, "rol": None, "id_usuario": None, "primer_nombre": None}

    # 1. Barra de navegación inferior
    def crear_barra():
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Image(src="home.png", width=40, height=40), 
                             on_click=lambda e: navegar("home"), padding=10),
                ft.Container(content=ft.Image(src="plant.png", width=40, height=40), 
                             on_click=lambda e: navegar("actividades"), padding=10),
                ft.Container(content=ft.Image(src="calendar.png", width=40, height=40), 
                             on_click=lambda e: navegar("calendario"), padding=10),
                ft.Container(content=ft.Image(src="family.png", width=40, height=40), 
                             on_click=lambda e: navegar("familia"), padding=10),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor="#E1BEE7", height=80, width=float('inf'), padding=0, margin=0
        )

    # 2. Funciones puente para navegación
    def ir_a_familia(e): navegar("familia")
    def ir_a_actividades(e): navegar("actividades") 
    def ir_a_mis_actividades(e): navegar("mis_actividades") 
    def ir_a_calendario(e): navegar("calendario")
    def ir_a_perfil(e): navegar("perfil") 
    def ir_a_configuracion(e): navegar("configuracion")
    def ir_a_gestion_familia(e): navegar("gestion_familia")

    # 3. Función maestra de navegación (Ahora recibe primer_nombre)
    def navegar(destino, nombre=None, rol=None, id_usuario=None, primer_nombre=None):
        if nombre: sesion["nombre"] = nombre
        if rol: sesion["rol"] = rol
        if id_usuario: sesion["id_usuario"] = id_usuario
        if primer_nombre: sesion["primer_nombre"] = primer_nombre # <-- Guardamos el nombre del perfil
        
        page.clean()
        nombre_actual = sesion["nombre"]
        rol_actual = sesion["rol"]
        id_actual = sesion["id_usuario"]
        p_nombre_actual = sesion["primer_nombre"] # <-- Recuperamos el nombre del perfil

        if destino == "home":
            page.add(obtener_home_view(
                page, nombre_actual, rol_actual, 
                ir_a_bienvenida, ir_a_familia, ir_a_actividades, 
                ir_a_calendario, ir_a_perfil, ir_a_mis_actividades, 
                ir_a_configuracion, ir_a_gestion_familia,
                primer_nombre=p_nombre_actual # <-- PASAMOS EL NOMBRE AL HOME
            ))
        
        elif destino == "familia":
            page.add(obtener_familia_view(page, lambda e: navegar("home")))
        
        elif destino == "gestion_familia":
            usuario_actual = {"id_usuario": id_actual, "tipo_usuario": rol_actual}
            page.add(obtener_gestion_familia_view(page, lambda e: navegar("home"), usuario_actual))
        
        elif destino == "actividades":
            # CORRECCIÓN: Pasamos el diccionario completo, no solo el rol
            usuario_actual = {"id_usuario": id_actual, "tipo_usuario": rol_actual}
            page.add(obtener_actividades_view(page, lambda e: navegar("home"), usuario_actual))

        elif destino == "mis_actividades":
            # CORRECCIÓN: Pasamos el diccionario y quitamos modo="personal" para evitar el error
            usuario_actual = {"id_usuario": id_actual, "tipo_usuario": rol_actual}
            page.add(obtener_actividades_view(page, lambda e: navegar("home"), usuario_actual))
        
        elif destino == "calendario":
            page.add(obtener_calendario_view(page, lambda e: navegar("home")))
        
        elif destino == "perfil":
            try:
                url = f"http://127.0.0.1:8000/usuarios/{id_actual}/perfil"
                res = requests.get(url, timeout=5)
                usuario_actual = res.json() if res.status_code == 200 else {}
                
                # Sincronizamos el primer_nombre guardado con la sesión
                sesion["primer_nombre"] = usuario_actual.get("primer_nombre")
                
                usuario_actual["id_usuario"] = id_actual
                usuario_actual["tipo_usuario"] = rol_actual
            except:
                usuario_actual = {"id_usuario": id_actual, "tipo_usuario": rol_actual}

            # El lambda ahora usa p_n para recibir el nombre desde el perfil
            page.add(obtener_perfil_view(page, lambda p_n=None: navegar("home", primer_nombre=p_n), usuario_actual))
        
        elif destino == "configuracion":
            page.add(obtener_configuracion_view(page, lambda e: navegar("home")))
        
        # Barra visible solo en pantallas principales
        if destino not in ["bienvenida", "login", "registro", "perfil", "configuracion", "gestion_familia"]:
            page.add(crear_barra())
        
        page.update()

    # 4. Funciones de inicio
    def ir_a_login(e):
        page.clean()
        page.add(obtener_login_view(page, ir_a_bienvenida, lambda n, r, i: navegar("home", n, r, i)))
        page.update()
        
    def ir_a_registro(e):
        page.clean()
        page.add(obtener_registro_view(page, ir_a_bienvenida))
        page.update()

    def ir_a_bienvenida(e):
        page.clean()
        page.add(obtener_bienvenida_view(page, ir_a_registro, ir_a_login))
        page.update()

    ir_a_bienvenida(None)

ft.app(target=main, assets_dir="assets")