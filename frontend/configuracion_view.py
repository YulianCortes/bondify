import flet as ft

def obtener_configuracion_view(page, ir_a_home):
    return ft.Column([
        ft.Container(
            padding=20,
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=ir_a_home),
                ft.Text("Configuración", size=24, weight="bold", color="#5D4037")
            ])
        ),
        ft.Column([
            ft.ListTile(leading=ft.Icon(ft.Icons.NOTIFICATIONS), title=ft.Text("Notificaciones")),
            ft.ListTile(leading=ft.Icon(ft.Icons.LOCK), title=ft.Text("Seguridad")),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOGOUT, color="red"), 
                title=ft.Text("Cerrar Sesión", color="red")
            ),
        ], spacing=10)
    ], expand=True)