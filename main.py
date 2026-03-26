import flet as ft
from app.ui.auth_page import login_view, signin_view
from app.ui.dashboard_page import dashboard_view

async def main(page: ft.Page):
    page.title = "BankApp Control - Supervision"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    page.bgcolor = "#f8fafc"
    page.padding = 0

    current_user = None

    async def on_login_success(user):
        nonlocal current_user
        current_user = user
        await page.push_route("/dashboard")

    async def on_logout(e=None):
        nonlocal current_user
        current_user = None
        await page.push_route("/")

    async def route_change(e):
        try:
            page.views.clear()
            
            if page.route == "/":
                page.views.append(login_view(page, on_login_success, page.push_route))
            elif page.route == "/signin":
                page.views.append(signin_view(page, page.push_route))
            elif page.route == "/dashboard":
                if current_user:
                    view = await dashboard_view(page, current_user, on_logout)
                    page.views.append(view)
                else:
                    await page.push_route("/")
            
            page.update()
        except Exception as ex:
            print(f"Route Error: {ex}")
            page.snack_bar = ft.SnackBar(ft.Text(f"Erreur de rendu: {ex}"), bgcolor="#ef4444")
            page.snack_bar.open = True
            page.update()

    async def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top = page.views[-1]
            await page.push_route(top.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    await route_change(None)



if __name__ == "__main__":
    ft.run(main)