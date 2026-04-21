import flet as ft
import requests

def obtener_registro_view(page, volver_bienvenida):
    # Campos de texto
    nombre = ft.TextField(label="Nombre Completo", border_color="#558B2F", width=300, color="black" , label_style=ft.TextStyle(color="#2E7D32"))
    correo = ft.TextField(label="Correo Electrónico", border_color="#558B2F", width=300, color="black" , label_style=ft.TextStyle(color="#2E7D32"))
    tel = ft.TextField(label="Teléfono", border_color="#558B2F", width=300, color="black" , label_style=ft.TextStyle(color="#2E7D32"))
    clave = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, border_color="#558B2F", width=300, color="black" , label_style=ft.TextStyle(color="#2E7D32"))
    rol = ft.Dropdown(
        label="Rol Familiar",
        width=300,
        options=[ft.dropdown.Option("Jefe"), ft.dropdown.Option("Familiar")],
        border_color="#558B2F",color="black" , label_style=ft.TextStyle(color="#2E7D32")
    )

    def registrar_usuario(e):
        payload = {
            "nombre": nombre.value,
            "correo": correo.value,
            "telefono": tel.value,
            "contrasena": clave.value,
            "tipo_usuario": rol.value
        }
        try:
            res = requests.post("http://127.0.0.1:8000/usuarios/", json=payload)
            if res.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("¡Usuario registrado!"))
                page.snack_bar.open = True
                volver_bienvenida(None)
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {res.json()['detail']}"))
                page.snack_bar.open = True
        except:
            page.snack_bar = ft.SnackBar(ft.Text("Error: ¿Encendiste el Backend?"))
            page.snack_bar.open = True
        page.update()

    return ft.Column(
        [
            ft.Text("Crear Cuenta", size=28, weight="bold", color="#558B2F"),
            nombre, correo, tel, clave, rol,
            ft.Container(height=20),
            ft.ElevatedButton("Finalizar Registro", bgcolor="#9575CD", color="white", width=280, on_click=registrar_usuario),
            ft.TextButton("Volver al inicio", on_click=volver_bienvenida)
        ],
        horizontal_alignment="center",
        scroll=ft.ScrollMode.AUTO # Por si la pantalla es pequeña y hay muchos campos
    )