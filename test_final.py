import flet as ft

def main(page: ft.Page):
    def close_modal(e):
        print("Closing modal...")
        page.pop_dialog()
        print("Modal closed.")

    def open_modal():
        dlg = ft.AlertDialog(
            content=ft.Container(
                ft.Column([
                    ft.Text("Modal"),
                    ft.ElevatedButton("Go FS", on_click=lambda e: open_fs()),
                    ft.ElevatedButton("Close", on_click=close_modal)
                ])
            )
        )
        page.show_dialog(dlg)

    def open_fs():
        page.pop_dialog()
        fs_view = ft.View(
            route="/fullscreen",
            controls=[
                ft.ElevatedButton("Close FS", on_click=lambda e: close_fs())
            ]
        )
        page.views.append(fs_view)
        page.update()

    def close_fs():
        page.views.pop()
        open_modal()
        page.update()

    page.add(ft.ElevatedButton("Open", on_click=lambda e: open_modal()))

ft.run(main)
