import flet as ft
import requests
import time

def obtener_gestion_familia_view(page: ft.Page, volver_home, usuario_sesion):
    id_actual = usuario_sesion.get("id_usuario")
    es_jefe = usuario_sesion.get("tipo_usuario") == "Jefe"
    
    # --- DICCIONARIO DE ESTADO (Cerebro de la vista) ---
    # Esto es lo que evita que el programa "explote" con errores de variables locales
    estado = {
        "id_familia": None
    }

    # --- CONTROLES ORIGINALES ---
    txt_nombre_familia = ft.TextField(label="Nombre de la Familia", width=250, color="black", bgcolor="white", border_color="#3C7517")
    txt_correo_miembro = ft.TextField(label="Correo del nuevo miembro", hint_text="ejemplo@correo.com", width=250, color="black", bgcolor="white", border_color="#3C7517")
    lista_miembros = ft.Column(spacing=12)
    titulo_familia = ft.Text("Mi Familia", size=28, weight="bold", color="#3C7517")

    # --- DIÁLOGO DE CONFIRMACIÓN ---
    def cerrar_dialogo(e):
        dialogo_confirmacion.open = False
        page.update()

    def abrir_confirmacion(e):
        # Sincronizamos el ID antes de abrir el diálogo
        id_fam = estado["id_familia"] or usuario_sesion.get("id_familia")
        estado["id_familia"] = id_fam 
        
        print(f"🔍 DEBUG: Abriendo diálogo para familia ID: {id_fam}")
        
        page.dialog = dialogo_confirmacion
        dialogo_confirmacion.open = True
        page.update()

    # --- FUNCIÓN MAESTRA: CARGAR DATOS ---
    def cargar_datos_familia():
        try:
            res = requests.get(f"http://127.0.0.1:8000/familias/{id_actual}/integrantes")
            if res.status_code == 200:
                datos = res.json()
                if datos.get("nombre_familia") and datos["nombre_familia"] != "N/A":
                    # Guardamos el ID en el estado y en la sesión global
                    estado["id_familia"] = datos.get("id_familia")
                    usuario_sesion["id_familia"] = estado["id_familia"]
                    
                    print(f"✅ FRONTEND: Familia cargada con ID: {estado['id_familia']}")
                    titulo_familia.value = f"Familia {datos['nombre_familia']}"
                    
                    lista_miembros.controls.clear()
                    for m in datos["integrantes"]:
                        # Solo el jefe ve el botón de eliminar miembros (y no se puede eliminar a sí mismo)
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
                    # Si no hay familia, preparamos la vista de creación
                    estado["id_familia"] = None
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
            print(f"❌ Error cargando familia: {ex}")

    # --- FUNCIÓN: DISOLVER (ELIMINACIÓN DEFINITIVA) ---
    def disolver_grupo_directo(e):
        print("🚨 BOTÓN 'SÍ, DISOLVER' PRESIONADO")
        dialogo_confirmacion.open = False
        page.update()
        
        id_fam = estado["id_familia"]
        if id_fam is None:
            print("🛑 ERROR: No se encontró ID de familia para borrar.")
            return

        try:
            url = f"http://127.0.0.1:8000/familias/disolver/{id_fam}?id_jefe={id_actual}"
            print(f"📡 ENVIANDO DELETE A: {url}")
            
            res = requests.delete(url)
            
            if res.status_code == 200:
                print("✨ ÉXITO: El servidor borró la familia de MySQL.")
                usuario_sesion["id_familia"] = None
                page.snack_bar = ft.SnackBar(ft.Text("✅ Grupo familiar disuelto correctamente."), bgcolor="#3C7517")
                page.snack_bar.open = True
                page.update()
                time.sleep(1)
                volver_home(None)
            else:
                print(f"⚠️ SERVIDOR DIJO NO: {res.status_code} - {res.text}")
        except Exception as ex:
            print(f"💥 FALLO DE CONEXIÓN: {ex}")

    # --- DEFINICIÓN DEL DIÁLOGO ---
    dialogo_confirmacion = ft.AlertDialog(
        modal=True,
        title=ft.Text("¿Disolver Familia?", color="#B71C1C", weight="bold"),
        content=ft.Text("Esta acción eliminará a todos los miembros y borrará el progreso de la mascota."),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo),
            ft.ElevatedButton("Sí, disolver", bgcolor="#B71C1C", color="white", on_click=disolver_grupo_directo),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # --- FUNCIONES DE BASE DE DATOS ---
    def crear_familia_db(e):
        if not txt_nombre_familia.value: return
        payload = {"nombre_familia": txt_nombre_familia.value, "id_jefe": id_actual}
        res = requests.post("http://127.0.0.1:8000/familias/", json=payload)
        if res.status_code == 200:
            usuario_sesion["id_familia"] = res.json().get("id_familia")
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

    # Carga inicial al entrar a la vista
    cargar_datos_familia()

    # --- RETORNO DE LA INTERFAZ ---
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=volver_home, icon_color="#3C7517", icon_size=20),
                titulo_familia
            ]),
            ft.Divider(color="#3C7517", thickness=1.5),
            ft.Text("Integrantes actuales:", size=18, weight="bold", color="#212121"),
            lista_miembros,
            
            # Botón de disolver (Solo para el Jefe)
            ft.Container(
                content=ft.ElevatedButton(
                    "Disolver Grupo Familiar", 
                    icon=ft.Icons.DELETE_FOREVER, 
                    bgcolor="#B71C1C", color="white",
                    on_click=abrir_confirmacion, 
                    width=400, height=45
                ),
                visible=es_jefe,
                padding=ft.padding.only(top=20)
            ) if es_jefe else ft.Container(),
            
            # Formulario para agregar miembros (Solo para el Jefe)
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