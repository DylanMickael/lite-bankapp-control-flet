import flet as ft

def dashboard_modals(
    input_c_nom, input_c_solde, 
    input_v_nc, input_v_amt,
    on_close, on_save_client, on_save_virement, on_delete,
    success_msg_text, on_close_success,
    error_msg_text, on_close_error
):
    ACCENT = "#2563eb"
    ERROR = "#ef4444"
    SUCCESS = "#10b981"

    c_modal = ft.AlertDialog(
        title=ft.Text("Gestion Client"),
        content=ft.Column([input_c_nom, input_c_solde], tight=True, spacing=15),
        actions=[
            ft.TextButton("Annuler", on_click=on_close), 
            ft.ElevatedButton("Enregistrer", bgcolor=ACCENT, color="white", on_click=on_save_client)
        ]
    )
    
    v_modal = ft.AlertDialog(
        title=ft.Text("Gestion Virement"),
        content=ft.Column([input_v_nc, input_v_amt], tight=True, spacing=15),
        actions=[
            ft.TextButton("Annuler", on_click=on_close), 
            ft.ElevatedButton("Confirmer", bgcolor=ACCENT, color="white", on_click=on_save_virement)
        ]
    )

    conf_modal = ft.AlertDialog(
        title=ft.Text("Confirmation"),
        content=ft.Text("Êtes-vous sûr de vouloir supprimer cet élément ?"),
        actions=[
            ft.TextButton("Non", on_click=on_close), 
            ft.ElevatedButton("Oui, Supprimer", bgcolor=ERROR, color="white", on_click=on_delete)
        ]
    )

    success_modal = ft.AlertDialog(
        title=ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color=SUCCESS), ft.Text("Succès")], spacing=10),
        content=success_msg_text,
        actions=[
            ft.TextButton("Fermer", on_click=on_close_success)
        ]
    )

    error_modal = ft.AlertDialog(
        title=ft.Row([ft.Icon(ft.Icons.ERROR_OUTLINE, color=ERROR), ft.Text("Erreur")], spacing=10),
        content=error_msg_text,
        actions=[
            ft.TextButton("Fermer", on_click=on_close_error)
        ]
    )

    return c_modal, v_modal, conf_modal, success_modal, error_modal
