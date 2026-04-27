import flet as ft
import requests
import re

def obtener_registro_view(page: ft.Page, volver_bienvenida):
    # --- 1. DIÁLOGO DE ERROR ESTILIZADO (Estilo Pixar) ---
    txt_error = ft.Text("", color="#212121", size=16, text_align=ft.TextAlign.CENTER)
    
    def cerrar_dialogo(e):
        dialogo_error.open = False
        page.update()

    dialogo_error = ft.AlertDialog(
        modal=True,
        bgcolor="#FFFFFF",
        shape=ft.RoundedRectangleBorder(radius=20),
        title=ft.Row([
            ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#B71C1C", size=35),
            ft.Text(" ¡Atención!", color="#B71C1C", weight="bold")
        ], alignment=ft.MainAxisAlignment.CENTER),
        content=ft.Container(
            content=txt_error,
            padding=10,
            width=300
        ),
        actions=[
            ft.TextButton("Entendido", on_click=cerrar_dialogo)
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    
    # Aseguramos que el diálogo esté en el overlay
    if dialogo_error not in page.overlay:
        page.overlay.append(dialogo_error)

    # --- CAMPOS DE TEXTO ---
    nombre = ft.TextField(label="Nombre Completo", border_color="#558B2F", width=300, color="black", label_style=ft.TextStyle(color="#2E7D32"))
    correo = ft.TextField(label="Correo Electrónico", border_color="#558B2F", width=300, color="black", label_style=ft.TextStyle(color="#2E7D32"))
    tel = ft.TextField(
        label="Teléfono", border_color="#558B2F", width=300, color="black", 
        label_style=ft.TextStyle(color="#2E7D32"),
        input_filter=ft.NumbersOnlyInputFilter()
    )
    clave = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, border_color="#558B2F", width=300, color="black", label_style=ft.TextStyle(color="#2E7D32"))
    
    rol = ft.Dropdown(
        label="Rol Familiar",
        width=300,
        options=[ft.dropdown.Option("Jefe"), ft.dropdown.Option("Familiar")],
        border_color="#558B2F", color="black", label_style=ft.TextStyle(color="#2E7D32")
    )

    def registrar_usuario(e):
        # 1. Validaciones básicas de formato
        if not all([nombre.value, correo.value, tel.value, clave.value, rol.value]):
            txt_error.value = "Por favor, completa todos los campos del formulario."
            dialogo_error.open = True
            page.update()
            return

        email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.match(email_regex, correo.value.lower()):
            txt_error.value = "El formato del correo no es válido."
            dialogo_error.open = True
            page.update()
            return

        # 2. Envío de datos al Backend
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
                page.snack_bar = ft.SnackBar(ft.Text("✨ ¡Registro exitoso!"), bgcolor="#3C7517")
                page.snack_bar.open = True
                volver_bienvenida(None)
            else:
                # CAPTURA DEL ERROR ESPECÍFICO (Correo o Número ya registrados)
                # El backend envía el detalle en el JSON, lo mostramos directamente
                error_data = res.json()
                mensaje_servidor = error_data.get('detail', 'Ocurrió un error en el registro')
                
                txt_error.value = mensaje_servidor
                dialogo_error.open = True
            
        except Exception as ex:
            txt_error.value = "No se pudo conectar con el servidor. Verifica tu conexión."
            dialogo_error.open = True
            
        page.update()

    # --- RETORNO DE LA VISTA CON CENTRADO ABSOLUTO ---
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER, # Esto centra el contenido en toda la pantalla
        bgcolor="#D1E8E4", # Fondo Pixar suave
        content=ft.Column(
            [
                ft.Text("Crear Cuenta", size=32, weight="bold", color="#388E3C"),
                nombre, 
                correo, 
                tel, 
                clave, 
                rol,
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Finalizar Registro", 
                    bgcolor="#9575CD", 
                    color="white", 
                    width=280, 
                    height=50,
                    on_click=registrar_usuario
                ),
                ft.TextButton("Volver al inicio", on_click=volver_bienvenida)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
            scroll=ft.ScrollMode.AUTO
        )
    )