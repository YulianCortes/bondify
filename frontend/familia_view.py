import flet as ft

def obtener_familia_view(page, volver_home):
    """
    Crea la vista de la sección de familia con un diseño de árbol jerárquico.
    Muestra contenedores vacíos para los perfiles, simulando la estructura Jefe -> Familiares.
    """

    # --- CONFIGURACIÓN DE ESTILO ---
    page.bgcolor = "#D1E8E4" # Fondo verde menta pastel (el mismo de home)
    page.padding = 0
    
    # Colores Aesthetic (Pink & Clean)
    color_jefe = ft.Colors.PINK_300      # Rosa más fuerte para el Jefe
    color_familiar = ft.Colors.PINK_100   # Rosa pastel para los Familiares
    color_lineas = "#9575CD"              # Púrpura de tus botones para los conectores
    
    # --- COMPONENTES REUTILIZABLES ---
    
    def crear_tarjeta_perfil(color_fondo, ancho, alto):
        """Crea un contenedor de perfil vacío con bordes redondeados y sombra."""
        return ft.Container(
            width=ancho,
            height=alto,
            bgcolor=color_fondo,
            border_radius=15,
            border=ft.border.all(2, ft.Colors.WHITE), # Borde blanco fino
            # Añadimos una sombra suave para el efecto aesthetic
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK54),
                offset=ft.Offset(2, 3),
            ),
        )

    def crear_linea_conector(ancho, alto, left=0, top=0, border_side="top"):
        """Crea una línea de conexión usando bordes de un contenedor transparente."""
        border = None
        if border_side == "top":
            border = ft.border.only(top=ft.BorderSide(3, color_lineas))
        elif border_side == "left":
            border = ft.border.only(left=ft.BorderSide(3, color_lineas))
        elif border_side == "right":
            border = ft.border.only(right=ft.BorderSide(3, color_lineas))

        return ft.Container(
            width=ancho,
            height=alto,
            left=left,
            top=top,
            border=border,
            bgcolor="transparent",
        )

    # --- CONSTRUCCIÓN DEL ÁRBOL (USANDO STACK) ---
    # Stack nos permite posicionar elementos de forma absoluta (coordenadas x,y).
    
    # 1. Perfil del Jefe (Arriba, centrado)
    jefe_perfil = ft.Container(
        content=crear_tarjeta_perfil(color_jefe, 140, 100),
        left=110, # (360 - 140) / 2 = 110 para centrar
        top=20,
    )

    # 2. Línea vertical desde el Jefe hacia abajo
    linea_vertical_principal = crear_linea_conector(ancho=4, alto=50, left=178, top=120, border_side="left")

    # 3. Línea horizontal de expansión (la "T" invertida)
    linea_horizontal_T = crear_linea_conector(ancho=260, alto=4, left=50, top=170, border_side="top")

    # 4. Líneas verticales hacia los Familiares
    linea_vertical_fam1 = crear_linea_conector(ancho=4, alto=30, left=50, top=170, border_side="left")
    linea_vertical_fam2 = crear_linea_conector(ancho=4, alto=30, left=178, top=170, border_side="left")
    linea_vertical_fam3 = crear_linea_conector(ancho=4, alto=30, left=306, top=170, border_side="left")

    # 5. Perfiles de Familiares (Abajo, en fila)
    familiar1_perfil = ft.Container(content=crear_tarjeta_perfil(color_familiar, 100, 80), left=0, top=200)
    familiar2_perfil = ft.Container(content=crear_tarjeta_perfil(color_familiar, 100, 80), left=128, top=200)
    familiar3_perfil = ft.Container(content=crear_tarjeta_perfil(color_familiar, 100, 80), left=256, top=200)

    # El Stack con todo el árbol genealógico
    arbol_familia = ft.Stack(
        [
            # Dibujamos las líneas primero para que queden "detrás" de los perfiles
            linea_vertical_principal,
            linea_horizontal_T,
            linea_vertical_fam1,
            linea_vertical_fam2,
            linea_vertical_fam3,
            # Luego los perfiles
            jefe_perfil,
            familiar1_perfil,
            familiar2_perfil,
            familiar3_perfil,
        ],
        width=360,
        height=300,
    )

    # --- RETORNO DE LA COLUMNA PRINCIPAL ---
    return ft.Column(
        [
            # Barra superior personalizada (estilo home_view)
            ft.Container(
                height=60,
                content=ft.Row([
                    ft.Container(content=ft.Image(src="volver.png", width=30, height=30), on_click=volver_home, padding=10),
                    ft.Text("Mi Familia", size=22, weight="bold", color="#558B2F")
                ], alignment=ft.MainAxisAlignment.START),
                bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.WHITE), # Fondo semi-transparente
                border=ft.border.only(bottom=ft.BorderSide(1, color="#BDBDBD")),
            ),
            
            # Espaciado
            ft.Container(height=30),
            
            # Título de la sección
            ft.Text("Jerarquía Familiar", size=26, weight="bold", color="#558B2F", text_align="center"),
            
            # El árbol jerárquico centrado
            ft.Container(
                content=arbol_familia,
                padding=20,
            ),
            
            ft.Container(expand=True), # Empuja todo hacia arriba
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        expand=True
    )