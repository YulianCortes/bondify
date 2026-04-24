import flet as ft
import sys
import os
import requests 

def obtener_actividades_view(page: ft.Page, volver_home, usuario_sesion):
    id_actual = usuario_sesion.get("id_usuario")
    es_jefe = usuario_sesion.get("tipo_usuario") == "Jefe"
    
    estado = {"id_familia": None, "miembros": []}

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

    lista_oficial = ft.Column(spacing=15, width=380)
    lista_disponibilidad = ft.Column(spacing=5)
    
    txt_jefe_titulo = ft.TextField(label="Título de la tarea", bgcolor="white", color="#212121", border_color="#3C7517")
    txt_jefe_desc = ft.TextField(label="Descripción", bgcolor="white", color="#212121", multiline=True, border_color="#3C7517")

    # --- FUNCIÓN: CALIFICACIÓN INDIVIDUAL (CHULITO ✅) ---
    def abrir_calificacion(actividad):
        # PRINT PARA DEPURAR (Míralo en tu terminal)
        print(f"SISTEMA: Intentando mostrar calificador para '{actividad['titulo']}'")
        
        participaciones = {}
        checkboxes_cont = ft.Column(spacing=10)

        for u in actividad["usuarios_asignados"]:
            u_id = str(u["id_usuario"])
            participaciones[u_id] = True # Por defecto decimos que sí cumplió
            
            def check_cambiado(e, uid=u_id):
                participaciones[uid] = e.control.value

            checkboxes_cont.controls.append(
                ft.Checkbox(
                    label=f"¿Cumplió {u['nombre']}?", 
                    value=True, 
                    on_change=check_cambiado, 
                    fill_color="#3C7517"
                )
            )

        def finalizar_y_cobrar(e):
            try:
                res = requests.put(
                    f"http://127.0.0.1:8000/actividades/{actividad['id_actividad']}/finalizar",
                    json=participaciones
                )
                if res.status_code == 200:
                    dialogo_nota.open = False
                    page.update()
                    page.snack_bar = ft.SnackBar(ft.Text("✅ Actividad finalizada. ¡Rachas individuales actualizadas!"), bgcolor="#3C7517")
                    page.snack_bar.open = True
                    cargar_todo()
                else:
                    print(f"ERROR: {res.text}")
            except: pass

        dialogo_nota = ft.AlertDialog(
            modal=True,
            title=ft.Text("Finalizar y Calificar"),
            content=ft.Column([
                ft.Text("Marca a los que cumplieron para darles +5 puntos. A los que no, se les restará -5.", size=12, italic=True),
                checkboxes_cont
            ], tight=True, width=300),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: [setattr(dialogo_nota, "open", False), page.update()]),
                ft.ElevatedButton("Cobrar Puntos 💰", bgcolor="#3C7517", color="white", on_click=finalizar_y_cobrar)
            ]
        )
        
        # EL TRUCO PARA QUE APAREZCA:
        page.dialog = dialogo_nota
        dialogo_nota.open = True
        page.update()

    # --- FUNCIÓN: ACTIVIDAD FALLIDA (BOTÓN X ❌) ---
    def marcar_actividad_fallida(actividad):
        # Penalizamos a todos los asignados y a la familia
        participaciones_fallidas = {str(u["id_usuario"]): False for u in actividad["usuarios_asignados"]}
        
        def confirmar_fallo(e):
            try:
                res = requests.put(
                    f"http://127.0.0.1:8000/actividades/{actividad['id_actividad']}/finalizar",
                    json=participaciones_fallidas
                )
                if res.status_code == 200:
                    dialogo_fallo.open = False
                    page.update()
                    page.snack_bar = ft.SnackBar(ft.Text("❌ Actividad fallida. Se restó racha a la familia."), bgcolor="orange")
                    page.snack_bar.open = True
                    cargar_todo()
            except: pass

        dialogo_fallo = ft.AlertDialog(
            title=ft.Text("¿Nadie hizo la tarea?"),
            content=ft.Text("Esto restará puntos individuales y bajará la racha de la mascota."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: [setattr(dialogo_fallo, "open", False), page.update()]),
                ft.ElevatedButton("Marcar Fallo", bgcolor="red", color="white", on_click=confirmar_fallo)
            ]
        )
        page.dialog = dialogo_fallo
        dialogo_fallo.open = True
        page.update()

    def cargar_todo():
        try:
            res_fam = requests.get(f"http://127.0.0.1:8000/familias/{id_actual}/integrantes")
            if res_fam.status_code == 200:
                datos_f = res_fam.json()
                estado["id_familia"] = datos_f.get("id_familia")
                estado["miembros"] = datos_f.get("integrantes", [])
                
                if estado["id_familia"]:
                    cargar_actividades_y_sugerencias(estado["id_familia"])
                    lista_disponibilidad.controls.clear()
                    for m in estado["miembros"]:
                        dispo = m.get('disponibilidad') or "Sin horario"
                        lista_disponibilidad.controls.append(
                            ft.Row([
                                ft.Icon(ft.Icons.PERSON_PIN_ROUNDED, color="#3C7517", size=20),
                                ft.Text(f"{m['nombre']}: ", color="#212121", weight="bold"),
                                ft.Text(dispo, color="#333333")
                            ])
                        )
            page.update()
        except: pass

    def toggle_asignacion(id_act, id_usu, marcado):
        try:
            if marcado:
                res = requests.put(f"http://127.0.0.1:8000/actividades/{id_act}/asignar/{id_usu}")
            else:
                res = requests.delete(f"http://127.0.0.1:8000/actividades/{id_act}/desasignar/{id_usu}")
            if res.status_code == 200:
                cargar_todo()
        except: pass

    def cargar_actividades_y_sugerencias(id_f):
        try:
            res = requests.get(f"http://127.0.0.1:8000/familias/{id_f}/actividades")
            if res.status_code == 200:
                tareas = res.json()
                lista_oficial.controls.clear()
                
                for a in tareas:
                    if a.get('es_sugerencia'): continue
                    asignados = a.get('usuarios_asignados', [])
                    ids_asignados = [u['id_usuario'] for u in asignados]
                    nombres_equipo = ", ".join([u['nombre'] for u in asignados]) or "Nadie asignado"

                    selector_equipo = ft.ExpansionTile(
                        title=ft.Text(f"Equipo: {nombres_equipo}", size=13, color="#3C7517", weight="bold"),
                        subtitle=ft.Text("Selecciona quiénes participan", size=11, color="#333333"),
                        maintain_state=True,
                        controls=[
                            ft.Checkbox(
                                label=m['nombre'],
                                value=(m['id_usuario'] in ids_asignados),
                                fill_color="#3C7517",
                                on_change=lambda e, id_a=a['id_actividad'], id_u=m['id_usuario']: 
                                    toggle_asignacion(id_a, id_u, e.control.value)
                            ) for m in estado["miembros"]
                        ]
                    ) if es_jefe else ft.Text(f"👥 Equipo: {nombres_equipo}", size=13, color="#3C7517", weight="bold")

                    card = ft.Container(
                        padding=20, bgcolor="white", border_radius=15, 
                        border=ft.border.all(2, "#3C7517" if ids_asignados else "#CCCCCC"),
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.GROUPS_ROUNDED, color="#3C7517", size=26),
                                ft.Text(a['titulo'], weight="bold", color="#212121", size=18, expand=True),
                                
                                # --- BOTONES DE ACCIÓN ---
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.Icons.CHECK_CIRCLE_ROUNDED, 
                                        icon_color="green",
                                        tooltip="Repartir puntos",
                                        on_click=lambda e, act=a: abrir_calificacion(act)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.CANCEL_ROUNDED, 
                                        icon_color="orange",
                                        tooltip="No realizada",
                                        on_click=lambda e, act=a: marcar_actividad_fallida(act)
                                    ),
                                    ft.IconButton(ft.Icons.DELETE_SWEEP_ROUNDED, icon_color="red", 
                                                  on_click=lambda e, id_a=a['id_actividad']: borrar_act_db(id_a))
                                ], visible=es_jefe)
                            ]),
                            ft.Text(a['descripcion'] or "Actividad familiar", color="#333333", size=15),
                            ft.Divider(height=20, color="#EEEEEE"),
                            selector_equipo
                        ])
                    )
                    lista_oficial.controls.append(card)
                page.update()
        except: pass

    def crear_tarea_jefe(e):
        if not txt_jefe_titulo.value or not estado["id_familia"]: return
        payload = {"titulo": txt_jefe_titulo.value, "descripcion": txt_jefe_desc.value,
                   "id_familia": int(estado["id_familia"]), "es_sugerencia": False}
        requests.post("http://127.0.0.1:8000/actividades/", json=payload)
        txt_jefe_titulo.value = ""; txt_jefe_desc.value = ""; cargar_todo()

    def asignar_catalogo(titulo, cat):
        if not estado["id_familia"]: return
        requests.post("http://127.0.0.1:8000/actividades/", json={
            "titulo": titulo, "descripcion": f"Categoría: {cat}", "id_familia": int(estado["id_familia"]), "es_sugerencia": False
        })
        cargar_todo()

    def borrar_act_db(id_act):
        requests.delete(f"http://127.0.0.1:8000/actividades/{id_act}")
        cargar_todo()

    panel_jefe = ft.Column([
        ft.Text("Control de Familia", size=22, weight="bold", color="#3C7517"),
        ft.Container(padding=15, bgcolor="#FFFFFF", border_radius=15, border=ft.border.all(1.5, "#3C7517"),
            content=ft.Column([ft.Text("Estado de Integrantes:", weight="bold", color="#212121"), lista_disponibilidad])),
        ft.Divider(height=10, color="transparent"),
        ft.Container(padding=20, bgcolor="#F1F8E9", border_radius=20,
            content=ft.Column([
                ft.Text("➕ Nueva Tarea", weight="bold", color="#3C7517", size=16),
                txt_jefe_titulo, txt_jefe_desc,
                ft.ElevatedButton("Publicar para la Familia", on_click=crear_tarea_jefe, bgcolor="#3C7517", color="white", width=400, height=45)
            ])),
        ft.ExpansionTile(
            title=ft.Text("Sugerencias Bondify", weight="bold", color="#212121"),
            subtitle=ft.Text("Ideas para fortalecer la unión", size=12, color="#333333"),
            controls=[
                ft.ListTile(
                    title=ft.Text(item['t'], size=14, color="#212121", weight="w500"),
                    subtitle=ft.Text(item['cat'], size=11, color="#3C7517"),
                    trailing=ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, icon_color="#3C7517", 
                                           on_click=lambda e, t=item['t'], c=item['cat']: asignar_catalogo(t, c)),
                ) for item in catalogo_items
            ]
        ),
    ]) if es_jefe else ft.Container()

    cargar_todo()

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=volver_home, icon_color="#3C7517", icon_size=20),
                    ft.Text("Actividades", size=26, weight="bold", color="#3C7517")]),
            ft.Divider(color="#3C7517", thickness=2),
            panel_jefe,
            ft.Text("Tareas en Curso", size=20, weight="bold", color="#3C7517"),
            lista_oficial,
            ft.Container(height=100) 
        ], scroll=ft.ScrollMode.ALWAYS, expand=True),
        padding=20, expand=True
    )