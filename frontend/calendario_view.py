import flet as ft
import datetime
import calendar
import requests

def obtener_calendario_view(page: ft.Page, volver_home, usuario_sesion):
    # --- 1. CONFIGURACIÓN INICIAL ---
    # Obtenemos tu ID. El id_familia lo buscaremos dinámicamente si no está.
    id_usuario_actual = usuario_sesion.get("id_usuario")
    
    # Fecha de referencia: Sábado 25 de Abril, 2026
    hoy = datetime.date(2026, 4, 25) 
    mes_actual = hoy.month
    anio_actual = hoy.year
    
    # Lista de nombres de meses en español
    meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    # Contenedores dinámicos
    grid_calendario = ft.GridView(runs_count=7, spacing=5, run_spacing=5, child_aspect_ratio=1.0)
    lista_detalles = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS, height=150)
    
    # --- SUB-FUNCIÓN: PARSEAR LA FECHA ---
    def parsear_fecha_completa(fecha_obj):
        try:
            if isinstance(fecha_obj, list) and len(fecha_obj) >= 3:
                return int(fecha_obj), int(fecha_obj), int(fecha_obj)
                
            f_texto = str(fecha_obj).strip()
            
            if f_texto.startswith("[") and f_texto.endswith("]"):
                f_texto = f_texto.replace("[", "").replace("]", "")
                p = f_texto.split(",")
                return int(p.strip()), int(p.strip()), int(p.strip())
                
            if "T" in f_texto:
                f_texto = f_texto.split("T")
                
            if "-" in f_texto:
                p = f_texto.split("-")
                if len(p) >= 3:
                    return int(p), int(p), int(p)
                    
            return 0, 0, 0 
        except Exception:
            return 0, 0, 0

    # --- 2. FUNCIÓN: BUSCAR ACTIVIDADES DEL MES ---
    def cargar_actividades_mes():
        # --- EL FIX MÁGICO: BUSCAR LA FAMILIA COMO LO HACE ACTIVIDADES ---
        id_fam = usuario_sesion.get("id_familia")
        
        if not id_fam and id_usuario_actual:
            try:
                res_fam = requests.get(f"http://127.0.0.1:8000/familias/{id_usuario_actual}/integrantes")
                if res_fam.status_code == 200:
                    id_fam = res_fam.json().get("id_familia")
            except:
                pass

        if not id_fam:
            print("SISTEMA CALENDARIO: No se encontró id_familia. Imposible cargar tareas.")
            return {}

        try:
            res = requests.get(f"http://127.0.0.1:8000/familias/{id_fam}/actividades")
            if res.status_code == 200:
                tareas = res.json()
                mapa = {}
                id_seguro = str(id_usuario_actual) 
                
                for t in tareas:
                    # Ignoramos las sugerencias del catálogo que no han sido publicadas
                    if t.get('es_sugerencia'):
                        continue
                        
                    if t.get("fecha"):
                        anio_t, mes_t, dia_t = parsear_fecha_completa(t["fecha"])
                        
                        # Si es del mes actual...
                        if anio_t == anio_actual and mes_t == mes_actual and dia_t > 0:
                            
                            asignados = t.get('usuarios_asignados', [])
                            ids_asignados = [str(u.get('id_usuario')) for u in asignados if isinstance(u, dict)]
                            
                            # Si tú estás en el equipo de esta tarea, la mostramos
                            if id_seguro in ids_asignados:
                                if dia_t not in mapa: mapa[dia_t] = []
                                mapa[dia_t].append(t)
                return mapa
        except Exception as e:
            print(f"ERROR CALENDARIO API: {e}")
            return {}
        return {}

    # --- 3. FUNCIÓN: MOSTRAR TAREAS AL TOCAR UN DÍA ---
    def seleccionar_dia(dia, tareas_dia):
        lista_detalles.controls.clear()
        if not tareas_dia:
            lista_detalles.controls.append(ft.Text(f"No hay actividades para el {dia} de {meses_nombres[mes_actual-1]}.", italic=True, color="#5D4037"))
        else:
            for t in tareas_dia:
                integrantes_lista = t.get('usuarios_asignados', [])
                nombres_asignados = ", ".join([u['nombre'] for u in integrantes_lista if isinstance(u, dict)])
                
                es_paz = "Reconciliación" in t['titulo'] or (t.get('descripcion') and "Reconciliación" in t.get('descripcion'))
                icono = ft.Icons.FAVORITE if es_paz else ft.Icons.TASK_ALT
                color_ic = "pink" if es_paz else "#3C7517"
                
                lista_detalles.controls.append(
                    ft.Container(
                        padding=10, bgcolor="white", border_radius=10, border=ft.border.all(1, "#3C7517"),
                        content=ft.Row([
                            ft.Icon(icono, color=color_ic),
                            ft.Column([
                                ft.Text(t['titulo'], weight="bold", size=14, color="#212121"),
                                ft.Text(t['descripcion'] or "Actividad familiar", size=12, color="#5D4037"),
                                ft.Row([
                                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=14, color="#3C7517"),
                                    ft.Text(
                                        f"Equipo: {nombres_asignados if nombres_asignados else 'Sin asignar'}", 
                                        size=11, 
                                        color="#3C7517", 
                                        weight="w500",
                                        italic=True
                                    )
                                ], spacing=5)
                            ], spacing=2, expand=True)
                        ])
                    )
                )
        page.update()

    # --- 4. FUNCIÓN: DIBUJAR LA CUADRÍCULA ---
    def construir_interfaz():
        grid_calendario.controls.clear()
        mapa_tareas = cargar_actividades_mes()
        
        for d in ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]:
            grid_calendario.controls.append(
                ft.Container(
                    content=ft.Text(d, weight="bold", size=12, color="#3C7517"), 
                    alignment=ft.Alignment.CENTER
                )
            )

        cal = calendar.Calendar(firstweekday=0)
        for semana in cal.monthdayscalendar(anio_actual, mes_actual):
            for dia in semana:
                if dia == 0:
                    grid_calendario.controls.append(ft.Container())
                else:
                    es_hoy = (dia == hoy.day)
                    tareas_dia = mapa_tareas.get(dia, [])
                    tiene_act = len(tareas_dia) > 0

                    grid_calendario.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(str(dia), color="white" if es_hoy else "#212121", weight="bold" if es_hoy else "normal"),
                                
                                ft.Container(
                                    content=ft.Text(str(len(tareas_dia)), size=10, color="white", weight="bold"),
                                    bgcolor="#FF7043", 
                                    border_radius=10,  
                                    width=18,
                                    height=18,
                                    alignment=ft.Alignment.CENTER, 
                                    visible=tiene_act 
                                )
                                
                            ], alignment="center", spacing=2),
                            bgcolor="#3C7517" if es_hoy else "white",
                            border_radius=8,
                            alignment=ft.Alignment.CENTER,
                            on_click=lambda e, d=dia, t=tareas_dia: seleccionar_dia(d, t)
                        )
                    )
        page.update()

    # --- DISEÑO FINAL ---
    construir_interfaz()
    
    return ft.Container(
        padding=20, expand=True,
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=volver_home, icon_color="#3C7517"),
                ft.Text(f"{meses_nombres[mes_actual-1]} {anio_actual}", size=24, weight="bold", color="#3C7517")
            ]),
            ft.Text("Toca un día para ver las responsabilidades familiares.", size=13, italic=True, color="#5D4037"),
            ft.Container(
                content=grid_calendario,
                bgcolor="#F1F8E9", padding=15, border_radius=20, border=ft.border.all(1, "#3C7517"),
                height=320 
            ),
            ft.Divider(height=10, color="transparent"),
            ft.Text("Detalles del día:", weight="bold", color="#3C7517", size=16),
            lista_detalles
        ], scroll=ft.ScrollMode.ALWAYS)
    )