import os
import threading
import flet as ft
from utils.theme import ThemeColors

current_exit_dialog = None

def is_exit_dialog_open() -> bool:
    return current_exit_dialog is not None

def close_exit_dialog(page: ft.Page, e=None):
    global current_exit_dialog
    if current_exit_dialog is not None:
        if hasattr(page, "pop_dialog"):
            page.pop_dialog()
        elif hasattr(page, "close"):
            page.close(current_exit_dialog)
        else:
            current_exit_dialog.open = False
            page.update()
        current_exit_dialog = None

def confirm_exit(page: ft.Page, e=None):
    try:
        page.window.prevent_close = False
        page.window.visible = False
        page.window.update()
        if hasattr(page.window, "destroy"):
            page.run_task(page.window.destroy)
        elif hasattr(page.window, "close"):
            page.run_task(page.window.close)
    except Exception:
        pass
    threading.Timer(0.05, lambda: os._exit(0)).start()

def show_exit_dialog(page: ft.Page):
    global current_exit_dialog
    if current_exit_dialog is not None:
        return

    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = ThemeColors(is_dark=is_dark)

    # Tactile Neumorphic icon box
    exit_icon_box = ft.Container(
        content=ft.Icon(
            ft.Icons.LOGOUT_ROUNDED,
            size=26,
            color="#EF4444",
        ),
        width=52,
        height=52,
        border_radius=16,
        bgcolor=colors.card_surface,
        shadow=colors.subtle_shadow(depth=1, blur=3),
        alignment=ft.Alignment(0, 0),
    )

    # Tactile Neumorphic Cancel button
    cancel_btn = ft.Container(
        content=ft.Text(
            "Cancel",
            size=13,
            weight=ft.FontWeight.W_700,
            color=colors.text_primary,
            text_align=ft.TextAlign.CENTER,
        ),
        padding=ft.Padding(18, 10, 18, 10),
        border_radius=12,
        bgcolor=colors.card_surface,
        shadow=colors.subtle_shadow(depth=1, blur=2),
        alignment=ft.Alignment(0, 0),
        expand=True,
        on_click=lambda e: close_exit_dialog(page, e),
    )

    # Tactile Neumorphic Exit button
    exit_btn = ft.Container(
        content=ft.Text(
            "Exit",
            size=13,
            weight=ft.FontWeight.W_700,
            color="#EF4444",
            text_align=ft.TextAlign.CENTER,
        ),
        padding=ft.Padding(18, 10, 18, 10),
        border_radius=12,
        bgcolor=colors.card_surface,
        shadow=colors.subtle_shadow(depth=1, blur=2),
        alignment=ft.Alignment(0, 0),
        expand=True,
        on_click=lambda e: confirm_exit(page, e),
    )

    # Floating Neumorphic modal card
    modal_card = ft.Container(
        content=ft.Column(
            controls=[
                exit_icon_box,
                ft.Container(height=6),
                ft.Text(
                    "Exit App",
                    size=17,
                    weight=ft.FontWeight.W_800,
                    color=colors.text_primary,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Are you sure you want to exit the application?",
                    size=12.5,
                    weight=ft.FontWeight.W_500,
                    color=colors.text_secondary,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=10),
                ft.Row(
                    controls=[cancel_btn, exit_btn],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=3,
            tight=True,
        ),
        bgcolor=colors.card_surface,
        shadow=colors.raised_shadow(),
        padding=ft.Padding(18, 16, 18, 14),
        border_radius=22,
    )

    current_exit_dialog = ft.AlertDialog(
        content=ft.Container(
            content=modal_card,
            width=300,
            padding=0,
        ),
        content_padding=0,
        bgcolor="transparent",
        shape=ft.RoundedRectangleBorder(radius=22),
        on_dismiss=lambda e: close_exit_dialog(page),
    )
    page.show_dialog(current_exit_dialog)
    page.update()
