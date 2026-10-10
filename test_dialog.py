import flet as ft

def main(page: ft.Page):
    dlg = ft.AlertDialog(content=ft.Text("Hello"), title=ft.Text("Test"))

    def close_dlg(e):
        dlg.open = False
        page.update()

    dlg.actions = [
        ft.TextButton("Close", on_click=close_dlg)
    ]
    
    def open_dlg(e):
        if dlg not in page.overlay:
            page.overlay.append(dlg)
        dlg.open = True
        page.update()
            
    page.add(
        ft.ElevatedButton("Open", on_click=open_dlg)
    )

ft.run(main)
