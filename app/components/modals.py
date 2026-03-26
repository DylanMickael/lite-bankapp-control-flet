import flet as ft

def client_modal(title, on_save, ref_nom, ref_solde, on_cancel):
    return ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Column([
            ft.TextField(label="Nom Client", ref=ref_nom, border_radius=10),
            ft.TextField(label="Solde Initial (Ar)", ref=ref_solde, border_radius=10)
        ], height=120, spacing=15, tight=True),
        actions=[
            ft.TextButton("Annuler", on_click=on_cancel),
            ft.ElevatedButton("Enregistrer", bgcolor="#2563eb", color="white", on_click=on_save),
        ],
    )

def virement_modal(title, on_save, ref_nc, ref_amt, on_cancel):
    return ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Column([
            ft.TextField(label="N° Compte", ref=ref_nc, border_radius=10),
            ft.TextField(label="Montant (Ar)", ref=ref_amt, border_radius=10)
        ], height=120, spacing=15, tight=True),
        actions=[
            ft.TextButton("Annuler", on_click=on_cancel),
            ft.ElevatedButton("Valider", bgcolor="#2563eb", color="white", on_click=on_save),
        ],
    )

def confirm_modal(title, message, on_confirm, on_cancel):
    return ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[
            ft.TextButton("Annuler", on_click=on_cancel),
            ft.ElevatedButton("Confirmer", bgcolor="#ef4444", color="white", on_click=on_confirm),
        ],
    )
