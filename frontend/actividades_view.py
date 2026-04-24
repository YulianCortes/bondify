import flet as ft
import requests

def obtener_actividades_view(page: ft.Page, volver_home, usuario_sesion):
    id_actual = usuario_sesion.get("id_usuario")
    es_jefe = usuario_sesion.get("tipo_usuario") == "Jefe"
    
    estado = {"id_familia": None}

    catalogo_items = [
        {"t": "Fútbol en el parque", "cat": "Física"}, {"t": "Caminata familiar", "cat": "Física"},
        {"t": "Yoga en casa", "cat": "Física"}, {"t": "Carrera de sacos", "cat": "Física"},
        {"t": "Baile grupal", "cat": "Física"}, {"t": "Noche de acertijos", "cat": "Mental"},
        {"t": "Torneo de ajedrez", "cat": "Mental"}, {"t": "Maratón de lectura", "cat": "Mental"},
        {"t": "Sudoku gigante", "cat": "Mental"}, {"t": "Juego de memoria", "cat": "Mental"},
        {"t": "Taller de dibujo", "cat": "Habilidad"}, {"t": "Cocinar postre", "cat": "Habilidad"},
        {"t": "Origami básico", "cat": "Habilidad"}, {"t": "Bricolaje simple", "cat": "Habilidad"},
        {"t": "Pintura con dedos", "cat": "Habilidad"}
    ]

    lista_oficial = ft.Column(spacing=10)
    lista_sugerencias = ft.Column(spacing=10)
    lista_disponibilidad = ft.Column(spacing=5)
    
    txt_jefe_titulo = ft.TextField(label="Título de la nueva tarea", bgcolor="white", color="black")
    txt_jefe_desc = ft.TextField(label="Descripción (opcional)", bgcolor="white", color="black", multiline=True)

    def cargar_todo():
        try:
            res_fam = requests.get(f"http://127.0.0.1:8000/familias/{id_actual}/integrantes")
            if res_fam.status_code == 200:
                datos_f = res_fam.json()
                estado["id_familia"] = datos_f.get("id_familia")
                
                if estado["id_familia"]:
                    cargar_actividades_y_sugerencias(estado["id_familia"])
                    if es_jefe:
                        lista_disponibilidad.controls.clear()
                        for m in datos_f['integrantes']:
                            # USAMOS disponibilidad_semanal QUE ES EL CAMPO REAL
                            dispo = m.get('disponibilidad_semanal') or "Sin horario definido"
                            lista_disponibilidad.controls.append(
                                ft.Row([
                                    ft.Icon(ft.Icons.PERSON, color="#3C7517", size=16),
                                    ft.Text(f"{m['nombre']}: {dispo}", color="black", size=14)
                                ])
                            )
                else:
                    lista_oficial.controls.clear()
                    lista_oficial.controls.append(ft.Text("⚠️ No tienes familia vinculada.", color="red", weight="bold"))
            page.update()
        except Exception as ex:
            print(f"[DEBUG] Error en cargar_todo: {ex}")

    def cargar_actividades_y_sugerencias(id_f):
        try:
            res = requests.get(f"http://127.0.0.1:8000/familias/{id_f}/actividades")
            if res.status_code == 200:
                lista_oficial.controls.clear()
                lista_sugerencias.controls.clear()
                for a in res.json():
                    card = ft.Container(
                        padding=15, bgcolor="white", border_radius=10, border=ft.border.all(1, "#DDDDDD"),
                        content=ft.Row([
                            ft.Icon(ft.Icons.STAR if not a['es_sugerencia'] else ft.Icons.LIGHTBULB, color="#3C7517", size=30),
                            ft.Column([ft.Text(a['titulo'], weight="bold", color="black", size=16),
                                       ft.Text(a['descripcion'] or "", color="#555555", size=13)], expand=True),
                            ft.IconButton(ft.Icons.DELETE_ROUNDED, icon_color="red", 
                                          on_click=lambda e, id_a=a['id_actividad']: borrar_act_db(id_a)) if es_jefe else ft.Container()
                        ])
                    )
                    if a['es_sugerencia']: lista_sugerencias.controls.append(card)
                    else: lista_oficial.controls.append(card)
            page.update()
        except: pass

    def crear_tarea_jefe(e):
        id_fam = estado["id_familia"]
        if id_fam is None:
            page.snack_bar = ft.SnackBar(ft.Text("❌ Error: No se detectó el ID de tu familia."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return
        if not txt_jefe_titulo.value: return

        payload = {"titulo": txt_jefe_titulo.value, "descripcion": txt_jefe_desc.value,
                   "id_familia": int(id_fam), "es_sugerencia": False}

        try:
            res = requests.post("http://127.0.0.1:8000/actividades/", json=payload)
            if res.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("✅ Tarea guardada con éxito"), bgcolor="green")
                page.snack_bar.open = True
                txt_jefe_titulo.value = ""; txt_jefe_desc.value = ""; cargar_todo()
            else:
                print(f"[DEBUG] Error del servidor: {res.text}")
        except Exception as ex:
            print(f"[DEBUG] Error de conexión: {ex}")

    def asignar_catalogo(titulo, categoria):
        id_fam = estado["id_familia"]
        if not id_fam: return
        try:
            payload = {"titulo": titulo, "descripcion": f"Categoría: {categoria}", "id_familia": int(id_fam), "es_sugerencia": False}
            res = requests.post("http://127.0.0.1:8000/actividades/", json=payload)
            if res.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text(f"✅ ¡{titulo} asignada!"), bgcolor="green")
                page.snack_bar.open = True
                cargar_todo()
        except: pass

    def enviar_sugerencia(e):
        id_fam = estado["id_familia"]
        txt_sug_titulo = ft.TextField() # Placeholder para evitar error si no existe
        if not id_fam: return
        requests.post("http://127.0.0.1:8000/actividades/", json={"titulo": "Sugerencia", "id_familia": id_fam, "es_sugerencia": True})
        cargar_todo()

    def borrar_act_db(id_act):
        try:
            requests.delete(f"http://127.0.0.1:8000/actividades/{id_act}")
            cargar_todo()
        except: pass

    panel_jefe = ft.Column([
        ft.Text("Panel de Control del Jefe", size=22, weight="bold", color="#3C7517"),
        ft.Container(padding=15, bgcolor="#FFFFFF", border_radius=15, border=ft.border.all(1, "#3C7517"),
            content=ft.Column([ft.Text("Disponibilidad Familiar:", weight="bold", color="black"), lista_disponibilidad])),
        ft.Divider(height=20, color="transparent"),
        ft.Container(padding=15, bgcolor="#E8F5E9", border_radius=15,
            content=ft.Column([
                ft.Text("➕ Crear Tarea Personalizada", weight="bold", color="#3C7517", size=16),
                txt_jefe_titulo, txt_jefe_desc,
                ft.ElevatedButton("Guardar Tarea", on_click=crear_tarea_jefe, bgcolor="#3C7517", color="white")
            ])),
        ft.Divider(height=20, color="transparent"),
        ft.ExpansionTile(
            title=ft.Text("Catálogo Bondify", weight="bold", color="black"),
            subtitle=ft.Text("Toca el (+) para programar", size=12, color="#666666"),
            bgcolor="#FFFFFF",
            controls=[
                ft.ListTile(
                    title=ft.Text(item['t'], size=14, color="black", weight="bold"),
                    subtitle=ft.Text(item['cat'], size=12, color="#3C7517"),
                    trailing=ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color="#3C7517", 
                                           on_click=lambda e, t=item['t'], c=item['cat']: asignar_catalogo(t, c)),
                ) for item in catalogo_items
            ]
        ),
        ft.Text("Sugerencias de la familia:", weight="bold", color="black", size=16),
        lista_sugerencias,
    ]) if es_jefe else ft.Container()

    cargar_todo()

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=volver_home, icon_color="#3C7517"),
                    ft.Text("Actividades", size=28, weight="bold", color="#3C7517")]),
            ft.Divider(color="#3C7517", thickness=2),
            panel_jefe,
            ft.Text("Actividades Programadas:", size=20, weight="bold", color="#3C7517"),
            lista_oficial,
            ft.Container(height=120) 
        ], scroll=ft.ScrollMode.ALWAYS, expand=True),
        padding=20, expand=True
    )