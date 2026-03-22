import flet as ft
from app.controller.auth_controller import AuthController

# --- Palette ---
BG       = "#f8fafc"
CARD     = "#ffffff"
ACCENT   = "#2563eb"
TEXT     = "#0f172a"
MUTED    = "#64748b"
ERROR    = "#ef4444"
SUCCESS  = "#10b981"
BORDER   = "#e2e8f0"

def _input_field(label, icon, password=False):
    return ft.TextField(
        label=label,
        prefix_icon=icon,
        password=password,
        can_reveal_password=password,
        border_radius=12,
        border_color=BORDER,
        focused_border_color=ACCENT,
        bgcolor="#ffffff",
        label_style=ft.TextStyle(color=MUTED),
        color=TEXT,
        cursor_color=ACCENT,
    )

def _auth_button(text, on_click):
    return ft.Container(
        content=ft.Text(text, weight="bold", size=16, color="white"),
        bgcolor=ACCENT,
        padding=ft.padding.symmetric(horizontal=40, vertical=15),
        border_radius=12,
        alignment=ft.Alignment.CENTER,
        on_click=on_click,
        animate=ft.Animation(200, "easeOut"),
    )

def login_view(page: ft.Page, on_login_success, navigate_to):
    username = _input_field("Identifiant", ft.Icons.PERSON_OUTLINE)
    password = _input_field("Mot de passe", ft.Icons.LOCK_OUTLINE, True)

    async def handle_login(e):
        user = AuthController.login(username.value, password.value)
        if user:
            page.snack_bar = ft.SnackBar(ft.Text(f"Accès autorisé : {user.username}"), bgcolor=SUCCESS)
            page.snack_bar.open = True
            await on_login_success(user)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Échec de l'authentification"), bgcolor=ERROR)
            page.snack_bar.open = True
            page.update()

    async def go_signin(e):
        navigate_to("/signin")

    return ft.View(
        route="/",
        bgcolor=BG,
        padding=0,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.LOCK_PERSON_ROUNDED, size=60, color=ACCENT),
                    ft.Text("BankApp Control", size=32, weight="bold", color=TEXT),
                    ft.Text("Connexion au terminal de supervision", color=MUTED),
                    ft.Container(height=20),
                    username,
                    password,
                    ft.Container(height=10),
                    _auth_button("Se connecter", handle_login),
                    ft.TextButton("Paramétrage Initial", on_click=go_signin)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                bgcolor=CARD,
                padding=40,
                border_radius=30,
                width=420,
                border=ft.border.all(1, BORDER),
                shadow=ft.BoxShadow(blur_radius=50, color="#0000000d")
            )
        ]
    )

def signin_view(page: ft.Page, navigate_to):
    username = _input_field("Nom d'utilisateur", ft.Icons.PERSON_OUTLINE)
    password = _input_field("Mot de passe", ft.Icons.LOCK_OUTLINE, True)
    
    role_dropdown = ft.Dropdown(
        label="Rôle Système",
        options=[
            ft.dropdown.Option("admin", "Administrateur"),
            ft.dropdown.Option("user", "Collaborateur"),
        ],
        border_radius=12,
        value="user",
        border_color=BORDER,
        color=TEXT
    )

    async def handle_signin(e):
        user, msg = AuthController.signin(username.value, password.value, role_dropdown.value)
        if user:
            page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=SUCCESS)
            page.snack_bar.open = True
            await navigate_to("/")
        else:
            page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ERROR)
            page.snack_bar.open = True
            page.update()

    async def go_back(e):
        navigate_to("/")

    return ft.View(
        route="/signin",
        bgcolor=BG,
        padding=0,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text("Nouvel Utilisateur", size=28, weight="bold", color=TEXT),
                    ft.Container(height=10),
                    username,
                    password,
                    role_dropdown,
                    ft.Container(height=10),
                    _auth_button("Enregistrer", handle_signin),
                    ft.TextButton("Retour", on_click=go_back)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                bgcolor=CARD,
                padding=40,
                border_radius=30,
                width=420,
                border=ft.border.all(1, BORDER)
            )
        ]
    )
