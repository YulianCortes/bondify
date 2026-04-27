import flet as ft
import requests
import time

def obtener_gestion_familia_view(page: ft.Page, volver_home, usuario_sesion):
    id_actual = usuario_sesion.get("id_usuario")
    es_jefe = usuario_sesion.get("tipo_usuario") == "Jefe"
    
    # --- DICCIONARIO DE ESTADO ---
    estado = {
        "id_familia": usuario_sesion.get("id_familia")
    }

    # --- CONTROLES ---
    txt_nombre_familia = ft.TextField(label="Nombre de la Familia", width=250, color="black", bgcolor="white", border_color="#3C7517")
    txt_correo_miembro = ft.TextField(label="Correo del nuevo miembro", hint_text="ejemplo@correo.com", width=250, color="black", bgcolor="white", border_color="#3C7517")
    lista_miembros = ft.Column(spacing=12)
    
    # MEJORA 1: Definimos el texto del título
    titulo_familia = ft.Text("Mi Familia", size=26, weight="bold", color="#3C7517")

    def cerrar_dialogo(e):
        dialogo_confirmacion.open = False
        page.update()

    def abrir_confirmacion(e):
        id_fam = estado["id_familia"] or usuario_sesion.get("id_familia")
        estado["id_familia"] = id_fam 
        if dialogo_confirmacion not in page.overlay:
            page.overlay.append(dialogo_confirmacion)
        dialogo_confirmacion.open = True
        page.update()

    # --- FUNCIÓN MAESTRA: CARGAR DATOS ---
    def cargar_datos_familia():
        try:
            res = requests.get(f"http://127.0.0.1:8000/familias/{id_actual}/integrantes")
            if res.status_code == 200:
                datos = res.json()
                if datos.get("id_familia"):
                    estado["id_familia"] = datos.get("id_familia")
                    usuario_sesion["id_familia"] = estado["id_familia"]
                    titulo_familia.value = f"Familia {datos['nombre_familia']}"
                    
                    lista_miembros.controls.clear()
                    for m in datos["integrantes"]:
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
                                        ft.Text(m['nombre'], weight="bold", color="#212121", size=16),
                                        ft.Text(f"Rol: {m['rol']}", size=12, italic=True, color="#444444"),
                                    ], expand=True),
                                    btn_borrar
                                ]),
                                bgcolor="#FFFFFF", padding=15, border_radius=12, border=ft.border.all(1, "#3C7517")
                            )
                        )
                else:
                    # MEJORA 2: Si no hay familia, refrescamos la UI de inmediato
                    estado["id_familia"] = None
                    usuario_sesion["id_familia"] = None
                    titulo_familia.value = "Crea tu grupo"
                    if es_jefe:
                        lista_miembros.controls.clear()
                        lista_miembros.controls.append(
                            ft.Column([
                                ft.Text("No tienes una familia activa:", color="#212121", size=16),
                                txt_nombre_familia,
                                ft.ElevatedButton("Crear Grupo", icon=ft.Icons.GROUP_ADD, on_click=crear_familia_db, bgcolor="#3C7517", color="white")
                            ], spacing=15)
                        )
            page.update()
        except Exception as ex:
            print(f"❌ Error cargando familia: {ex}")

    def disolver_grupo_directo(e):
        dialogo_confirmacion.open = False
        page.update()
        id_fam = estado["id_familia"] or usuario_sesion.get("id_familia")
        if id_fam is None: return

        try:
            url = f"http://127.0.0.1:8000/familias/disolver/{id_fam}?id_jefe={id_actual}"
            res = requests.delete(url)
            if res.status_code == 200:
                # MEJORA 3: Limpiamos y recargamos la vista sin salir de ella
                usuario_sesion["id_familia"] = None
                estado["id_familia"] = None
                page.snack_bar = ft.SnackBar(ft.Text("✅ Familia disuelta correctamente."), bgcolor="#3C7517")
                page.snack_bar.open = True
                cargar_datos_familia() # <-- Esto hace que aparezca el botón de Crear al instante
            else:
                print(f"⚠️ Error: {res.text}")
        except Exception as ex:
            print(f"💥 Error: {ex}")

    # --- MEJORA 4: DIÁLOGO ESTÉTICO (SIN CUADRO NEGRO) ---
    dialogo_confirmacion = ft.AlertDialog(
        modal=True,
        bgcolor="#F1F8E9", # Fondo verde clarito
        shape=ft.RoundedRectangleBorder(radius=20), # Bordes redondeados
        title=ft.Row([
            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color="#B71C1C", size=30),
            ft.Text("¿BORRAR TODO?", color="#B71C1C", weight="bold")
        ], alignment=ft.MainAxisAlignment.CENTER),
        content=ft.Text(
            "Esta acción borrará mensajes, tareas y el progreso del cerezo.\n¿Estás seguro?",
            text_align=ft.TextAlign.CENTER,
            color="#444444"
        ),
        actions=[
            ft.TextButton("No, cancelar", on_click=cerrar_dialogo),
            ft.ElevatedButton("SÍ, DISOLVER", bgcolor="#B71C1C", color="white", on_click=disolver_grupo_directo),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def crear_familia_db(e):
        if not txt_nombre_familia.value: return
        res = requests.post("http://127.0.0.1:8000/familias/", json={"nombre_familia": txt_nombre_familia.value, "id_jefe": id_actual})
        if res.status_code == 200:
            datos = res.json()
            usuario_sesion["id_familia"] = datos.get("id_familia")
            estado["id_familia"] = datos.get("id_familia")
            cargar_datos_familia()

    def agregar_miembro_db(e):
        if not txt_correo_miembro.value: return
        res = requests.post(f"http://127.0.0.1:8000/familias/miembros/?correo={txt_correo_miembro.value}&id_jefe={id_actual}")
        if res.status_code == 200:
            txt_correo_miembro.value = ""
            page.snack_bar = ft.SnackBar(ft.Text("✅ Miembro añadido"), bgcolor="#3C7517")
            page.snack_bar.open = True
            cargar_datos_familia()

    def borrar_miembro_db(id_m):
        res = requests.delete(f"http://127.0.0.1:8000/familias/miembros/{id_m}?id_jefe={id_actual}")
        if res.status_code == 200:
            cargar_datos_familia()

    cargar_datos_familia()

    return ft.Container(
        expand=True,
        bgcolor="#F1F8E9",
        padding=20,
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=volver_home, icon_color="#3C7517", icon_size=20),
                # MEJORA 5: Columna con expand=True para que el nombre no se recorte
                ft.Column([titulo_familia], expand=True) 
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(color="#3C7517", thickness=1.5),
            ft.Text("Integrantes actuales:", size=18, weight="bold", color="#212121"),
            lista_miembros,
            
            ft.Container(
                content=ft.ElevatedButton(
                    "Disolver Grupo Familiar", 
                    icon=ft.Icons.DELETE_FOREVER, 
                    bgcolor="#B71C1C", color="white",
                    on_click=abrir_confirmacion, 
                    width=400, height=45
                ),
                visible=es_jefe and estado["id_familia"] is not None,
                padding=ft.padding.only(top=20)
            ) if es_jefe else ft.Container(),
            
            ft.Column([
                ft.Divider(height=40, color="transparent"),
                ft.Text("Agregar por correo:", size=18, weight="bold", color="#212121"),
                ft.Row([
                    txt_correo_miembro, 
                    ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=agregar_miembro_db, bgcolor="#3C7517")
                ])
            ], visible=es_jefe and estado["id_familia"] is not None) if es_jefe else ft.Container()
        ], expand=True, scroll=ft.ScrollMode.AUTO)
    )