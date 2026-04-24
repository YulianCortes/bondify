import flet as ft

def obtener_home_view(page, nombre, rol, ir_a_bienvenida, ir_a_familia, ir_a_actividades, ir_a_calendario, ir_a_perfil, ir_a_mis_actividades, ir_a_configuracion, ir_a_gestion_familia, primer_nombre=None):
    
    # --- LÓGICA DE NOMBRE DINÁMICO ---
    # Si el usuario ya llenó su perfil, usamos su primer nombre. Si no, usamos "Usuario".
    nombre_a_mostrar = primer_nombre if primer_nombre and primer_nombre.strip() != "" else "Usuario"

    # --- FUNCIONES DE CONTROL ---
    def cerrar_menu(e):
        capa_overlay_menu.visible = False
        page.update()

    def abrir_menu(e):
        capa_overlay_menu.visible = True
        page.update()

    def clic_perfil(e):
        cerrar_menu(None)
        ir_a_perfil(e)

    def clic_configuracion(e):
        cerrar_menu(None)
        ir_a_configuracion(e)

    # --- 1. LA TARJETA DEL MENÚ ---
    cuadro_menu = ft.Container(
        width=280, # Aumentamos un poco el ancho para el texto más grande
        bgcolor="#F4EAE0",
        border_radius=15,
        padding=15,
        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK26),
        on_click=lambda _: None, 
        content=ft.Column([
            ft.Row([
                # ZONA DE PERFIL
                ft.Container(
                    on_click=clic_perfil,
                    border_radius=10,
                    expand=True, 
                    content=ft.Row([
                        ft.CircleAvatar(
                            content=ft.Icon(ft.Icons.PERSON, color="#5D4037"),
                            bgcolor="#D7CCC8",
                            radius=25
                        ),
                        ft.Column([
                            ft.Row([
                                ft.Text(
                                    nombre_a_mostrar, 
                                    size=22, # Texto más grande y visible
                                    weight="bold", 
                                    color="#864430", 
                                    italic=True, 
                                    overflow=ft.TextOverflow.ELLIPSIS
                                ),
                                ft.Icon(ft.Icons.EDIT, size=18, color="#864430"), 
                            ], spacing=5),
                        ], spacing=0),
                    ], spacing=10)
                ),
                
                ft.IconButton(
                    icon=ft.Icons.CLOSE, 
                    icon_size=20, 
                    icon_color="#864430", 
                    on_click=cerrar_menu
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),

            ft.Container(height=15), 

            # OPCIÓN: CONFIGURACIÓN
            ft.Container(
                on_click=clic_configuracion,
                padding=10, border_radius=10,
                content=ft.Row([
                    ft.Icon(ft.Icons.SETTINGS, color="#5D4037", size=24), 
                    ft.Text("Configuración", color="#5D4037", size=18, weight="w500")
                ], spacing=15)
            ),

            # OPCIÓN: MI FAMILIA (Gestión)
            ft.Container(
                on_click=lambda e: [cerrar_menu(None), ir_a_gestion_familia(e)],
                padding=10, border_radius=10,
                content=ft.Row([
                    ft.Icon(ft.Icons.GROUP, color="#5D4037", size=24), 
                    ft.Text("mi familia", color="#5D4037", size=18, weight="w500")
                ], spacing=15)
            ),

            # OPCIÓN: MIS ACTIVIDADES
            ft.Container(
                on_click=lambda e: [cerrar_menu(None), ir_a_mis_actividades(e)],
                padding=10, border_radius=10,
                content=ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_TODAY, color="#5D4037", size=24), 
                    ft.Text("mis actividades", color="#5D4037", size=18, weight="w500")
                ], spacing=15)
            ),
        ], spacing=10)
    )

    # --- 2. CAPA OSCURA DE FONDO ---
    capa_overlay_menu = ft.Container(
        content=cuadro_menu,
        alignment=ft.Alignment(-0.85, -0.85),
        bgcolor="#99000000",
        visible=False,
        expand=True,
        top=0, left=0, right=0, bottom=0,
        on_click=cerrar_menu 
    )

    # --- 3. CONTENIDO PRINCIPAL DEL HOME ---
    contenido_home = ft.Column(
        [
            ft.Container(
                height=60, 
                padding=ft.padding.only(left=10, top=10), 
                content=ft.Row([
                    ft.Container(
                        content=ft.Image(src="menu_icono.png", width=35, height=35),
                        on_click=abrir_menu,
                        padding=5,
                    ),
                    ft.Text("Bondify", size=22, weight="bold", color="#864430")
                ])
            ),
            
            ft.Container(height=80), 
            
            ft.Text(
                f"¡Bienvenido,\n{nombre_a_mostrar}!", 
                size=36, # Aumentamos el tamaño del saludo principal
                weight="bold", 
                color="#558B2F", 
                text_align="center"
            ),
            
            ft.Container(expand=True), 
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )

    return ft.Stack([
        contenido_home,
        capa_overlay_menu
    ], expand=True)