from typing import Optional
import flet as ft
from constants import WHATSAPP
from utils.theme import ThemeColors


class FooterComponent:
    def __init__(self, page: Optional[ft.Page] = None):
        self.page = page
        is_dark = page.theme_mode == ft.ThemeMode.DARK if page else True
        self.colors = ThemeColors(is_dark=is_dark)

        (
            self.inline_wave_img,
            self.inline_body,
            self.inline_text,
            self.inline_wa_btn,
            self.inline_wa_text,
            self.footer_inline
        ) = self._build_footer()

        (
            self.fixed_wave_img,
            self.fixed_body,
            self.fixed_text,
            self.fixed_wa_btn,
            self.fixed_wa_text,
            self.footer_fixed
        ) = self._build_footer()

        self.footer_fixed.bottom = 0
        self.footer_fixed.left = 0
        self.footer_fixed.right = 0
        self.footer_fixed.visible = False

    def _build_footer(self):
        wave_src = "wave_dark.svg" if self.colors.is_dark else "wave_white.svg"
        body_bg = self.colors.card_surface
        text_color = self.colors.text_primary
        btn_bg = "#FFFFFF" if not self.colors.is_dark else self.colors.card_elevated

        wave_img = ft.Image(
            src=wave_src,
            fit=ft.BoxFit.FILL,
            width=float('inf'),
            height=60
        )

        wave_container = ft.Container(
            content=wave_img,
            width=float('inf'),
            height=60,
        )

        text = ft.Text(
            "Made for fun by me",
            color=text_color,
            weight=ft.FontWeight.BOLD,
            size=15
        )

        wa_text = ft.Text(
            "Contact me",
            color=self.colors.text_primary,
            weight=ft.FontWeight.BOLD,
            size=13.5
        )

        wa_btn = ft.Container(
            content=ft.Row([
                ft.Image(src="wa_green.svg", width=18, height=18),
                wa_text
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8, tight=True),
            bgcolor=btn_bg,
            padding=ft.Padding(20, 10, 22, 10),
            border_radius=16,
            border=None,
            shadow=self.colors.subtle_shadow(depth=1, blur=4),
            url="https://wa.me/6282258941501",
            tooltip="Hubungi via WhatsApp",
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )

        body_container = ft.Container(
            content=ft.Column([
                text,
                ft.Row([wa_btn], alignment=ft.MainAxisAlignment.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            bgcolor=body_bg,
            padding=ft.Padding(20, 0, 20, 40),
            width=float('inf')
        )

        footer_container = ft.Container(
            content=ft.Column([
                wave_container,
                body_container
            ], spacing=-2),
            width=float('inf')
        )

        return wave_img, body_container, text, wa_btn, wa_text, footer_container

    def update_theme(self, is_dark: bool):
        self.colors = ThemeColors(is_dark=is_dark)
        wave_src = "wave_dark.svg" if is_dark else "wave_white.svg"
        body_bg = self.colors.card_surface
        text_color = self.colors.text_primary
        btn_bg = "#FFFFFF" if not is_dark else self.colors.card_elevated
        btn_shadow = self.colors.subtle_shadow(depth=1, blur=4)

        for wave_img, body_container, text, wa_btn, wa_text in [
            (self.inline_wave_img, self.inline_body, self.inline_text, self.inline_wa_btn, self.inline_wa_text),
            (self.fixed_wave_img, self.fixed_body, self.fixed_text, self.fixed_wa_btn, self.fixed_wa_text),
        ]:
            wave_img.src = wave_src
            body_container.bgcolor = body_bg
            text.color = text_color
            wa_btn.bgcolor = btn_bg
            wa_btn.shadow = btn_shadow
            wa_text.color = self.colors.text_primary

    def update_visibility(self, total_filtered_count: int):
        if total_filtered_count <= 2:
            self.footer_inline.visible = False
            self.footer_fixed.visible = True
        else:
            self.footer_inline.visible = True
            self.footer_fixed.visible = False
