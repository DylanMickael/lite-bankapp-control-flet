import flet as ft

def table_card(title, table, actions=None):
    return ft.Container(
        padding=20,
        expand=True,
        content=ft.Column([
            ft.Row([
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color="#0f172a"),
                actions if actions else ft.Container()
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=10),
            ft.Column([
                ft.Row([
                    ft.Container(
                        content=table,
                        border_radius=12,
                        bgcolor="white",
                        expand=True,
                        border=ft.border.all(1, "#e2e8f0"),
                    )
                ], expand=True)
            ], expand=True, scroll=ft.ScrollMode.AUTO)
        ], expand=True)
    )
