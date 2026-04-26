import flet as ft

def obtener_configuracion_view(page: ft.Page, volver_home, ir_a_bienvenida, usuario_sesion):
    # --- CONFIGURACIÓN Y ESTADO ---
    nombre_usuario = usuario_sesion.get("nombre") or "Usuario"
    rol_usuario = usuario_sesion.get("tipo_usuario") or "Miembro"

    # --- FUNCIÓN: LOGOUT (CERRAR SESIÓN) ---
    def ejecutar_logout(e):
        # 1. Limpiamos los datos de la sesión centralizada
        usuario_sesion["nombre"] = None
        usuario_sesion["id_usuario"] = None
        usuario_sesion["tipo_usuario"] = None
        usuario_sesion["id_familia"] = None
        
        # 2. Navegamos a la pantalla de bienvenida
        ir_a_bienvenida(None)

    # --- UI: SECCIONES DE CONFIGURACIÓN ---
    def crear_item_config(icono, titulo, subtitulo=None):
        color_tema = "#3C7517"
        return ft.Container(
            padding=15,
            border_radius=10,
            bgcolor="white",
            border=ft.border.all(1, "#E0E0E0"),
            content=ft.Row([
                ft.Icon(icono, color=color_tema),
                ft.Column([
                    ft.Text(titulo, weight="bold", color=color_tema, size=14),
                    ft.Text(subtitulo, size=12, color="#757575") if subtitulo else ft.Container()
                ], spacing=0, expand=True),
                ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=15, color="#BDBDBD")
            ])
        )

    # --- RETORNO DE LA VISTA ---
    return ft.Container(
        padding=20, expand=True,
        content=ft.Column([
            # Cabecera
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=volver_home, icon_color="#3C7517"),
                ft.Text("Configuración", size=26, weight="bold", color="#3C7517")
            ]),
            ft.Divider(color="#3C7517", thickness=1),
            
            # --- Info de Cuenta ---
            ft.Text("Mi Cuenta", weight="bold", size=16, color="#3C7517"),
            ft.Container(
                padding=15, bgcolor="#F1F8E9", border_radius=15, border=ft.border.all(1, "#A5D6A7"),
                content=ft.Row([
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=50, color="#3C7517"), 
                    ft.Column([
                        ft.Text(nombre_usuario, weight="bold", size=16, color="#212121"), 
                        ft.Text(f"Rol: {rol_usuario}", size=13, italic=True, color="#5D4037") 
                    ], spacing=2, expand=True) 
                ])
            ),
            
            ft.Divider(height=10, color="transparent"),
            
            # --- Ajustes Generales (CIRUGÍA AQUÍ) ---
            crear_item_config(ft.Icons.MANAGE_ACCOUNTS, "Actualizar Datos", "Contraseña, correo, número y nombre"),
            crear_item_config(ft.Icons.NOTIFICATIONS_OUTLINED, "Notificaciones", "Gestiona tus alertas"),
            crear_item_config(ft.Icons.HELP_OUTLINE, "Centro de Ayuda", "Preguntas y soporte"),
            
            ft.Container(expand=True), # Empuja el botón de cerrar sesión hacia abajo
            
            # BOTÓN CERRAR SESIÓN
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.LOGOUT, color="white"),
                    ft.Text("Cerrar Sesión", size=16, weight="bold", color="white") 
                ], alignment="center"),
                style=ft.ButtonStyle(
                    color="white",
                    bgcolor="#B71C1C",
                    shape=ft.RoundedRectangleBorder(radius=12),
                ),
                height=50,
                width=float("inf"),
                on_click=ejecutar_logout
            ),
            ft.Text("Bondify v1.0 - Hecho con ❤️ para la familia", size=10, color="#BDBDBD", text_align="center", width=float("inf"))
        ])
    )