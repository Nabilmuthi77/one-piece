from typing import Any
import flet as ft
from constants import BASE_IMG_URL
from utils.theme import ThemeColors

def create_character_card(char: dict, is_dark_or_bg: Any, on_click) -> ft.Container:
    """Creates a character card wrapped inside a soft Neumorphic box container."""
    if isinstance(is_dark_or_bg, bool):
        is_dark = is_dark_or_bg
    elif isinstance(is_dark_or_bg, str):
        is_dark = is_dark_or_bg.lower() in ("#071a20", "#0a2028", "#0e2a34", "#0f172a", "#1e293b", "dark")
    else:
        is_dark = True

    colors = ThemeColors(is_dark=is_dark)
    img_src = BASE_IMG_URL + char.get('image', '') if char.get('image') else 'https://via.placeholder.com/400x500?text=No+Image'

    # Inner image wrapper with rounded corners and bottom gradient text overlay
    inner_image_box = ft.Container(
        content=ft.Stack([
            ft.Image(
                src=img_src,
                fit=ft.BoxFit.FIT_WIDTH,
                width=float('inf'),
            ),
            ft.Container(
                left=0, right=0, bottom=0, height=85,
                padding=ft.Padding(top=0, left=12, right=12, bottom=12),
                alignment=ft.Alignment.BOTTOM_CENTER,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_CENTER,
                    end=ft.Alignment.BOTTOM_CENTER,
                    colors=[
                        ft.Colors.TRANSPARENT,
                        ft.Colors.with_opacity(0.80, ft.Colors.BLACK),
                        ft.Colors.BLACK
                    ],
                    stops=[0.0, 0.55, 1.0]
                ),
                content=ft.Text(
                    char.get('name', 'Unknown'),
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS
                )
            )
        ]),
        border_radius=14,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )

    # Outer Neumorphic wrap container matching my-life NeumorphicCard spec
    return ft.Container(
        content=inner_image_box,
        bgcolor=colors.card_surface,
        border_radius=20,
        padding=ft.Padding.all(10),
        shadow=colors.raised_shadow(),
        border=None,
        animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT),
        on_click=lambda e, c=char: on_click(c)
    )


class CharacterGridComponent:
    def __init__(self, initial_cols: int = 4):
        self.masonry_columns = [ft.Column(expand=1, spacing=16) for _ in range(initial_cols)]
        self.grid = ft.Container(
            content=ft.Row(
                controls=self.masonry_columns,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START
            ),
            padding=ft.Padding(20, 8, 20, 20)
        )

    def adjust_columns(self, page_width: float) -> bool:
        cols = 2
        if page_width >= 1200:
            cols = 5
        elif page_width >= 900:
            cols = 4
        elif page_width >= 600:
            cols = 3

        if len(self.masonry_columns) != cols:
            self.masonry_columns.clear()
            for _ in range(cols):
                self.masonry_columns.append(ft.Column(expand=1, spacing=16))
            self.grid.content.controls = self.masonry_columns
            return True
        return False

    def clear(self):
        for col in self.masonry_columns:
            col.controls.clear()

    def add_card(self, col_index: int, card: ft.Container):
        self.masonry_columns[col_index].controls.append(card)
