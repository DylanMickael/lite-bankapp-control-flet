import flet as ft
from app.controller.client_controller import ClientController
from app.controller.virement_controller import VirementController
from app.controller.audit_controller import AuditController
from app.components.stat_card import stat_card
from app.components.table_card import table_card
import datetime

# --- Palette ---
BG       = "#f8fafc"
CARD     = "#ffffff"
ACCENT   = "#2563eb"
BORDER   = "#e2e8f0"
TEXT     = "#0f172a"
MUTED    = "#64748b"
ERROR    = "#ef4444"
SUCCESS  = "#10b981"
WARNING  = "#f59e0b"

async def dashboard_view(page: ft.Page, current_user, on_logout):
    v_ctrl = VirementController()
    c_ctrl = ClientController()
    a_ctrl = AuditController()

    is_admin = current_user.role == "admin"
    is_simple_user = current_user.role == "user"
    selected_v_id = [None]
    selected_c_num = [None]
    
    # --- Inputs ---
    input_c_nom = ft.TextField(label="Nom Client", border_radius=10)
    input_c_solde = ft.TextField(label="Solde Initial (Ar)", border_radius=10)
    input_v_nc = ft.TextField(label="N° Compte", border_radius=10)
    input_v_amt = ft.TextField(label="Montant (Ar)", border_radius=10)

    stats_container = ft.Container()
    audit_stats_container = ft.Container()
    clients_container = ft.Container()
    virements_container = ft.Container()
    audit_container = ft.Container()

    # --- Persistent Modals in Overlay ---
    async def close_dlg(e):
        for dlg in [c_modal, v_modal, conf_modal]:
            dlg.open = False
        page.update()

    async def save_client(e):
        try:
            val = float(input_c_solde.value or 0)
            if selected_c_num[0]: c_ctrl.update(selected_c_num[0], input_c_nom.value, val)
            else: c_ctrl.create(input_c_nom.value, val)
            await close_dlg(None); await refresh_data()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erreur Client: {ex}"), bgcolor=ERROR); page.snack_bar.open = True; page.update()

    async def save_virement(e):
        try:
            amt = float(input_v_amt.value or 0); nc = int(input_v_nc.value or 0)
            if selected_v_id[0]: v_ctrl.update(selected_v_id[0], nc, amt, current_user.username)
            else: v_ctrl.create(nc, amt, current_user.username)
            await close_dlg(None); await refresh_data()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erreur Virement: {ex}"), bgcolor=ERROR); page.snack_bar.open = True; page.update()

    async def exec_delete(e):
        if selected_c_num[0]: 
            c_ctrl.delete(selected_c_num[0]); selected_c_num[0] = None
        elif selected_v_id[0]: 
            v_ctrl.delete(selected_v_id[0], current_user.username); selected_v_id[0] = None
        await close_dlg(None); await refresh_data()

    c_modal = ft.AlertDialog(
        title=ft.Text("Gestion Client"),
        content=ft.Column([input_c_nom, input_c_solde], tight=True, spacing=15),
        actions=[ft.TextButton("Annuler", on_click=close_dlg), ft.ElevatedButton("Enregistrer", bgcolor=ACCENT, color="white", on_click=save_client)]
    )
    
    v_modal = ft.AlertDialog(
        title=ft.Text("Gestion Virement"),
        content=ft.Column([input_v_nc, input_v_amt], tight=True, spacing=15),
        actions=[ft.TextButton("Annuler", on_click=close_dlg), ft.ElevatedButton("Confirmer", bgcolor=ACCENT, color="white", on_click=save_virement)]
    )

    conf_modal = ft.AlertDialog(
        title=ft.Text("Confirmation"),
        content=ft.Text("Êtes-vous sûr de vouloir supprimer cet élément ?"),
        actions=[ft.TextButton("Non", on_click=close_dlg), ft.ElevatedButton("Oui, Supprimer", bgcolor=ERROR, color="white", on_click=exec_delete)]
    )

    # Pre-add to overlay for reliability
    if not any(d in page.overlay for d in [c_modal, v_modal, conf_modal]):
        page.overlay.extend([c_modal, v_modal, conf_modal])

    # --- Refresh Logic ---
    async def refresh_data(e=None):
        try:
            all_v = v_ctrl.get_all(); all_c = c_ctrl.get_all(); all_a = a_ctrl.get_all() if is_admin else []
            audit_counts = a_ctrl.get_counts() if is_admin else {"ajout": 0, "modification": 0, "suppression": 0}
            
            def create_stats_row():
                return ft.Row([
                    stat_card("Ajout", audit_counts["ajout"], ft.Icons.ADD_CIRCLE, ACCENT),
                    stat_card("Modification", audit_counts["modification"], ft.Icons.EDIT, ACCENT),
                    stat_card("Suppression", audit_counts["suppression"], ft.Icons.DELETE, ERROR)
                ], spacing=20)
            
            stats_container.content = create_stats_row()
            if is_admin:
                audit_stats_container.content = create_stats_row()

            def mk_on_c_select(num):
                async def on_select(e):
                    selected_c_num[0] = num if str(e.data).lower() == "true" else None
                    await refresh_data()
                return on_select

            clients_container.content = ft.DataTable(
                columns=[ft.DataColumn(ft.Text("N°")), ft.DataColumn(ft.Text("Nom")), ft.DataColumn(ft.Text("Solde"), numeric=True)],
                show_checkbox_column=True,
                rows=[ft.DataRow(
                    selected=(c.num_compte == selected_c_num[0]),
                    cells=[ft.DataCell(ft.Text(str(c.num_compte))), ft.DataCell(ft.Text(c.nomclient)), ft.DataCell(ft.Text(f"{float(c.solde or 0):,.2f}", weight="bold"))],
                    on_select_change=mk_on_c_select(c.num_compte)
                ) for c in all_c]
            )

            def mk_on_v_select(vid):
                async def on_select(e):
                    selected_v_id[0] = vid if str(e.data).lower() == "true" else None
                    await refresh_data()
                return on_select

            virements_container.content = ft.DataTable(
                columns=[ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Compte")), ft.DataColumn(ft.Text("Montant"), numeric=True), ft.DataColumn(ft.Text("Date"))],
                show_checkbox_column=True,
                rows=[ft.DataRow(
                    selected=(v.num_virement == selected_v_id[0]),
                    cells=[ft.DataCell(ft.Text(str(v.num_virement))), ft.DataCell(ft.Text(str(v.num_compte))), ft.DataCell(ft.Text(f"{float(v.montant or 0):,.2f}", weight="bold")), ft.DataCell(ft.Text(v.date_virement.strftime("%Y-%m-%d %H:%M") if v.date_virement else "—"))],
                    on_select_change=mk_on_v_select(v.num_virement)
                ) for v in all_v]
            )

            if is_admin:
                audit_container.content = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Action")),
                        ft.DataColumn(ft.Text("Compte")),
                        ft.DataColumn(ft.Text("Client")),
                        ft.DataColumn(ft.Text("Date Vir.")),
                        ft.DataColumn(ft.Text("Date Op.")),
                        ft.DataColumn(ft.Text("Anc.")),
                        ft.DataColumn(ft.Text("Nouv.")),
                        ft.DataColumn(ft.Text("User")),
                    ],
                    rows=[
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text((a.type_action or "").upper())),
                            ft.DataCell(ft.Text(str(a.num_compte or ""))),
                            ft.DataCell(ft.Text(a.nom_client or "—")),
                            ft.DataCell(ft.Text(a.date_virement.strftime("%Y-%m-%d %H:%M") if a.date_virement else "—")),
                            ft.DataCell(ft.Text(a.date_operation.strftime("%Y-%m-%d %H:%M") if a.date_operation else "—")),
                            ft.DataCell(ft.Text(f"{float(a.montant_ancien or 0):,.2f}")),
                            ft.DataCell(ft.Text(f"{float(a.montant_nouv or 0):,.2f}")),
                            ft.DataCell(ft.Text(a.utilisateur or "")),
                        ]) for a in all_a
                    ]
                )
            page.update()
        except Exception as ex: print(f"Refresh Error: {ex}")

    # --- UI Handlers ---
    async def open_c_dlg(e, edit=False):
        if edit and not selected_c_num[0]:
            page.snack_bar = ft.SnackBar(ft.Text("Sélectionnez un client."), bgcolor=WARNING); page.snack_bar.open = True; page.update(); return
        c_modal.title.value = "Modifier Client" if edit else "Nouveau Client"
        if edit:
            c = next((c for c in c_ctrl.get_all() if c.num_compte == selected_c_num[0]), None)
            if c: input_c_nom.value = c.nomclient; input_c_solde.value = str(c.solde)
        else: input_c_nom.value = ""; input_c_solde.value = "0.0"
        c_modal.open = True; page.update()

    async def open_v_dlg(e, edit=False):
        if edit and not selected_v_id[0]:
            page.snack_bar = ft.SnackBar(ft.Text("Sélectionnez une opération."), bgcolor=WARNING); page.snack_bar.open = True; page.update(); return
        v_modal.title.value = "Modifier Virement" if edit else "Nouveau Virement"
        if edit:
            v = next((v for v in v_ctrl.get_all() if v.num_virement == selected_v_id[0]), None)
            if v: input_v_nc.value = str(v.num_compte); input_v_amt.value = str(v.montant)
        else: input_v_nc.value = ""; input_v_amt.value = ""
        v_modal.open = True; page.update()

    async def open_conf(e):
        if not selected_c_num[0] and not selected_v_id[0]: return
        conf_modal.open = True; page.update()

    # --- UI Assembly ---
    tabs_header = ft.TabBar(tabs=[ft.Tab(label="Accueil", icon=ft.Icons.DASHBOARD)])
    if is_simple_user: 
        tabs_header.tabs.append(ft.Tab(label="Clients", icon=ft.Icons.PERSON))
        tabs_header.tabs.append(ft.Tab(label="Virements", icon=ft.Icons.SWAP_HORIZ))
    if is_admin: 
        tabs_header.tabs.append(ft.Tab(label="Audit", icon=ft.Icons.HISTORY))

    c_actions = ft.Row([ft.ElevatedButton("Ajouter", on_click=lambda e: page.run_task(open_c_dlg, e)), ft.ElevatedButton("Modifier", on_click=lambda e: page.run_task(open_c_dlg, e, True)), ft.IconButton(ft.Icons.DELETE, icon_color=ERROR, on_click=open_conf)])
    v_actions = ft.Row([ft.ElevatedButton("Ajouter", on_click=lambda e: page.run_task(open_v_dlg, e)), ft.ElevatedButton("Modifier", on_click=lambda e: page.run_task(open_v_dlg, e, True)), ft.IconButton(ft.Icons.DELETE, icon_color=ERROR, on_click=open_conf)])

    tabs_view = ft.TabBarView(expand=True, controls=[
        ft.Column([
            ft.Column([ft.Container(padding=30, content=ft.Text(f"Bienvenue, {current_user.username}", size=24, weight="bold"))], expand=True, scroll=ft.ScrollMode.AUTO)
        ], expand=True),
    ])
    if is_simple_user: 
        tabs_view.controls.append(table_card("Clients", clients_container, c_actions))
        tabs_view.controls.append(table_card("Virements", virements_container, v_actions))
    if is_admin: 
        tabs_view.controls.append(
            ft.Column([
                table_card("Audit", audit_container, None),
                ft.Container(padding=ft.padding.only(left=20, right=20, bottom=20), content=audit_stats_container)
            ], expand=True)
        )

    header = ft.Container(content=ft.Row([ft.Text("BankApp Control", size=20, weight="bold"), ft.Row([ft.IconButton(ft.Icons.REFRESH, on_click=refresh_data), ft.IconButton(ft.Icons.LOGOUT, on_click=on_logout)])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=20, border=ft.border.only(bottom=ft.BorderSide(1, BORDER)))

    layout = ft.Column([header, ft.Tabs(length=len(tabs_header.tabs), content=ft.Column([tabs_header, tabs_view], expand=True), expand=True)], expand=True, spacing=0)
    
    await refresh_data()
    return ft.View(route="/dashboard", bgcolor=BG, padding=0, controls=[layout])
