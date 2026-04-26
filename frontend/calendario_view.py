import flet as ft
import datetime
import calendar
import requests

def obtener_calendario_view(page: ft.Page, volver_home, usuario_sesion):
    # --- 1. CONFIGURACIÓN INICIAL ---
    id_usuario_actual = usuario_sesion.get("id_usuario")
    hoy = datetime.date.today() 
    mes_actual, anio_actual = hoy.month, hoy.year
    
    meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    grid_calendario = ft.GridView(runs_count=7, spacing=5, run_spacing=5, child_aspect_ratio=1.0)
    lista_detalles = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS, height=180) # Un poco más alto
    
    # --- PARSEADOR BLINDADO ---
    def parsear_fecha_completa(fecha_obj):
        if not fecha_obj: return 0, 0, 0
        try:
            if isinstance(fecha_obj, list) and len(fecha_obj) >= 3:
                return int(fecha_obj), int(fecha_obj), int(fecha_obj)
            
            f_texto = str(fecha_obj).strip().replace("[", "").replace("]", "").replace(" ", "")
            if "T" in f_texto: f_texto = f_texto.split("T")

            for formato in ("%Y-%m-%d", "%Y,%m,%d"):
                try:
                    dt = datetime.datetime.strptime(f_texto, formato)
                    return dt.year, dt.month, dt.day
                except: continue
            
            partes = f_texto.replace(",", "-").split("-")
            if len(partes) >= 3:
                return int(partes), int(partes), int(partes)
        except: pass
        return 0, 0, 0

    # --- 2. CARGAR ACTIVIDADES ---
    def cargar_actividades_mes():
        id_fam = usuario_sesion.get("id_familia")
        if not id_fam: return {}
        try:
            res = requests.get(f"http://127.0.0.1:8000/familias/{id_fam}/actividades", timeout=5)
            if res.status_code == 200:
                mapa = {}
                for t in res.json():
                    if t.get('es_sugerencia') or not t.get("fecha"): continue
                    a_t, m_t, d_t = parsear_fecha_completa(t["fecha"])
                    if a_t == anio_actual and m_t == mes_actual and d_t > 0:
                        ids_asig = [str(u.get('id_usuario')) for u in t.get('usuarios_asignados', []) if isinstance(u, dict)]
                        if str(id_usuario_actual) in ids_asig:
                            if d_t not in mapa: mapa[d_t] = []
                            mapa[d_t].append(t)
                return mapa
        except: return {}
        return {}

    # --- 3. SELECCIONAR DÍA (Aquí quitamos el cuadro gris) ---
    def seleccionar_dia(dia, tareas_dia):
        lista_detalles.controls.clear()
        if not tareas_dia:
            lista_detalles.controls.append(
                ft.Text(f"No hay actividades para el {dia}.", italic=True, color="#5D4037")
            )
        else:
            for t in tareas_dia:
                asignados = t.get('usuarios_asignados', [])
                nombres = ", ".join([u['nombre'] for u in asignados if isinstance(u, dict)])
                
                # CREAMOS LA TARJETA SIN "SOFT_WRAP" PARA EVITAR EL CRASH
                lista_detalles.controls.append(
                    ft.Container(
                        padding=15, 
                        bgcolor="white", 
                        border_radius=15, 
                        border=ft.border.all(1.5, "#3C7517"),
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color="#3C7517", size=30),
                            ft.Column([
                                ft.Text(t['titulo'], weight="bold", size=18, color="#212121"),
                                # Usamos expand=True en el Column para que el texto sepa dónde frenar
                                ft.Text(t['descripcion'] or "Actividad familiar", size=14, color="#444444"),
                                ft.Row([
                                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=16, color="#3C7517"),
                                    ft.Text(f"Equipo: {nombres}", size=12, color="#3C7517", weight="w500", italic=True)
                                ], spacing=5, wrap=True) # wrap=True arregla el recorte de nombres
                            ], spacing=4, expand=True)
                        ], vertical_alignment=ft.CrossAxisAlignment.START)
                    )
                )
        page.update()

    def construir_interfaz():
        grid_calendario.controls.clear()
        mapa = cargar_actividades_mes()
        dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]
        for d in dias_semana:
            grid_calendario.controls.append(
                ft.Container(content=ft.Text(d, weight="bold", color="#3C7517"), alignment=ft.Alignment.CENTER)
            )

        cal = calendar.Calendar(firstweekday=0)
        for semana in cal.monthdayscalendar(anio_actual, mes_actual):
            for dia in semana:
                if dia == 0:
                    grid_calendario.controls.append(ft.Container())
                else:
                    es_hoy = (dia == hoy.day)
                    tareas = mapa.get(dia, [])
                    grid_calendario.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(str(dia), color="white" if es_hoy else "#212121", weight="bold" if es_hoy else "normal"),
                                ft.Container(
                                    content=ft.Text(str(len(tareas)), size=10, color="white", weight="bold"), 
                                    bgcolor="#FF7043", border_radius=10, width=18, height=18, visible=len(tareas)>0,
                                    alignment=ft.Alignment.CENTER
                                )
                            ], alignment="center", spacing=2),
                            bgcolor="#3C7517" if es_hoy else "white",
                            border_radius=10, 
                            alignment=ft.Alignment.CENTER,
                            on_click=lambda e, d=dia, t=tareas: seleccionar_dia(d, t)
                        )
                    )
        page.update()

    construir_interfaz()
    
    return ft.Container(
        padding=20, 
        expand=True,
        bgcolor="#F1F8E9",
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=volver_home, icon_color="#3C7517"), 
                ft.Text(f"{meses_nombres[mes_actual-1]} {anio_actual}", size=26, weight="bold", color="#3C7517")
            ]),
            ft.Container(
                content=grid_calendario, 
                bgcolor="white", 
                padding=15, 
                border_radius=25, 
                border=ft.border.all(1.5, "#3C7517"), 
                height=320
            ),
            ft.Text("Detalles del día:", weight="bold", size=20, color="#3C7517"), 
            lista_detalles
        ], scroll=ft.ScrollMode.ALWAYS)
    )