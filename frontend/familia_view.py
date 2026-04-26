import flet as ft
import datetime
import json
import os

# --- RUTA DEL ARCHIVO DONDE SE GUARDARÁN LOS MENSAJES ---
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
    hoy_str = datetime.date.today().isoformat() # Ej: "2026-04-25"
    
    estado = {
        "nivel_mascota": 3, 
    }

    # --- PERSISTENCIA LOCAL INFALIBLE ---
    # 1. Leemos el archivo JSON físico
    mensajes_guardados = cargar_mensajes_disco()
        
    # 2. LA MAGIA DE LAS 24 HORAS: Filtramos y nos quedamos SOLO con los de hoy.
    mensajes_activos = [m for m in mensajes_guardados if m.get("fecha") == hoy_str]
    
    # 3. Guardamos la lista limpia de vuelta (así borramos para siempre los de ayer del archivo)
    guardar_mensajes_disco(mensajes_activos)

    # --- 7 MENSAJES MOTIVACIONALES POR NIVEL ---
    mensajes_niveles = {
        1: "¡Bienvenidos a la aventura! La semilla del amor familiar ha sido plantada. 🌱",
        2: "¡Van por buen camino! El trabajo en equipo empieza a dar frutos. 🌿",
        3: "¡Qué gran familia! Su dedicación hace que la mascota crezca feliz. 🐾",
        4: "¡Súper excelente! La comunicación y el esfuerzo los hace imparables. 🌟",
        5: "¡Increíble conexión! Son un verdadero ejemplo de unión familiar. 💖",
        6: "¡Nivel maestro! Los lazos que han construido son fuertes y hermosos. 🏆",
        7: "¡Felicidades, familia legendaria! Han alcanzado la máxima armonía. 👑"
    }

    nivel_seguro = max(1, min(7, estado["nivel_mascota"]))
    mensaje_actual = mensajes_niveles[nivel_seguro]

    # --- CONTENEDORES VISUALES ---
    lista_mensajes = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS, expand=True)
    
    txt_mensaje = ft.TextField(
        label="Escribe una sugerencia o cómo te sientes...", 
        expand=True, 
        bgcolor="white", 
        color="#212121", 
        border_color="#3C7517"
    )

    # --- FUNCIÓN: RENDERIZAR UN MENSAJE EN PANTALLA ---
    def dibujar_mensaje(msg):
        if msg["tipo"] == "emoji":
            return ft.Container(
                padding=10, bgcolor="white", border_radius=10, border=ft.border.all(1, "#CCCCCC"),
                content=ft.Text(f"{msg['autor']} se siente: {msg['contenido']}", size=15, color="#212121", weight="w500")
            )
        else:
            return ft.Container(
                padding=15, bgcolor="#E8F5E9", border_radius=10, border=ft.border.all(1, "#3C7517"),
                content=ft.Column([
                    ft.Text(f"{msg['autor']} dice:", weight="bold", color="#3C7517", size=12),
                    ft.Text(msg['contenido'], color="#212121", size=14)
                ], spacing=2)
            )

    # 4. Pintamos los mensajes que sobrevivieron al filtro
    for m in mensajes_activos:
        lista_mensajes.controls.append(dibujar_mensaje(m))

    # --- FUNCIÓN: ENVIAR EMOJI ---
    def enviar_emoji(emoji_seleccionado):
        nuevo_msg = {
            "tipo": "emoji", 
            "autor": nombre_usuario, 
            "contenido": emoji_seleccionado, 
            "fecha": hoy_str 
        }
        mensajes_activos.append(nuevo_msg)
        guardar_mensajes_disco(mensajes_activos) # ¡GUARDAMOS EN EL ARCHIVO!
        
        lista_mensajes.controls.append(dibujar_mensaje(nuevo_msg))
        page.update()

    # --- FUNCIÓN: ENVIAR TEXTO ---
    def enviar_texto(e):
        if not txt_mensaje.value.strip(): return
        
        nuevo_msg = {
            "tipo": "texto", 
            "autor": nombre_usuario, 
            "contenido": txt_mensaje.value, 
            "fecha": hoy_str 
        }
        mensajes_activos.append(nuevo_msg)
        guardar_mensajes_disco(mensajes_activos) # ¡GUARDAMOS EN EL ARCHIVO!
        
        lista_mensajes.controls.append(dibujar_mensaje(nuevo_msg))
        txt_mensaje.value = "" 
        page.update()

    # --- UI: SECCIÓN DE LA MASCOTA ---
    txt_nivel = ft.Text(f"Nivel de la Mascota: {estado['nivel_mascota']}", size=20, weight="bold", color="#3C7517")
    
    panel_mascota = ft.Container(
        padding=20, bgcolor="#F1F8E9", border_radius=15, border=ft.border.all(2, "#3C7517"),
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PETS, color="#3C7517", size=40),
                txt_nivel,
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Text(
                mensaje_actual, 
                size=14, 
                italic=True, 
                color="#5D4037", 
                weight="w500",
                text_align=ft.TextAlign.CENTER
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # --- UI: SECCIÓN DE EMOJIS ---
    panel_emojis = ft.Container(
        padding=10, bgcolor="white", border_radius=10, border=ft.border.all(1, "#E0E0E0"),
        content=ft.Column([
            ft.Text("¿Cómo te sientes hoy?", weight="bold", color="#212121"),
            ft.Row([
                ft.TextButton("😊 Feliz", on_click=lambda _: enviar_emoji("😊 Feliz")),
                ft.TextButton("😴 Cansado", on_click=lambda _: enviar_emoji("😴 Cansado")),
                ft.TextButton("🚀 Motivado", on_click=lambda _: enviar_emoji("🚀 Motivado")),
                ft.TextButton("❤️ Amoroso", on_click=lambda _: enviar_emoji("❤️ Amoroso")),
                ft.TextButton("😡 Estresado", on_click=lambda _: enviar_emoji("😡 Estresado"))
            ], wrap=True, alignment=ft.MainAxisAlignment.CENTER)
        ])
    )

    # --- RETORNO DE LA VISTA COMPLETA ---
    return ft.Container(
        padding=20, expand=True,
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=volver_home, icon_color="#3C7517"),
                ft.Text("Muro Familiar", size=26, weight="bold", color="#3C7517")
            ]),
            ft.Divider(color="#3C7517", thickness=2),
            panel_mascota,
            panel_emojis,
            ft.Text("Mensajes y Sugerencias:", weight="bold", color="#3C7517", size=16),
            ft.Container(
                content=lista_mensajes,
                expand=True,
                bgcolor="#FAFAFA",
                border_radius=10,
                padding=10
            ),
            ft.Row([
                txt_mensaje,
                ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color="white", bgcolor="#3C7517", on_click=enviar_texto)
            ])
        ])
    )