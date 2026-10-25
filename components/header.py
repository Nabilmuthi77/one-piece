import time
import flet as ft
from constants import ACCENT, STATUS_BAR_SPACER_HEIGHT
from utils.theme import ThemeColors

class HeaderComponent:
    def __init__(self, page: ft.Page, on_toggle_theme, on_search, on_open_settings=None):
        self.page = page
        self.on_toggle_theme = on_toggle_theme
        self.on_search = on_search
        self.on_open_settings = on_open_settings

        is_dark = page.theme_mode == ft.ThemeMode.DARK
        self.colors = ThemeColors(is_dark=is_dark)

        # Quick Theme Capsule Pill (Putih, Gelap, Auto) matching C:\Users\nabil\Documents\My Program\my-life
        self.theme_pref = "dark" if is_dark else "light"
        self.theme_icons = {}
        self.theme_containers = {}

        def make_quick_icon(icon_name: str, val: str, tooltip_text: str):
            is_active = self.theme_pref == val
            icon_ctrl = ft.Icon(
                getattr(ft.Icons, icon_name),
                size=14,
                color="#FFFFFF" if (is_active and not self.colors.is_dark) else self.colors.accent_primary,
                opacity=1.0 if is_active else 0.55,
            )
            self.theme_icons[val] = icon_ctrl

            container = ft.Container(
                content=icon_ctrl,
                padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                border_radius=10,
                bgcolor=self.colors.accent_primary if (is_active and not self.colors.is_dark) else (self.colors.card_surface if is_active else "transparent"),
                shadow=self.colors.subtle_shadow(depth=1, blur=3) if is_active else [],
                tooltip=tooltip_text,
                on_click=lambda e, v=val: self._handle_theme_change(v),
            )
            self.theme_containers[val] = container
            return container

        self.theme_btn = ft.Container(
            content=ft.Row(
                controls=[
                    make_quick_icon("LIGHT_MODE_ROUNDED", "light", "Putih"),
                    make_quick_icon("DARK_MODE_ROUNDED", "dark", "Gelap"),
                    make_quick_icon("BRIGHTNESS_AUTO_ROUNDED", "auto", "Auto"),
                ],
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            height=32,
            border_radius=16,
            padding=ft.Padding(3, 2, 3, 2),
            bgcolor="#FFFFFF" if not self.colors.is_dark else self.colors.pressed_surface,
            border=None,
            shadow=self.colors.subtle_shadow(depth=1, blur=2) if not self.colors.is_dark else self.colors.pressed_shadow(),
            alignment=ft.Alignment.CENTER,
        )

        # Tactile Neumorphic Settings Button right next to theme capsule pill
        self.settings_btn = ft.Container(
            content=ft.Icon(
                ft.Icons.SETTINGS_ROUNDED,
                size=16,
                color=self.colors.accent_primary,
            ),
            width=32,
            height=32,
            border_radius=16,
            bgcolor="#FFFFFF" if not self.colors.is_dark else self.colors.pressed_surface,
            border=None,
            shadow=self.colors.subtle_shadow(depth=1, blur=2) if not self.colors.is_dark else self.colors.pressed_shadow(),
            alignment=ft.Alignment(0, 0),
            tooltip="Pengaturan",
            on_click=lambda e: self.on_open_settings() if self.on_open_settings else None,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )

        # Logo wrapped inside a tactile Neumorphic card with click scale bounce (full width)
        self.logo_image = ft.Image(src="one-piece-logo.png", height=105, fit=ft.BoxFit.CONTAIN)
        self.logo = ft.Container(
            content=self.logo_image,
            width=float("inf"),
            alignment=ft.Alignment.CENTER,
            bgcolor=self.colors.card_surface,
            border_radius=22,
            padding=ft.Padding(26, 12, 26, 12),
            shadow=self.colors.raised_shadow(),
            on_click=self._animate_logo,
            scale=1.0,
            animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT)
        )

        # Neumorphic Search Input field with separated Icon in Row for perfect vertical centering
        self.search_icon = ft.Icon(
            ft.Icons.SEARCH_ROUNDED,
            size=18,
            color=self.colors.accent_primary,
        )

        self.search_input = ft.TextField(
            hint_text="Search characters (Luffy, Zoro, Kaido...)",
            hint_style=ft.TextStyle(color=self.colors.text_secondary, size=13),
            expand=True,
            border=ft.InputBorder.NONE,
            collapsed=True,
            on_submit=lambda e: self.on_search(),
            on_change=lambda e: self.on_search(),
            color=self.colors.text_primary,
            text_size=13,
        )

        # Tactile Neumorphic Search Card container (full width)
        self.search_container = ft.Container(
            content=ft.Row(
                controls=[
                    self.search_icon,
                    self.search_input,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            width=float("inf"),
            height=42,
            border_radius=21,
            bgcolor=self.colors.card_surface,
            shadow=self.colors.raised_shadow(),
            padding=ft.Padding(14, 0, 14, 0),
            alignment=ft.Alignment.CENTER,
            animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT)
        )

        self.container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(expand=True),
                    self.theme_btn,
                    self.settings_btn
                ], alignment=ft.MainAxisAlignment.END, spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                self.logo,
                self.search_container
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            padding=ft.Padding(20, STATUS_BAR_SPACER_HEIGHT, 20, 8),
        )

    def _animate_logo(self, e):
        self.logo.scale = 1.05
        self.logo.update()
        time.sleep(0.15)
        self.logo.scale = 1.0
        self.logo.update()

    def _handle_theme_change(self, val: str):
        self.theme_pref = val
        if callable(self.on_toggle_theme):
            self.on_toggle_theme(val)

    def update_theme(self, theme_mode, card_bg=None, text_main=None, current_pref=None):
        is_dark = theme_mode == ft.ThemeMode.DARK
        self.colors = ThemeColors(is_dark=is_dark)
        if current_pref:
            self.theme_pref = current_pref

        # Update capsule pill container
        self.theme_btn.bgcolor = "#FFFFFF" if not self.colors.is_dark else self.colors.pressed_surface
        self.theme_btn.shadow = (
            self.colors.subtle_shadow(depth=1, blur=2)
            if not self.colors.is_dark
            else self.colors.pressed_shadow()
        )

        # Update quick theme segmented icons (Putih, Gelap, Auto)
        for val, container in self.theme_containers.items():
            is_active = self.theme_pref == val
            icon_ctrl = self.theme_icons.get(val)
            if icon_ctrl:
                icon_ctrl.color = "#FFFFFF" if (is_active and not self.colors.is_dark) else self.colors.accent_primary
                icon_ctrl.opacity = 1.0 if is_active else 0.55

            container.bgcolor = (
                self.colors.accent_primary
                if (is_active and not self.colors.is_dark)
                else (self.colors.card_surface if is_active else "transparent")
            )
            container.shadow = self.colors.subtle_shadow(depth=1, blur=3) if is_active else []

        # Update logo card
        self.logo.bgcolor = self.colors.card_surface
        self.logo.shadow = self.colors.raised_shadow()

        # Update search container & input
        self.search_container.bgcolor = self.colors.card_surface
        self.search_container.shadow = self.colors.raised_shadow()
        self.search_icon.color = self.colors.accent_primary
        self.search_input.color = self.colors.text_primary
        self.search_input.hint_style = ft.TextStyle(color=self.colors.text_secondary, size=13)

        # Update settings button
        self.settings_btn.bgcolor = "#FFFFFF" if not self.colors.is_dark else self.colors.pressed_surface
        self.settings_btn.shadow = (
            self.colors.subtle_shadow(depth=1, blur=2)
            if not self.colors.is_dark
            else self.colors.pressed_shadow()
        )
        self.settings_btn.content.color = self.colors.accent_primary
