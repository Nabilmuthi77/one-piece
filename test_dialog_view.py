import flet as ft
import asyncio

def main(page: ft.Page):
    dlg = ft.AlertDialog(content=ft.Text("Dialog content"), title=ft.Text("Test"))

    def close_dlg(e):
        dlg.open = False
        page.update()

    dlg.actions = [
        ft.TextButton("Close Modal", on_click=close_dlg)
    ]
    
    def open_fs(e):
        fs_view = ft.View(
            route="/fullscreen",
            controls=[
                ft.Text("Fullscreen View"),
                ft.ElevatedButton("Unlock (Close FS)", on_click=lambda e: close_fs())
            ]
        )
        page.views.append(fs_view)
        page.update()

    def close_fs():
        page.views.pop()
        page.update()

    dlg.content = ft.Column([
        ft.Text("Click below to go fullscreen"),
        ft.ElevatedButton("Go Fullscreen", on_click=open_fs)
    ])

    def open_dlg(e):
        if dlg not in page.overlay:
            page.overlay.append(dlg)
        dlg.open = True
        page.update()
            
    page.add(
        ft.ElevatedButton("Open Modal", on_click=open_dlg)
    )

ft.run(main, port=8001)
