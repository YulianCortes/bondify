import flet as ft
import datetime
import json
import os
import requests 

# --- RUTA DEL ARCHIVO DONDE SE GUARDARÁN LOS MENSAJES (MANTENIDO) ---
ARCHIVO_MENSAJES = "historial_muro.json"

def cargar_mensajes_disco():
    """Lee los mensajes del archivo físico si existe."""
    if os.path.exists(ARCHIVO_MENSAJES):
        try:
            with open(ARCHIVO_MENSAJES, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def guardar_mensajes_disco(mensajes):
    """Guarda los mensajes en el archivo físico."""
    try:
        with open(ARCHIVO_MENSAJES, "w", encoding="utf-8") as f:
            json.dump(mensajes, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error guardando mensajes: {e}")

def obtener_familia_view(page: ft.Page, volver_home, usuario_sesion):
    # --- CONFIGURACIÓN Y ESTADO ---
    nombre_usuario = usuario_sesion.get("nombre") or "Miembro de la familia"
    id_familia = usuario_sesion.get("id_familia")
    id_usuario_logueado = usuario_sesion.get("id_usuario") 
    hoy_str = datetime.date.today().isoformat() 
    
    estado = {"nivel_mascota": 1}

    # --- PERSISTENCIA LOCAL (MANTENIDA) ---
    mensajes_guardados = cargar_mensajes_disco()
    mensajes_activos = [m for m in mensajes_guardados if m.get("fecha") == hoy_str]
    guardar_mensajes_disco(mensajes_activos)

    # --- 7 MENSAJES MOTIVACIONALES POR NIVEL (MANTENIDO) ---
    mensajes_niveles = {
        1: "¡Bienvenidos! La semilla del amor ha sido plantada. 🌱",
        2: "¡Van por buen camino! El equipo da frutos. 🌿",
        3: "¡Qué gran familia! La mascota crece feliz. 🐾",
        4: "¡Súper excelente! Son imparables. 🌟",
        5: "¡Increíble conexión! Ejemplo de unión. 💖",
        6: "¡Nivel maestro! Lazos fuertes y hermosos. 🏆",
        7: "¡Felicidades, familia legendaria! Armonía total. 👑"
    }

    puntos_fam = usuario_sesion.get("puntos_familia") or 0
    nivel_calculado = max(1, min(7, (puntos_fam // 15) + 1))
    mensaje_actual = mensajes_niveles.get(nivel_calculado, "¡Sigamos adelante!")

    # --- CONTROLES DINÁMICOS ---
    lista_mensajes = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS, expand=True)
    txt_mensaje = ft.TextField(
        label="Escribe aquí...", expand=True, bgcolor="white", 
        color="#212121", border_color="#3C7517", border_radius=10
    )
    txt_nivel_display = ft.Text(f"Nivel: {nivel_calculado}", size=18, weight="bold", color="#3C7517")
    txt_motivacion_display = ft.Text(mensaje_actual, size=12, italic=True, color="#5D4037")

    # --- FUNCIÓN: RENDERIZAR MENSAJE ---
    def dibujar_mensaje(msg):
        if msg["tipo"] == "emoji":
            return ft.Container(
                expand=True, padding=10, bgcolor="white", border_radius=12, border=ft.border.all(1, "#E0E0E0"),
                content=ft.Text(f"{msg['autor']} se siente: {msg['contenido']}", size=14, color="#212121")
            )
        else:
            return ft.Container(
                expand=True, padding=12, bgcolor="#E8F5E9", border_radius=12, border=ft.border.all(1, "#3C7517"),
                content=ft.Column([
                    ft.Text(f"{msg['autor']} dice:", weight="bold", color="#3C7517", size=11),
                    ft.Text(msg['contenido'], color="#212121", size=13)
                ], spacing=1)
            )

    # --- LÓGICA DE DATOS (MANTENIDA) ---
    def cargar_muro_db():
        if not id_familia: return
        try:
            r = requests.get(f"http://127.0.0.1:8000/familias/{id_familia}/muro", timeout=2)
            if r.status_code == 200:
                mensajes_db = r.json()
                lista_mensajes.controls.clear()
                for m in mensajes_db:
                    lista_mensajes.controls.append(dibujar_mensaje(m))
                page.update()
        except: pass

    def refrescar_nivel_desde_db():
        try:
            res = requests.get(f"http://127.0.0.1:8000/familias/{id_usuario_logueado}/integrantes", timeout=2)
            if res.status_code == 200:
                datos = res.json()
                puntos_reales = datos.get("puntos_familia", 0)
                nuevo_nivel = min(7, (puntos_reales // 15) + 1)
                txt_nivel_display.value = f"Nivel: {nuevo_nivel}"
                txt_motivacion_display.value = mensajes_niveles.get(nuevo_nivel, "¡Sigamos!")
                page.update()
        except: pass

    def enviar_emoji(emoji_seleccionado):
        nuevo_msg = {"tipo": "emoji", "autor": nombre_usuario, "contenido": emoji_seleccionado, "fecha": hoy_str}
        mensajes_activos.append(nuevo_msg)
        guardar_mensajes_disco(mensajes_activos)
        if id_familia:
            try: requests.post(f"http://127.0.0.1:8000/familias/{id_familia}/muro", json=nuevo_msg, timeout=2)
            except: pass
        cargar_muro_db()

    def enviar_texto(e):
        if not txt_mensaje.value.strip(): return
        nuevo_msg = {"tipo": "texto", "autor": nombre_usuario, "contenido": txt_mensaje.value, "fecha": hoy_str}
        mensajes_activos.append(nuevo_msg)
        guardar_mensajes_disco(mensajes_activos)
        if id_familia:
            try: requests.post(f"http://127.0.0.1:8000/familias/{id_familia}/muro", json=nuevo_msg, timeout=2)
            except: pass
        txt_mensaje.value = "" 
        cargar_muro_db()

    # --- UI: COMPACTACIÓN MASTER ---
    # 1. Mascota en modo horizontal (Slim)
    panel_mascota = ft.Container(
        padding=10, bgcolor="#F1F8E9", border_radius=15, border=ft.border.all(1.5, "#3C7517"),
        content=ft.Row([
            ft.Icon(ft.Icons.PETS, color="#3C7517", size=30),
            ft.Column([
                txt_nivel_display,
                txt_motivacion_display
            ], spacing=0, expand=True)
        ], alignment=ft.MainAxisAlignment.START)
    )

    # 2. Emojis en modo compacto
    panel_emojis = ft.Container(
        padding=5, bgcolor="white", border_radius=10, border=ft.border.all(1, "#E0E0E0"),
        content=ft.Column([
            ft.Text("¿Cómo te sientes?", weight="bold", size=13),
            ft.Row([
                ft.TextButton("😊 Feliz", on_click=lambda _: enviar_emoji("😊 Feliz"), style=ft.ButtonStyle(padding=2)),
                ft.TextButton("😔 Triste", on_click=lambda _: enviar_emoji("😔 Triste"), style=ft.ButtonStyle(padding=2)),
                ft.TextButton("🚀 OK", on_click=lambda _: enviar_emoji("🚀 Motivado"), style=ft.ButtonStyle(padding=2)),
                ft.TextButton("❤️ Amor", on_click=lambda _: enviar_emoji("❤️ Amor"), style=ft.ButtonStyle(padding=2)),
                ft.TextButton("😡 Mal", on_click=lambda _: enviar_emoji("😡 Estresado"), style=ft.ButtonStyle(padding=2))
            ], wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=0)
        ], spacing=2)
    )

    refrescar_nivel_desde_db()
    cargar_muro_db()

    # --- RETORNO DE LA VISTA (ESTRUCTURA CORREGIDA) ---
    return ft.Container(
        padding=15, expand=True,
        bgcolor="#D1E8E4", 
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=volver_home, icon_color="#3C7517", icon_size=18),
                ft.Text("Muro Familiar", size=22, weight="bold", color="#3C7517")
            ]),
            panel_mascota,
            panel_emojis,
            ft.Text("Mensajes:", weight="bold", color="#3C7517", size=15),
            
            # EL MURO: Expand=True para que use todo lo que sobra
            ft.Container(
                content=lista_mensajes,
                expand=True, # Toma todo el espacio disponible
                bgcolor="#FAFAFA",
                border_radius=15,
                padding=10,
                border=ft.border.all(1, "#D1E8E4")
            ),
            
            ft.Row([
                txt_mensaje,
                ft.IconButton(
                    icon=ft.Icons.SEND_ROUNDED, icon_color="white", 
                    bgcolor="#3C7517", on_click=enviar_texto
                )
            ])
        ], spacing=8)
    )