import flet as ft
import requests

def obtener_login_view(page, volver_bienvenida, ir_a_home):
    # Campos de entrada
    usuario_tf = ft.TextField(
        label="Correo o Teléfono", 
        border_color="#558B2F", 
        width=300,
        color="black",
        label_style=ft.TextStyle(color="#558B2F"),
    )
    
    clave_tf = ft.TextField(
        label="Contraseña", 
        password=True, 
        can_reveal_password=True, 
        border_color="#558B2F", 
        width=300,
        color="black",
        label_style=ft.TextStyle(color="#558B2F"),
    )

    def intentar_login(e):
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

        print(f"Intentando conectar con: {payload}")
        
        try:
            res = requests.post("http://localhost:8000/login/", json=payload, timeout=5)
            
            if res.status_code == 200:
                datos = res.json()
                
                # --- LA FORMA MÁS SEGURA ---
                usuario_raw = datos.get('usuario')
                
                # Si es una lista, convertimos a string directamente antes de enviar
                if isinstance(usuario_raw, list):
                    # Esto convierte ["Yulian", "Esteban"] a "Yulian" directamente
                    nombre_final = str(usuario_raw)
                else:
                    nombre_final = str(usuario_raw)
                
                print(f"DEBUG: Enviando a home: {nombre_final}")
                ir_a_home(nombre_final, datos.get('rol'))
                
            else:
                error_det = res.json()
                print(f"Error del servidor: {error_det}")
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {error_det.get('detail', 'Ocurrió un error')}"))
                page.snack_bar.open = True
        
        except Exception as ex:
            print(f"Ocurrió un error inesperado: {ex}")
            page.snack_bar = ft.SnackBar(ft.Text("Error de conexión con el servidor"))
            page.snack_bar.open = True
            
        page.update()

    return ft.Column(
        [
            ft.Text("Iniciar Sesión", size=28, weight="bold", color="#558B2F"),
            ft.Container(height=20),
            usuario_tf,
            clave_tf,
            ft.Container(height=20),
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
        horizontal_alignment="center"
    )