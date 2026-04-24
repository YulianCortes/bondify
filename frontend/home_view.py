import flet as ft
import requests

def obtener_home_view(page, nombre, rol, ir_a_bienvenida, ir_a_familia, ir_a_actividades, ir_a_calendario, ir_a_perfil, ir_a_mis_actividades, ir_a_configuracion, ir_a_gestion_familia, usuario_sesion, primer_nombre=None):
    
    # 1. Recuperamos datos de la sesión
    id_actual = usuario_sesion.get("id_usuario")
    # Si el perfil no tiene nombre, usamos el nombre de registro
    nombre_a_mostrar = primer_nombre if primer_nombre and primer_nombre.strip() != "" else nombre

    # --- ELEMENTOS DE LA INTERFAZ (OBJETOS DINÁMICOS) ---
    # Usamos variables claras para que el código sea fácil de leer
    puntos_personales_texto = ft.Text("0", size=24, weight="bold", color="#3C7517")
    racha_familiar_texto = ft.Text("Racha: 0", size=16, color="#558B2F", weight="w500")
    
    # Configuramos la mascota con coordenadas básicas para evitar errores de versión
    imagen_mascota = ft.Image(
        src="nivel_1.jpeg",
        width=240,
        height=240,
        fit="contain", # Evitamos ft.ImageFit
        animate_scale=ft.Animation(600, "bounceOut") # Evitamos ft.AnimationCurve
    )

    # --- LÓGICA DE ACTUALIZACIÓN ---
    def cargar_datos_pantalla():
        """Consulta al servidor los puntos y actualiza la mascota."""
        try:
            url_integrantes = f"http://127.0.0.1:8000/familias/{id_actual}/integrantes"
            respuesta = requests.get(url_integrantes)
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                pts_familia = datos.get("puntos_familia", 0)
                
                # Buscamos mis puntos en la lista de integrantes
                mis_puntos_actuales = 0
                for miembro in datos.get("integrantes", []):
                    if miembro['id_usuario'] == id_actual:
                        mis_puntos_actuales = miembro.get('puntos', 0)
                
                # Actualizamos los textos en pantalla
                puntos_personales_texto.value = str(mis_puntos_actuales)
                racha_familiar_texto.value = f"Racha Familiar: {pts_familia} pts"
                
                # CÁLCULO DE EVOLUCIÓN: Cada 15 puntos cambia de imagen
                nivel_calculado = (pts_familia // 15) + 1
                if nivel_calculado > 7: nivel_calculado = 7
                
                # Cambiamos la imagen JPEG
                imagen_mascota.src = f"nivel_{nivel_calculado}.jpeg"
                print(f"SISTEMA: Mostrando mascota nivel {nivel_calculado}")
                
                page.update()
        except Exception as e:
            print(f"Error en carga de datos: {e}")

    # --- FUNCIONES DEL MENÚ LATERAL ---
    def abrir_menu_lateral(e):
        capa_oscura_overlay.visible = True
        page.update()

    def cerrar_menu_lateral(e):
        capa_oscura_overlay.visible = False
        page.update()

    # --- CONSTRUCCIÓN DEL MENÚ (DISEÑO) ---
    cuadro_blanco_menu = ft.Container(
        width=280, 
        bgcolor="#F4EAE0", 
        border_radius=15, 
        padding=20,
        shadow=ft.BoxShadow(blur_radius=20, color="black26"),
        content=ft.Column([
            # Cabecera del menú con avatar
            ft.Row([
                ft.Container(
                    on_click=lambda e: [cerrar_menu_lateral(None), ir_a_perfil(e)],
                    content=ft.Row([
                        ft.CircleAvatar(content=ft.Icon(ft.Icons.PERSON), bgcolor="#D7CCC8", radius=25),
                        ft.Text(nombre_a_mostrar, size=18, weight="bold", color="#864430")
                    ])
                ),
                ft.IconButton(ft.Icons.CLOSE, on_click=cerrar_menu_lateral, icon_color="#864430")
            ], alignment="spaceBetween"),
            
            ft.Divider(height=20, color="#D7CCC8"),
            
            # Listado de opciones
            ft.ListTile(
                leading=ft.Icon(ft.Icons.SETTINGS, color="#5D4037"), 
                title=ft.Text("Configuración", color="#5D4037"), 
                on_click=lambda e: [cerrar_menu_lateral(None), ir_a_configuracion(e)]
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.GROUP, color="#5D4037"), 
                title=ft.Text("Mi Familia", color="#5D4037"), 
                on_click=lambda e: [cerrar_menu_lateral(None), ir_a_gestion_familia(e)]
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LIST_ALT, color="#5D4037"), 
                title=ft.Text("Actividades", color="#5D4037"), 
                on_click=lambda e: [cerrar_menu_lateral(None), ir_a_actividades(e)]
            ),
        ], spacing=10)
    )

    # Capa de fondo que se oscurece al abrir el menú
    capa_oscura_overlay = ft.Container(
        content=cuadro_blanco_menu,
        # SOLUCIÓN AL ERROR: Usamos coordenadas directas (-1 es izquierda, -1 es arriba)
        alignment=ft.Alignment(-1, -1), 
        bgcolor="#AA000000", 
        visible=False, 
        expand=True, 
        on_click=cerrar_menu_lateral 
    )

    # --- CUERPO PRINCIPAL DE LA PANTALLA ---
    # Aquí es donde ocurre la magia de Bondify
    columna_principal = ft.Column(
        [
            # BARRA SUPERIOR (LOGO Y PUNTOS)
            ft.Container(
                padding=10, 
                content=ft.Row([
                    ft.IconButton(ft.Icons.MENU, icon_color="#864430", on_click=abrir_menu_lateral),
                    ft.Text("Bondify", size=24, weight="bold", color="#864430"),
                    # Espaciador invisible para empujar los puntos a la derecha
                    ft.Container(expand=True), 
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.STARS, color="#3C7517", size=22),
                            puntos_personales_texto
                        ]),
                        padding=ft.padding.only(right=10)
                    )
                ])
            ),
            
            ft.Container(height=30), # Espacio
            
            # SALUDO PERSONALIZADO
            ft.Text(f"¡Hola, {nombre_a_mostrar}!", size=34, weight="bold", color="#558B2F", text_align="center"),
            racha_familiar_texto,

            ft.Container(height=50),

            # EL NÚCLEO: LA MASCOTA QUE EVOLUCIONA
            ft.Container(
                content=imagen_mascota,
                alignment=ft.Alignment(0, 0), # 0,0 es el centro exacto
                on_hover=lambda e: setattr(imagen_mascota, "scale", 1.1 if e.data == "true" else 1.0) or page.update()
            ),
            
            ft.Container(expand=True), # Empuja el consejo hacia abajo
            
            # BARRA DE CONSEJO O ESTADO
            ft.Container(
                margin=25, 
                padding=15, 
                bgcolor="#E8F5E9", 
                border_radius=15,
                border=ft.border.all(1, "#388E3C"),
                content=ft.Text(
                    "¡Trabajen en equipo! Cada 15 actividades completadas, su racha familiar subirá de nivel.", 
                    color="#2E7D32", 
                    text_align="center", 
                    italic=True,
                    size=13
                )
            )
        ],
        horizontal_alignment="center",
        expand=True
    )

    # Iniciamos la carga de datos apenas entramos
    cargar_datos_pantalla()

    # Devolvemos la vista en capas (Stack)
    return ft.Stack([
        columna_principal,
        capa_oscura_overlay
    ], expand=True)