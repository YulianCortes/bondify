import flet as ft

def obtener_bienvenida_view(page, ir_a_registro, ir_a_login):

    btn_numero = ft.ElevatedButton(
        "Entrar con número",
        width=280,
        height=50,
        color="white",
        bgcolor="#9575CD",
        on_click=ir_a_login  # <--- CONECTADO
    )

    btn_correo = ft.ElevatedButton(
        "Entrar con correo",
        width=280,
        height=50,
        color="white",
        bgcolor="#9575CD",
        on_click=ir_a_login  # <--- CONECTADO
    )

    btn_registro = ft.TextButton(
        "¿No tienes cuenta? Regístrate aquí",
        style=ft.ButtonStyle(color="#558B2F"),
        on_click=ir_a_registro # <--- CONECTADO
    )
    # Retornamos una Columna con todo tu diseño original
    return ft.Column(
        [
            ft.Text("¡Bienvenido a\nBondify!", size=35, weight="bold", color="#558B2F", text_align="center"),
            ft.Container(height=10),
            ft.Image(src="logo.png", width=220),
            ft.Container(height=10),
            ft.Text("\"Tu actitud decide qué altura alcanzarás\"", size=16, italic=True, color="#424242", text_align="center"),
            ft.Container(height=40),
            ft.Text("Inicia sesión o regístrate para continuar", size=14, color="#757575"),
            ft.Container(height=10),
            btn_numero, # <-- Usamos la variable conectada
            ft.Container(height=10),
            btn_correo, # <-- Usamos la variable conectada
            ft.Container(height=10),
            btn_registro # <-- Usamos la variable conectada
        ],
        horizontal_alignment="center"
    )