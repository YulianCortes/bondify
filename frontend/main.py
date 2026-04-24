import flet as ft
import sys
import os
import requests 

# Configuración de rutas para encontrar las vistas
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
    # Configuración estética de la ventana
    page.padding = 0 
    page.spacing = 0
    page.title = "Bondify"
    page.bgcolor = "#D1E8E4"
    page.window_width = 400
    page.window_height = 750
    page.horizontal_alignment = "center"
    page.vertical_alignment = "start"

    # --- MEMORIA DE SESIÓN CENTRALIZADA ---
    # Usamos 'tipo_usuario' para que coincida 100% con el Backend
    sesion = {
        "nombre": None, 
        "tipo_usuario": None, 
        "id_usuario": None, 
        "primer_nombre": None
    }

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
            ], alignment="spaceAround"),
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

    # 3. Función maestra de navegación (REPARADA)
    def navegar(destino, nombre=None, rol=None, id_usuario=None, primer_nombre=None):
        # Actualizamos la memoria global con lo que recibamos
        if nombre: sesion["nombre"] = nombre
        if rol: sesion["tipo_usuario"] = rol 
        if id_usuario: sesion["id_usuario"] = id_usuario
        if primer_nombre: sesion["primer_nombre"] = primer_nombre 
        
        page.clean()
        
        # Sincronización rápida con el servidor para evitar que se pierda el nombre
        if destino == "home" and sesion["id_usuario"]:
            try:
                r = requests.get(f"http://127.0.0.1:8000/usuarios/{sesion['id_usuario']}/perfil", timeout=1)
                if r.status_code == 200:
                    datos_p = r.json()
                    sesion["primer_nombre"] = datos_p.get("primer_nombre")
            except: pass

        # Parámetros listos para las vistas
        nombre_act = sesion["nombre"]
        rol_act = sesion["tipo_usuario"]
        id_act = sesion["id_usuario"]
        p_nombre_act = sesion["primer_nombre"]

        if destino == "home":
            page.add(obtener_home_view(
                page, nombre_act, rol_act, 
                ir_a_bienvenida, ir_a_familia, ir_a_actividades, 
                ir_a_calendario, ir_a_perfil, ir_a_mis_actividades, 
                ir_a_configuracion, ir_a_gestion_familia,
                sesion, # Pasamos el diccionario completo para la racha
                primer_nombre=p_nombre_act
            ))
        
        elif destino == "familia":
            page.add(obtener_familia_view(page, lambda e: navegar("home")))
        
        elif destino == "gestion_familia":
            # Pasamos la sesión para que el botón de borrar tenga el id_jefe
            page.add(obtener_gestion_familia_view(page, lambda e: navegar("home"), sesion))
        
        elif destino == "actividades" or destino == "mis_actividades":
            # Pasamos la sesión para que reconozca el rol de Jefe
            page.add(obtener_actividades_view(page, lambda e: navegar("home"), sesion))
        
        elif destino == "calendario":
            page.add(obtener_calendario_view(page, lambda e: navegar("home")))
        
        elif destino == "perfil":
            # --- NUEVA LÓGICA: CARGAR DATOS REALES DE LA DB ---
            datos_perfil_completos = sesion.copy() 
            try:
                respuesta_perfil = requests.get(f"http://127.0.0.1:8000/usuarios/{sesion['id_usuario']}/perfil", timeout=2)
                if respuesta_perfil.status_code == 200:
                    datos_perfil_completos = respuesta_perfil.json()
                    # Nos aseguramos de mantener el rol y el id por si el json del perfil no los trae
                    datos_perfil_completos["id_usuario"] = sesion["id_usuario"]
                    datos_perfil_completos["tipo_usuario"] = sesion["tipo_usuario"]
            except Exception as e:
                print(f"Error cargando datos del perfil: {e}")

            # FIX p_n: Hacemos que el parámetro sea opcional para evitar el error rojo
            page.add(obtener_perfil_view(
                page, 
                lambda p_n=None: navegar("home", primer_nombre=p_n), 
                datos_perfil_completos # <--- Pasamos el diccionario con TODO (edad, apellido, etc.)
            ))
        
        elif destino == "configuracion":
            page.add(obtener_configuracion_view(page, lambda e: navegar("home")))
        
        # Mostrar barra solo en las pantallas principales
        if destino not in ["bienvenida", "login", "registro", "perfil", "configuracion", "gestion_familia"]:
            page.add(crear_barra())
        
        page.update()

    # 4. Funciones de inicio de flujo
    def ir_a_login(e):
        page.clean()
        page.add(obtener_login_view(
            page, 
            ir_a_bienvenida, 
            lambda n, r, i: navegar("home", n, r, i)
        ))
        page.update()
        
    def ir_a_registro(e):
        page.clean()
        page.add(obtener_registro_view(page, ir_a_bienvenida))
        page.update()

    def ir_a_bienvenida(e):
        page.clean()
        page.add(obtener_bienvenida_view(page, ir_a_registro, ir_a_login))
        page.update()

    # Lanzar la app
    ir_a_bienvenida(None)

# Importante: assets_dir permite que Flet encuentre tus .jpeg de la mascota
ft.app(target=main, assets_dir="assets")