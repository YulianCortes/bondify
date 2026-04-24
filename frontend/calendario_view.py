import flet as ft

def obtener_calendario_view(page, volver_home):
    return ft.Column(
        [
            # Barra superior
            ft.Container(
                height=60,
                content=ft.Row([
                    ft.Container(content=ft.Image(src="volver.png", width=30, height=30), on_click=volver_home, padding=10),
                    ft.Text("Mi Calendario", size=22, weight="bold", color="#558B2F")
                ]),
                bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
            ),
            
            ft.Container(height=20),
            ft.Text("PROXIMAMENTEEE", size=24, weight="bold", color="#558B2F"),
            
            # Placeholder para el calendario
            ft.Container(
                content=ft.Text("pROXIMO", size=18, color="grey"),
                alignment="center",
                padding=50
            ),
            
            ft.Container(expand=True)
        ],
        expand=True
    )