import flet as ft
import requests
import time

def obtener_gestion_familia_view(page: ft.Page, volver_home, usuario_sesion):
    id_actual = usuario_sesion.get("id_usuario")
    es_jefe = usuario_sesion.get("tipo_usuario") == "Jefe"
    
    # El cajón para el ID de la familia
    id_familia_actual = [None] 

    # --- CONTROLES ---
    txt_nombre_familia = ft.TextField(label="Nombre de la Familia", width=250, color="black", bgcolor="white", border_color="#3C7517")
    txt_correo_miembro = ft.TextField(label="Correo del nuevo miembro", hint_text="ejemplo@correo.com", width=250, color="black", bgcolor="white", border_color="#3C7517")
    lista_miembros = ft.Column(spacing=12)
    titulo_familia = ft.Text("Mi Familia", size=28, weight="bold", color="#3C7517")

    def cargar_datos_familia():
        try:
            res = requests.get(f"http://127.0.0.1:8000/familias/{id_actual}/integrantes")
            if res.status_code == 200:
                datos = res.json()
                # Si el backend no devuelve N/A, es porque hay familia
                if datos.get("nombre_familia") and datos["nombre_familia"] != "N/A":
                    # CORRECCIÓN: Guardamos dentro del cajón real
                    id_familia_actual = datos.get("id_familia") 
                    titulo_familia.value = f"Familia {datos['nombre_familia']}"
                    
                    lista_miembros.controls.clear()
                    for m in datos["integrantes"]:
                        # No se puede borrar al jefe a sí mismo
                        btn_borrar = ft.IconButton(
                            ft.Icons.PERSON_REMOVE_ALT_1, 
                            icon_color="red",
                            on_click=lambda e, id_m=m['id_usuario']: borrar_miembro_db(id_m)
                        ) if es_jefe and m['id_usuario'] != id_actual else ft.Container()

                        lista_miembros.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.PERSON_PIN_ROUNDED, color="#3C7517", size=30),
                                    ft.Column([
                                        # Texto más oscuro (#212121) para que se vea bien
                                        ft.Text(m['nombre'], weight="bold", color="#212121", size=16),
                                        ft.Text(f"Rol: {m['rol']}", size=12, italic=True, color="#444444"),
                                    ], expand=True),
                                    btn_borrar
                                ]),
                                bgcolor="#FFFFFF", 
                                padding=15, 
                                border_radius=12,
                                border=ft.border.all(1, "#3C7517")
                            )
                        )
                else:
                    titulo_familia.value = "Crea tu grupo familiar"
                    if es_jefe:
                        lista_miembros.controls.clear()
                        lista_miembros.controls.append(
                            ft.Column([
                                ft.Text("Como Jefe, ponle un nombre a tu grupo:", color="#212121", size=16),
                                txt_nombre_familia,
                                ft.ElevatedButton("Crear Grupo", icon=ft.Icons.GROUP_ADD, on_click=crear_familia_db, bgcolor="#3C7517", color="white")
                            ], spacing=15)
                        )
            page.update()
        except Exception as ex:
            print(f"Error cargando familia: {ex}")

    def disolver_grupo_directo(e):
        # CORRECCIÓN: Sacamos el ID del cajón
        id_fam = id_familia_actual 
        if id_fam is None:
            return

        try:
            # La URL debe ser exacta a la del backend
            url = f"http://127.0.0.1:8000/familias/disolver/{id_fam}?id_jefe={id_actual}"
            res = requests.delete(url)
            if res.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("✅ Grupo disuelto. Volviendo al inicio..."), bgcolor="#3C7517")
                page.snack_bar.open = True
                page.update()
                time.sleep(1.5)
                volver_home(None)
        except Exception as ex:
            print(f"Error disolver: {ex}")

    def crear_familia_db(e):
        if not txt_nombre_familia.value: return
        payload = {"nombre_familia": txt_nombre_familia.value, "id_jefe": id_actual}
        res = requests.post("http://127.0.0.1:8000/familias/", json=payload)
        if res.status_code == 200:
            cargar_datos_familia()

    def agregar_miembro_db(e):
        if not txt_correo_miembro.value: return
        res = requests.post(f"http://127.0.0.1:8000/familias/miembros/?correo={txt_correo_miembro.value}&id_jefe={id_actual}")
        if res.status_code == 200:
            txt_correo_miembro.value = ""
            page.snack_bar = ft.SnackBar(ft.Text("✅ Miembro añadido"), bgcolor="#3C7517")
            page.snack_bar.open = True
            cargar_datos_familia()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("❌ Usuario no encontrado o ya tiene grupo"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def borrar_miembro_db(id_m):
        res = requests.delete(f"http://127.0.0.1:8000/familias/miembros/{id_m}?id_jefe={id_actual}")
        if res.status_code == 200:
            cargar_datos_familia()

    # Carga automática al entrar
    cargar_datos_familia()

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=volver_home, icon_color="#3C7517", icon_size=20),
                titulo_familia
            ]),
            ft.Divider(color="#3C7517", thickness=1.5),
            
            ft.Text("Integrantes actuales:", size=18, weight="bold", color="#212121"),
            lista_miembros,
            
            # Botón Disolver (Solo Jefe)
            ft.Container(
                content=ft.ElevatedButton(
                    "Disolver Grupo Familiar", 
                    icon=ft.Icons.DELETE_FOREVER, 
                    bgcolor="#B71C1C", color="white",
                    on_click=disolver_grupo_directo,
                    width=400, height=45
                ),
                visible=es_jefe,
                padding=ft.padding.only(top=20)
            ) if es_jefe else ft.Container(),
            
            # Sección Agregar (Solo Jefe)
            ft.Column([
                ft.Divider(height=40),
                ft.Text("Agregar por correo:", size=18, weight="bold", color="#212121"),
                ft.Row([
                    txt_correo_miembro, 
                    ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=agregar_miembro_db, bgcolor="#3C7517")
                ])
            ], visible=es_jefe) if es_jefe else ft.Container()
            
        ], expand=True, scroll=ft.ScrollMode.AUTO),
        padding=20
    )