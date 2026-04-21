import flet as ft
# Importamos nuestras nuevas vistas
from bienvenida_view import obtener_bienvenida_view
from login_view import obtener_login_view
from registro_view import obtener_registro_view
from home_view import obtener_home_view
def main(page: ft.Page):
    page.title = "Bondify"
    page.bgcolor = "#D1E8E4"
    page.window_width = 400
    page.window_height = 750
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    def ir_a_home(nombre, rol):
        page.clean()
        page.add(obtener_home_view(page, nombre, rol, ir_a_bienvenida))
        page.update()
        
    def ir_a_login(e):
        page.clean()
        page.add(obtener_login_view(page, ir_a_bienvenida, ir_a_home))
    def ir_a_registro(e):
        page.clean()
        page.add(obtener_registro_view(page, ir_a_bienvenida))

    def ir_a_bienvenida(e):
        page.clean()
        page.add(obtener_bienvenida_view(page, ir_a_registro, ir_a_login))
    
    
    # Iniciamos con la bienvenida
    ir_a_bienvenida(None)

ft.app(target=main, assets_dir="assets")