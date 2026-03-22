import flet as ft

def stat_card(label, value, icon, color):
    return ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(icon, color=color, size=24),
                bgcolor=f"{color}15",
                padding=12,
                border_radius=12
            ),
            ft.Column([
                ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color="#0f172a"),
                ft.Text(label, size=12, color="#64748b"),
            ], spacing=0)
        ], spacing=16),
        bgcolor="white",
        padding=20,
        border_radius=16,
        border=ft.border.all(1, "#e2e8f0"),
        expand=True
    )
