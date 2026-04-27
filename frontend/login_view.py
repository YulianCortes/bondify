import flet as ft
import requests

def obtener_login_view(page: ft.Page, volver_bienvenida, ir_a_home):
    # --- 1. DIÁLOGO DE ERROR (Estilo Pixar/Profesional) ---
    txt_error = ft.Text("", color="#212121", size=16, text_align=ft.TextAlign.CENTER)
    
    def cerrar_dialogo(e):
        dialogo_error.open = False
        page.update()

    dialogo_error = ft.AlertDialog(
        modal=True,
        bgcolor="#FFFFFF",
        shape=ft.RoundedRectangleBorder(radius=20),
        title=ft.Row([
            ft.Icon(ft.Icons.LOCK_PERSON_ROUNDED, color="#B71C1C", size=35),
            ft.Text(" Error de Acceso", color="#B71C1C", weight="bold")
        ], alignment=ft.MainAxisAlignment.CENTER),
        content=ft.Container(content=txt_error, padding=10, width=300),
        actions=[ft.TextButton("Reintentar", on_click=cerrar_dialogo)],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    
    # Agregamos el diálogo al overlay
    if dialogo_error not in page.overlay:
        page.overlay.append(dialogo_error)

    # --- CAMPOS DE ENTRADA ---
    usuario_tf = ft.TextField(
        label="Correo o Teléfono", 
        border_color="#558B2F", 
        width=300,
        color="black",
        label_style=ft.TextStyle(color="#558B2F"),
        prefix_icon=ft.Icons.PERSON_OUTLINE
    )
    
    clave_tf = ft.TextField(
        label="Contraseña", 
        password=True, 
        can_reveal_password=True, 
        border_color="#558B2F", 
        width=300,
        color="black",
        label_style=ft.TextStyle(color="#558B2F"),
        prefix_icon=ft.Icons.KEY_ROUNDED
    )

    def intentar_login(e):
        # A. Validación de campos vacíos
        if not usuario_tf.value or not clave_tf.value:
            txt_error.value = "Por favor, ingresa tu usuario y contraseña."
            dialogo_error.open = True
            page.update()
            return

        valor = usuario_tf.value
        payload = {
            "correo": None,
            "telefono": None,
            "contrasena": clave_tf.value
        }

        if "@" in valor:
            payload["correo"] = valor
        else:
            payload["telefono"] = valor

        try:
            res = requests.post("http://localhost:8000/login/", json=payload, timeout=5)
            
            if res.status_code == 200:
                datos = res.json()
                usuario_raw = datos.get('usuario')
                rol_final = datos.get('rol')
                id_usuario_final = datos.get('id_usuario')

                nombre_final = str(usuario_raw)
                ir_a_home(nombre_final, rol_final, id_usuario_final)
                
            else:
                # B. CAPTURA DE DATOS INCORRECTOS DESDE EL BACKEND
                error_det = res.json()
                # Mostramos el mensaje específico: "Datos incorrectos" o lo que envíe el servidor
                txt_error.value = error_det.get('detail', 'Usuario o contraseña incorrectos.')
                dialogo_error.open = True
        
        except Exception as ex:
            txt_error.value = "No se pudo conectar con el servidor. Verifica que el backend esté corriendo."
            dialogo_error.open = True
            
        page.update()

    # --- RETORNO DE LA VISTA (CENTRADO ABSOLUTO) ---
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER, # Centrado total
        bgcolor="#D1E8E4", # Tu color de fondo Pixar
        content=ft.Column(
            [
                ft.Icon(ft.Icons.LOCK_ROUNDED, color="#558B2F", size=60),
                ft.Text("Iniciar Sesión", size=32, weight="bold", color="#558B2F"),
                ft.Container(height=10),
                usuario_tf,
                clave_tf,
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Entrar", 
                    bgcolor="#9575CD", 
                    color="white", 
                    width=280, 
                    height=50,
                    on_click=intentar_login
                ),
                ft.TextButton("Volver al inicio", on_click=volver_bienvenida)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
    )