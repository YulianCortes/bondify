import flet as ft
import requests
import time

def obtener_perfil_view(page: ft.Page, volver_home, usuario_actual):
    if not usuario_actual:
        usuario_actual = {}

    id_usuario = usuario_actual.get("id_usuario", 0)

    # --- FUNCIÓN PARA CREAR CAMPOS ESTÉTICOS ---
    def crear_campo(label, value, width, multiline=False):
        return ft.TextField(
            label=label,
            value=str(value) if value else "",
            width=width,
            multiline=multiline,
            bgcolor="#FFFFFF",      # Fondo blanco limpio
            color="#2E312F",        # Texto gris muy oscuro (máxima legibilidad)
            border_color="#7EB7AD", # Verde suave de Bondify
            border_radius=12,
            focused_border_color="#3C7517", # Verde fuerte al escribir
            label_style=ft.TextStyle(color="#3C7517", weight="bold"),
            text_style=ft.TextStyle(size=16, weight="w500"),
            content_padding=15
        )

    campo_primer_nombre = crear_campo("Primer Nombre", usuario_actual.get("primer_nombre"), 145)
    campo_primer_apellido = crear_campo("Primer Apellido", usuario_actual.get("primer_apellido"), 145)
    campo_edad = crear_campo("Edad", usuario_actual.get("edad"), 100)
    
    campo_genero = ft.Dropdown(
        label="Género",
        width=190,
        bgcolor="#FFFFFF",
        value=usuario_actual.get("genero", ""),
        color="#2E312F",
        border_radius=12,
        border_color="#7EB7AD",
        label_style=ft.TextStyle(color="#3C7517", weight="bold"),
        options=[
            ft.dropdown.Option("Masculino"),
            ft.dropdown.Option("Femenino"),
            ft.dropdown.Option("Otro"),
        ]
    )

    campo_biografia = crear_campo("Sobre mí (Hobbies, gustos...)", usuario_actual.get("biografia"), 310, True)
    campo_disponibilidad = crear_campo("Mi Disponibilidad Semanal", usuario_actual.get("disponibilidad_semanal"), 310, True)

    def guardar_perfil(e):
        payload = {
            "primer_nombre": campo_primer_nombre.value,
            "primer_apellido": campo_primer_apellido.value,
            "edad": int(campo_edad.value) if campo_edad.value and campo_edad.value.isdigit() else None,
            "genero": campo_genero.value,
            "biografia": campo_biografia.value,
            "disponibilidad_semanal": campo_disponibilidad.value
        }
        
        try:
            res = requests.put(f"http://127.0.0.1:8000/usuarios/{id_usuario}/perfil", json=payload)
            
            if res.status_code == 200:
                # --- MENSAJE DE ÉXITO EN APP ---
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Perfil actualizado correctamente", color="white", weight="bold"),
                    bgcolor="#3C7517",
                    duration=2000
                )
                page.snack_bar.open = True
                page.update()
                
                # Pequeña pausa para que el usuario vea el check verde
                time.sleep(1)
                
                # VOLVER AL HOME: Enviamos el nuevo nombre (p_n) para que el saludo cambie
                volver_home(p_n=campo_primer_nombre.value)

            else:
                page.snack_bar = ft.SnackBar(ft.Text("Error al guardar cambios"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        except Exception as ex:
            print(f"Error: {ex}")

    # --- DISEÑO DE LA TARJETA ---
    tarjeta_blanca = ft.Container(
        bgcolor="white",
        padding=25,
        border_radius=25,
        shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK12),
        content=ft.Column([
            ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=80, color="#7EB7AD"),
            ft.Text(f"Rol: {usuario_actual.get('tipo_usuario', 'Jefe')}", color="grey", italic=True),
            ft.Divider(height=20, color="#F0F4F3"),
            
            ft.Row([campo_primer_nombre, campo_primer_apellido], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Row([campo_edad, campo_genero], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            campo_biografia,
            campo_disponibilidad,
            
            ft.Container(height=15),
            ft.ElevatedButton(
                "Guardar Cambios", 
                icon=ft.Icons.SAVE_ROUNDED, 
                bgcolor="#7EB7AD", 
                color="white",
                height=45,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                on_click=guardar_perfil
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=lambda e: volver_home(), icon_color="#7EB7AD", icon_size=20),
                ft.Text("Mi Perfil", size=24, weight="bold", color="#3C7517")
            ], alignment=ft.MainAxisAlignment.START),
            ft.Row([tarjeta_blanca], alignment=ft.MainAxisAlignment.CENTER)
        ], expand=True, scroll=ft.ScrollMode.AUTO),
        padding=20
    )