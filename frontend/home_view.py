import flet as ft

def obtener_home_view(page, nombre, rol, ir_a_bienvenida):
    
    # Esta es tu lógica original de cambios de tab
    def cambiar_tab(e):
        print(f"Cambiando a: {e.control.data}")

    # --- MENÚ (Estructura simple sin iconos de Flet para evitar errores) ---
    def cerrar_menu(e):
        menu_emergente.open = False
        page.update()

    def abrir_menu(e):
        page.dialog = menu_emergente
        menu_emergente.open = True
        page.update()

    menu_emergente = ft.AlertDialog(
        content=ft.Container(
            content=ft.Stack([
                ft.Image(src="menu_desplegado.png", width=280),
                # Botón invisible para cerrar, posicionado donde está la "X"
                ft.Container(width=40, height=40, left=220, top=10, on_click=cerrar_menu),
            ]),
            width=280, height=400,
        ),
        bgcolor="transparent",
        content_padding=0,
    )
    # ------------------------------------------------------------------------

    # Esta es tu barra inferior original que SÍ funcionaba
    barra_inferior = ft.Container(
        content=ft.Row(
            [
                ft.Container(content=ft.Image(src="home.png", width=40, height=40), on_click=cambiar_tab, data="home", padding=10),
                ft.Container(content=ft.Image(src="plant.png", width=40, height=40), on_click=cambiar_tab, data="activities", padding=10),
                ft.Container(content=ft.Image(src="calendar.png", width=40, height=40), on_click=cambiar_tab, data="calendar", padding=10),
                ft.Container(content=ft.Image(src="family.png", width=40, height=40), on_click=cambiar_tab, data="family", padding=10),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        ),
        bgcolor="#E1BEE7",
        height=80,
        width=float('inf'),
        padding=0, margin=0,
    )

    page.bgcolor = "#D1E8E4"
    page.padding = 0
    page.spacing = 0

    # Este es tu retorno original que SÍ funcionaba al 100%
    return ft.Column(
        [
            ft.Container(height=50, content=ft.Row([
                # Tu botón de menú original
                ft.Container(content=ft.Image(src="menu_icono.png", width=30, height=30), on_click=abrir_menu, padding=10),
                ft.Text("Bondify", size=20, weight="bold")
            ])),
            ft.Text("¡Buenos días, bienvenid@ a Bondify!", size=28, weight="bold", color="#558B2F", text_align="center"),
            ft.Container(expand=True),
            ft.Container(content=barra_inferior, width=float('inf'), padding=0, margin=0)
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0, expand=True
    )