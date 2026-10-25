from typing import List, Optional
import flet as ft
from constants import (
    DARK_BG, DARK_CARD, DARK_TEXT_MAIN, DARK_TEXT_MUTED,
    LIGHT_BG, LIGHT_CARD, LIGHT_TEXT_MAIN, LIGHT_TEXT_MUTED,
    ACCENT
)

class ThemeColors:
    """Color tokens and shadow generators for active theme (from my-life palette)."""

    def __init__(self, is_dark: bool):
        self.is_dark = is_dark

        if is_dark:
            # Dark Theme: Deep nocturnal blue-green / dark teal
            self.bg_main = "#071A20"
            self.card_surface = "#0A2028"      # Calm, velvety 1-step elevated surface
            self.card_elevated = "#0E2A34"
            self.pressed_surface = "#041217"   # Inset groove
            self.text_primary = "#FFFFFF"      # All primary text is WHITE in dark mode
            self.text_secondary = "#CBD5E1"    # Secondary text is soft WHITE
            self.icon_neutral = "#0D9488"
            self.accent_primary = "#0D9488"     # Jiwa Green
            self.accent_secondary = "#14B8A6"   # Subtle sky/teal accent
            self.border_subtle = "#0E2833"
            self.shadow_bright = ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
            self.shadow_dark = "#030C0F"        # Gentle diffused ambient drop
            self.progress_track = "#041217"
            self.nav_bg = "#0A2028"
        else:
            # Light Theme: Pure Clean Monochromatic Neumorphism without glare
            self.bg_main = "#F5F7FA"
            self.card_surface = "#FFFFFF"      # Crisp White card surface
            self.card_elevated = "#FFFFFF"     # Crisp White elevated card surface
            self.pressed_surface = "#EAEFF4"   # Soft recessed groove fill
            self.text_primary = "#0D9488"      # Crisp Jiwa Green
            self.text_secondary = "#0D9488"
            self.icon_neutral = "#0D9488"
            self.accent_primary = "#0D9488"
            self.accent_secondary = "#14B8A6"
            self.border_subtle = "#D1DAE5"
            self.shadow_bright = "#FFFFFF"
            self.shadow_dark = "#B8C5D6"
            self.progress_track = "#E2E8F0"
            self.nav_bg = "#FFFFFF"

    def raised_shadow(self, depth: Optional[int] = None, blur: Optional[int] = None) -> List[ft.BoxShadow]:
        """Soft opposing neumorphic dual shadows (Thin top-left light x bottom-right shadow)."""
        if self.is_dark:
            d = min(depth, 2) if depth is not None else 1
            b = min(blur, 6) if blur is not None else 4
            return [
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=b,
                    color=self.shadow_bright,
                    offset=ft.Offset(-d, -d),
                ),
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=b + 2,
                    color=self.shadow_dark,
                    offset=ft.Offset(d + 1, d + 1),
                ),
            ]
        else:
            d = depth if depth is not None else 2
            b = blur if blur is not None else 5
            return [
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=b,
                    color="#FFFFFF",
                    offset=ft.Offset(-d, -d),
                ),
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=b,
                    color=self.shadow_dark,
                    offset=ft.Offset(d, d),
                ),
            ]

    def subtle_shadow(self, depth: Optional[int] = None, blur: Optional[int] = None) -> List[ft.BoxShadow]:
        """Subtle dual shadows for buttons, chips, and small controls (Thin top-left light x bottom-right shadow)."""
        if self.is_dark:
            d = depth if depth is not None else 1
            b = blur if blur is not None else 3
            return [
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=b,
                    color=self.shadow_bright,
                    offset=ft.Offset(-d, -d),
                ),
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=b + 1,
                    color=self.shadow_dark,
                    offset=ft.Offset(d, d),
                ),
            ]
        else:
            d = depth if depth is not None else 1
            b = blur if blur is not None else 3
            return [
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=2,
                    color="#FFFFFF",
                    offset=ft.Offset(-1, -1),
                ),
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=b + 1,
                    color=self.shadow_dark,
                    offset=ft.Offset(d + 0.5, d + 1),
                ),
            ]

    def pressed_shadow(
        self,
        depth: Optional[int] = None,
        blur: Optional[int] = None,
        spread: Optional[int] = None,
    ) -> List[ft.BoxShadow]:
        """Subtle dual bevel shadow for inset / recessed controls."""
        d = depth if depth is not None else 1
        b = blur if blur is not None else 3
        s = spread if spread is not None else 0
        if self.is_dark:
            return [
                ft.BoxShadow(
                    spread_radius=s,
                    blur_radius=b,
                    color=self.shadow_bright,
                    offset=ft.Offset(-d, -d),
                ),
                ft.BoxShadow(
                    spread_radius=s,
                    blur_radius=b + 1,
                    color=self.shadow_dark,
                    offset=ft.Offset(d, d),
                ),
            ]
        else:
            return [
                ft.BoxShadow(
                    spread_radius=s,
                    blur_radius=b,
                    color="#FFFFFF",
                    offset=ft.Offset(-d, -d),
                ),
                ft.BoxShadow(
                    spread_radius=s,
                    blur_radius=b + 1,
                    color="#C8D2DE",
                    offset=ft.Offset(d, d),
                ),
            ]

    def inner_shadow(
        self,
        depth: Optional[int] = None,
        blur: Optional[int] = None,
        spread: Optional[int] = None,
    ) -> List[ft.BoxShadow]:
        return self.pressed_shadow(depth=depth, blur=blur, spread=spread)


def get_card_bg(page: ft.Page):
    return LIGHT_CARD if page.theme_mode == ft.ThemeMode.LIGHT else DARK_CARD

def get_text_main(page: ft.Page):
    return LIGHT_TEXT_MAIN if page.theme_mode == ft.ThemeMode.LIGHT else DARK_TEXT_MAIN

def get_text_muted(page: ft.Page):
    return LIGHT_TEXT_MUTED if page.theme_mode == ft.ThemeMode.LIGHT else DARK_TEXT_MUTED

def get_modern_gradient(page: ft.Page):
    return ft.LinearGradient(
        begin=ft.Alignment.TOP_LEFT,
        end=ft.Alignment.BOTTOM_RIGHT,
        colors=[
            ft.Colors.with_opacity(0.08, ACCENT) if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.with_opacity(0.15, ACCENT),
            ft.Colors.with_opacity(0.02, ACCENT) if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.with_opacity(0.05, ACCENT),
        ]
    )

def get_modern_border(page: ft.Page):
    border_color = ft.Colors.with_opacity(0.2, ACCENT) if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.with_opacity(0.3, ACCENT)
    return ft.Border.all(1, border_color)
