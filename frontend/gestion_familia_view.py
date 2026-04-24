import flet as ft
import requests
import time

def obtener_gestion_familia_view(page: ft.Page, volver_home, usuario_sesion):
    id_actual = usuario_sesion.get("id_usuario")
    es_jefe = usuario_sesion.get("tipo_usuario") == "Jefe"
    
    # --- LA CLAVE: EL "CAJÓN" ---
    # Usamos una lista [None] para que el ID se guarde aquí y todas 
    # las funciones internas puedan verlo sin que se pierda.
    id_familia_actual = [None] 

    # --- CAMPOS E INTERFAZ ---
    txt_nombre_familia = ft.TextField(label="Nombre de la Familia", width=250, color="black", bgcolor="white")
    txt_correo_miembro = ft.TextField(label="Correo del nuevo miembro", hint_text="usuario@correo.com", width=250, color="black", bgcolor="white")
    lista_miembros = ft.Column(spacing=10)
    titulo_familia = ft.Text("Mi Familia", size=28, weight="bold", color="#3C7517")

    # --- FUNCIÓN: DISOLVER GRUPO DIRECTO ---
    def disolver_grupo_directo(e):
        # Accedemos al valor dentro del cajón
        id_fam = id_familia_actual
        print(f"\n>>> DISOLVIENDO GRUPO DIRECTAMENTE. ID: {id_fam}")

        if id_fam is None:
            print("ERROR: No se encontró el ID de la familia (el cajón está vacío).")
            return

        try:
            url = f"http://127.0.0.1:8000/familias/disolver/{id_fam}?id_jefe={id_actual}"
            res = requests.delete(url)
            
            if res.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("✅ Grupo familiar disuelto correctamente"), bgcolor="#3C7517")
                page.snack_bar.open = True
                page.update()
                time.sleep(1)
                volver_home() 
            else:
                print(f"Error al borrar: {res.status_code}")
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {res.status_code}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
        except Exception as ex:
            print(f"Error conexión: {ex}")

    # --- FUNCIÓN: CARGAR DATOS ---
    def cargar_datos_familia():
        lista_miembros.controls.clear()
        try:
            res = requests.get(f"http://127.0.0.1:8000/familias/{id_actual}/integrantes")
            if res.status_code == 200:
                datos = res.json()
                print(f"DEBUG - Datos recibidos: {datos}")
                
                if datos["nombre_familia"] != "N/A":
                    # IMPORTANTE: Guardamos el ID dentro del cajón
                    id_familia_actual = datos.get("id_familia") 
                    titulo_familia.value = datos["nombre_familia"]
                    
                    for m in datos["integrantes"]:
                        # Solo el jefe ve el botón de borrar y no puede borrarse a sí mismo de la lista
                        btn_borrar = ft.IconButton(
                            ft.Icons.DELETE_OUTLINE, 
                            icon_color="red",
                            on_click=lambda e, id_m=m['id_usuario']: borrar_miembro_db(id_m)
                        ) if es_jefe and m['id_usuario'] != id_actual else ft.Container()

                        lista_miembros.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.PERSON_OUTLINE, color="#7EB7AD"),
                                    ft.Column([
                                        ft.Text(f"{m['nombre']} {m['primer_nombre'] if m['primer_nombre'] else ''}", weight="bold", color="black"),
                                        ft.Text(f"Rol: {m['rol']}", size=12, italic=True, color="grey"),
                                    ], expand=True),
                                    btn_borrar
                                ]),
                                bgcolor="#F0F4F3", padding=10, border_radius=10
                            )
                        )
                else:
                    titulo_familia.value = "Aún no tienes familia"
                    if es_jefe:
                        lista_miembros.controls.append(
                            ft.Column([
                                ft.Text("Como Jefe, puedes crear tu grupo familiar aquí:", color="black"),
                                txt_nombre_familia,
                                ft.ElevatedButton("Crear Familia", icon=ft.Icons.GROUP_ADD, on_click=crear_familia_db)
                            ])
                        )
            page.update()
        except Exception as ex:
            print(f"Error cargando familia: {ex}")

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
            cargar_datos_familia()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Usuario no encontrado o ya tiene familia"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def borrar_miembro_db(id_m):
        res = requests.delete(f"http://127.0.0.1:8000/familias/miembros/{id_m}?id_jefe={id_actual}")
        if res.status_code == 200:
            cargar_datos_familia()

    # Carga inicial para llenar la lista apenas entras
    cargar_datos_familia()

    # --- DISEÑO FINAL ---
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=volver_home, icon_color="#7EB7AD"),
                titulo_familia
            ]),
            ft.Divider(),
            ft.Text("Integrantes del grupo:", size=16, weight="bold", color="black"),
            lista_miembros,
            
            # Botón Disolver (Solo visible para el Jefe)
            ft.Container(
                content=ft.ElevatedButton(
                    "Disolver Grupo Familiar", 
                    icon=ft.Icons.DELETE_FOREVER, 
                    bgcolor="red", color="white",
                    on_click=disolver_grupo_directo 
                ),
                padding=ft.padding.only(top=10, bottom=10),
                visible=es_jefe
            ) if es_jefe else ft.Container(),
            
            # Sección Agregar Integrante (Solo para el Jefe)
            ft.Column([
                ft.Divider(),
                ft.Text("Agregar nuevo integrante:", size=16, weight="bold", color="black"),
                ft.Row([
                    txt_correo_miembro, 
                    ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=agregar_miembro_db, bgcolor="#7EB7AD")
                ])
            ]) if es_jefe else ft.Container()
        ], expand=True, scroll=ft.ScrollMode.AUTO),
        padding=20
    )