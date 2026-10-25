import math
from typing import Optional
import flet as ft
from constants import ACCENT
from utils.theme import ThemeColors

class PaginationComponent:
    def __init__(self, on_prev, on_next, page: Optional[ft.Page] = None):
        self.page = page
        self.on_prev_fn = on_prev
        self.on_next_fn = on_next
        self.is_prev_disabled = True
        self.is_next_disabled = False
        is_dark = page.theme_mode == ft.ThemeMode.DARK if page else True
        self.colors = ThemeColors(is_dark=is_dark)

        # Page Number Info inside a tactile recessed badge
        self.page_info = ft.Text(
            "Page 1",
            size=12.5,
            weight=ft.FontWeight.BOLD,
            color=self.colors.accent_primary
        )

        self.page_badge = ft.Container(
            content=self.page_info,
            padding=ft.Padding(left=14, right=14, top=6, bottom=6),
            border_radius=12,
            bgcolor=self.colors.pressed_surface,
            shadow=self.colors.pressed_shadow(depth=1, blur=2),
            alignment=ft.Alignment.CENTER,
        )

        # Prev Button Container (matching parent wrap card color)
        card_bg = "#FFFFFF" if not is_dark else self.colors.card_surface
        self.prev_text = ft.Text(
            "← Prev",
            size=12.5,
            weight=ft.FontWeight.BOLD,
            color=self.colors.accent_primary
        )
        self.prev_btn = ft.Container(
            content=self.prev_text,
            padding=ft.Padding(left=16, right=16, top=8, bottom=8),
            border_radius=16,
            bgcolor=card_bg,
            border=None,
            shadow=self.colors.subtle_shadow(depth=1, blur=2),
            alignment=ft.Alignment.CENTER,
            on_click=self._handle_prev,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )

        # Next Button Container (matching parent wrap card color)
        self.next_text = ft.Text(
            "Next →",
            size=12.5,
            weight=ft.FontWeight.BOLD,
            color=self.colors.accent_primary
        )
        self.next_btn = ft.Container(
            content=self.next_text,
            padding=ft.Padding(left=16, right=16, top=8, bottom=8),
            border_radius=16,
            bgcolor=card_bg,
            border=None,
            shadow=self.colors.subtle_shadow(depth=1, blur=2),
            alignment=ft.Alignment.CENTER,
            on_click=self._handle_next,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )

        # Inner pagination controls row
        self.pagination_row = ft.Row(
            controls=[self.prev_btn, self.page_badge, self.next_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            tight=True,
        )

        # Tactile Neumorphic Wrap Card (induk wrap)
        self.card = ft.Container(
            content=self.pagination_row,
            bgcolor=card_bg,
            border_radius=22,
            padding=ft.Padding(left=16, right=16, top=10, bottom=10),
            shadow=self.colors.raised_shadow(),
            animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT),
            visible=False,
        )

        # Centered container matching page flow
        self.container = ft.Container(
            content=self.card,
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding(left=0, top=16, right=0, bottom=36),
        )

    def _handle_prev(self, e):
        if not self.is_prev_disabled and callable(self.on_prev_fn):
            self.on_prev_fn(e)

    def _handle_next(self, e):
        if not self.is_next_disabled and callable(self.on_next_fn):
            self.on_next_fn(e)

    def set_visible(self, visible: bool):
        self.card.visible = visible
        self.pagination_row.visible = visible

    def update_theme(self, is_dark: bool):
        self.colors = ThemeColors(is_dark=is_dark)
        card_bg = "#FFFFFF" if not is_dark else self.colors.card_surface
        self.card.bgcolor = card_bg
        self.card.border = None
        self.card.shadow = self.colors.raised_shadow()

        self.prev_btn.bgcolor = card_bg
        self.prev_text.color = self.colors.accent_primary
        self.prev_btn.shadow = [] if self.is_prev_disabled else self.colors.subtle_shadow(depth=1, blur=2)

        self.next_btn.bgcolor = card_bg
        self.next_text.color = self.colors.accent_primary
        self.next_btn.shadow = [] if self.is_next_disabled else self.colors.subtle_shadow(depth=1, blur=2)

        self.page_badge.bgcolor = self.colors.pressed_surface
        self.page_badge.shadow = self.colors.pressed_shadow(depth=1, blur=2)
        self.page_info.color = self.colors.accent_primary

    def update_state(self, current_page: int, total_items: int, items_per_page: int, text_muted_color: str = None):
        total_pages = max(1, math.ceil(total_items / items_per_page))
        self.page_info.value = f"Page {current_page} of {total_pages}"

        if self.page:
            is_dark = self.page.theme_mode == ft.ThemeMode.DARK
            self.update_theme(is_dark)

        self.is_prev_disabled = (current_page == 1)
        self.is_next_disabled = (current_page >= total_pages)

        self.prev_btn.opacity = 0.35 if self.is_prev_disabled else 1.0
        self.prev_btn.shadow = [] if self.is_prev_disabled else self.colors.subtle_shadow(depth=1, blur=2)

        self.next_btn.opacity = 0.35 if self.is_next_disabled else 1.0
        self.next_btn.shadow = [] if self.is_next_disabled else self.colors.subtle_shadow(depth=1, blur=2)
