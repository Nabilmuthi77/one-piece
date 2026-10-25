import re
import time
from collections import Counter
import flet as ft
from constants import (
    ACCENT, BUTTON_SIZE, VIEWPORT_MARGIN, MENU_GAP, ARC_ORDER
)
from utils.theme import ThemeColors
from utils.helpers import (
    get_devil_fruit_type, get_story_arc, get_character_game_mode,
    matches_df_filter, matches_game_mode_filter
)

class FilterMenuComponent:
    def __init__(self, page: ft.Page, get_all_characters, on_filter_changed):
        self.page = page
        self.get_all_characters = get_all_characters
        self.on_filter_changed = on_filter_changed

        self.selected_category = "arcs"
        self.selected_arc = None
        self.selected_df = None
        self.selected_race = None
        self.selected_mode = None

        self.arc_menu_open = False
        self.is_drag_active = False
        self.drag_dist = 0.0
        self.last_toggle_time = 0.0

        self.race_counts = {}

        # Colors helper
        is_dark = page.theme_mode == ft.ThemeMode.DARK
        self.colors = ThemeColors(is_dark=is_dark)

        # Initial position: bottom-right of viewport
        init_pw = float(page.width if page.width else 400)
        init_ph = float(page.height if page.height else 800)
        self.btn_left = max(float(VIEWPORT_MARGIN), init_pw - BUTTON_SIZE - float(VIEWPORT_MARGIN))
        self.btn_top = max(float(VIEWPORT_MARGIN), init_ph - BUTTON_SIZE - 28.0)

        self.start_pointer_x = 0.0
        self.start_pointer_y = 0.0
        self.start_btn_left = self.btn_left
        self.start_btn_top = self.btn_top

        # Spinners
        self.fab_spinner_normal = ft.Image(
            src="usc_spinner.webp",
            width=22,
            height=22,
            fit=ft.BoxFit.CONTAIN
        )
        self.fab_spinner_active = ft.Image(
            src="usc_cog.webp",
            width=22,
            height=22,
            fit=ft.BoxFit.CONTAIN
        )

        # Inner Center: recessed groove disc
        self.fab_inner_center = ft.Container(
            content=self.fab_spinner_normal,
            width=30,
            height=30,
            border_radius=15,
            bgcolor=self.colors.pressed_surface,
            alignment=ft.Alignment.CENTER,
            shadow=self.colors.pressed_shadow(depth=1, blur=3)
        )

        # Outer Button: 46x46 circular tactile Neumorphic button
        self.arc_fab_container = ft.Container(
            content=self.fab_inner_center,
            width=46,
            height=46,
            border_radius=23,
            bgcolor=self.colors.card_surface,
            border=None,
            shadow=self.colors.raised_shadow(),
            alignment=ft.Alignment.CENTER,
            tooltip="Filter Characters",
            animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT)
        )

        # Gesture Detector
        self.arc_fab_wrapper = ft.GestureDetector(
            content=self.arc_fab_container,
            left=self.btn_left,
            top=self.btn_top,
            drag_interval=10,
            on_pan_start=self._on_pan_start,
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
            on_tap=self._on_tap
        )

        # Backdrop dismiss
        self.arc_dim_dismiss = ft.Container(
            top=0, bottom=0, left=0, right=0,
            bgcolor=ft.Colors.TRANSPARENT,
            visible=False,
            on_click=lambda e: self.close_arc_menu()
        )

        # Active Filters Row & Container
        self.active_filters_row = ft.Row(
            controls=[self._create_default_badge("All Characters")],
            spacing=6,
            scroll=ft.ScrollMode.HIDDEN,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.active_filter_container = ft.Container(
            content=self.active_filters_row,
            height=28,
            expand=True,
            alignment=ft.Alignment.CENTER_LEFT
        )

        # Category labels
        self.category_labels = {
            "arcs": "Story Arcs",
            "devil_fruit": "Devil Fruit",
            "race": "Race",
            "game_mode": "Game Mode",
        }

        # Tactile Neumorphic title badge for "CHARACTER FILTER"
        self.title_text = ft.Text(
            "CHARACTER FILTER",
            size=10,
            weight=ft.FontWeight.BOLD,
            color=self.colors.accent_primary if not self.colors.is_dark else self.colors.text_secondary,
        )

        self.title_badge = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.TUNE_ROUNDED, size=12, color=self.colors.accent_primary),
                self.title_text
            ], tight=True, spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_elevated,
            border_radius=10,
            padding=ft.Padding(8, 0, 8, 0),
            height=28,
            shadow=self.colors.subtle_shadow(depth=1, blur=3),
            border=None if not self.colors.is_dark else ft.Border.all(1, self.colors.border_subtle),
            alignment=ft.Alignment.CENTER
        )

        self.category_label_text = ft.Text(
            self.category_labels["arcs"],
            size=11,
            weight=ft.FontWeight.BOLD,
            color=self.colors.text_primary,
            no_wrap=True
        )

        # Tactile Neumorphic category pill container (white neumorphism)
        self.category_container = ft.Container(
            content=ft.Row([
                self.category_label_text,
                ft.Icon(ft.Icons.ARROW_DROP_DOWN_ROUNDED, size=18, color=self.colors.accent_primary)
            ], tight=True, spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_elevated,
            border=None,
            border_radius=10,
            shadow=self.colors.subtle_shadow(depth=1, blur=3),
            padding=ft.Padding(8, 0, 6, 0),
            height=28,
            alignment=ft.Alignment.CENTER,
        )

        self.category_anchor = ft.Container(
            content=self.category_container,
            padding=ft.Padding(0, 0, 0, 8),
        )

        self.category_dropdown = ft.PopupMenuButton(
            content=self.category_anchor,
            menu_position=ft.PopupMenuPosition.UNDER,
            padding=0,
            menu_padding=ft.Padding(6, 6, 6, 6),
            size_constraints=ft.BoxConstraints(min_width=142, max_width=142),
            bgcolor=ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_surface,
            shape=ft.RoundedRectangleBorder(radius=16),
            elevation=4,
            shadow_color=ft.Colors.BLACK_12 if not self.colors.is_dark else ft.Colors.BLACK_26,
            items=self.build_category_menu_items(),
            tooltip="Select Category",
        )

        # Neumorphic Search Input inside menu matching header search bar spec
        self.arc_search_icon = ft.Icon(
            ft.Icons.SEARCH_ROUNDED,
            size=16,
            color=self.colors.accent_primary,
        )

        self.arc_search_input = ft.TextField(
            hint_text="Search arcs (Wano, Alabasta...)",
            hint_style=ft.TextStyle(color=self.colors.text_secondary, size=12),
            expand=True,
            border=ft.InputBorder.NONE,
            collapsed=True,
            color=self.colors.text_primary,
            text_size=12,
            on_change=lambda e: self.build_filter_list_items(),
        )

        self.arc_search_container = ft.Container(
            content=ft.Row(
                controls=[
                    self.arc_search_icon,
                    self.arc_search_input,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            width=float("inf"),
            height=38,
            border_radius=19,
            bgcolor=self.colors.card_surface,
            shadow=self.colors.raised_shadow(),
            border=None,
            padding=ft.Padding(12, 0, 12, 0),
            margin=ft.Margin(0, 2, 0, 0),
            alignment=ft.Alignment.CENTER,
            animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT),
        )

        self.arc_list_col = ft.Column(spacing=0, scroll=ft.ScrollMode.HIDDEN, expand=True)

        # Header buttons
        self.reset_btn = ft.Container(
            content=ft.Icon(ft.Icons.RESTART_ALT_ROUNDED, size=14, color=self.colors.accent_primary),
            width=28,
            height=28,
            border_radius=14,
            bgcolor=ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_elevated,
            shadow=self.colors.subtle_shadow(depth=1, blur=3),
            alignment=ft.Alignment(0, 0),
            tooltip="Clear Suggest",
            on_click=lambda e: self.clear_all_filters()
        )

        self.close_btn = ft.Container(
            content=ft.Icon(ft.Icons.CLOSE_ROUNDED, size=14, color=self.colors.text_secondary),
            width=28,
            height=28,
            border_radius=14,
            bgcolor=ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_elevated,
            shadow=self.colors.subtle_shadow(depth=1, blur=3),
            alignment=ft.Alignment(0, 0),
            tooltip="Close",
            on_click=lambda e: self.close_arc_menu()
        )

        # Separator line
        self.separator_line = ft.Container(
            height=1,
            bgcolor=self.colors.accent_primary
        )

        # Neumorphic Card container
        self.arc_menu_card = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            self.title_badge,
                            ft.Row([
                                self.reset_btn,
                                self.close_btn
                            ], spacing=5, alignment=ft.CrossAxisAlignment.CENTER)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Row([
                            self.category_dropdown,
                            self.active_filter_container
                        ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.START),
                        self.arc_search_container
                    ], spacing=5),
                    padding=ft.Padding(14, 8, 14, 10)
                ),
                self.separator_line,
                ft.Container(
                    content=self.arc_list_col,
                    expand=True,
                    padding=ft.Padding(8, 2, 8, 8)
                )
            ], spacing=0),
            width=340,
            height=480,
            border_radius=22,
            bgcolor=self.colors.bg_main,
            border=None,
            shadow=self.colors.raised_shadow(depth=6, blur=20),
            left=self.btn_left,
            top=self.btn_top,
            visible=False
        )

    def clamp_button_pos(self, l=None, t=None):
        curr_pw = float(self.page.width if self.page.width else 400)
        curr_ph = float(self.page.height if self.page.height else 800)
        max_left = max(float(VIEWPORT_MARGIN), curr_pw - BUTTON_SIZE - float(VIEWPORT_MARGIN))
        max_top = max(float(VIEWPORT_MARGIN), curr_ph - BUTTON_SIZE - float(VIEWPORT_MARGIN))
        target_l = self.btn_left if l is None else l
        target_t = self.btn_top if t is None else t
        self.btn_left = max(float(VIEWPORT_MARGIN), min(float(target_l), max_left))
        self.btn_top = max(float(VIEWPORT_MARGIN), min(float(target_t), max_top))
        return self.btn_left, self.btn_top

    def set_normal_state(self):
        self.arc_fab_container.bgcolor = self.colors.card_surface
        self.arc_fab_container.shadow = self.colors.raised_shadow()
        self.fab_inner_center.content = self.fab_spinner_normal
        if self.arc_fab_wrapper and self.arc_fab_wrapper.page:
            self.arc_fab_container.update()

    def set_active_state(self):
        self.arc_fab_container.bgcolor = self.colors.card_elevated if self.colors.is_dark else self.colors.card_surface
        self.arc_fab_container.shadow = self.colors.subtle_shadow(depth=2, blur=8)
        self.fab_inner_center.content = self.fab_spinner_active
        if self.arc_fab_wrapper and self.arc_fab_wrapper.page:
            self.arc_fab_container.update()

    def position_arc_menu(self):
        if not self.arc_menu_open:
            return

        curr_pw = float(self.page.width if self.page.width else 1200)
        curr_ph = float(self.page.height if self.page.height else 800)

        menu_width = min(340.0, max(280.0, curr_pw - (VIEWPORT_MARGIN * 2)))
        menu_height = min(480.0, max(320.0, curr_ph - 90))
        self.arc_menu_card.width = menu_width
        self.arc_menu_card.height = menu_height

        btn_r = self.btn_left + BUTTON_SIZE
        btn_b = self.btn_top + BUTTON_SIZE
        btn_cx = self.btn_left + BUTTON_SIZE / 2.0
        btn_cy = self.btn_top + BUTTON_SIZE / 2.0

        candidates = [
            {"left": btn_r + MENU_GAP, "top": btn_cy - menu_height / 2.0},
            {"left": self.btn_left - menu_width - MENU_GAP, "top": btn_cy - menu_height / 2.0},
            {"left": btn_cx - menu_width / 2.0, "top": btn_b + MENU_GAP},
            {"left": btn_cx - menu_width / 2.0, "top": self.btn_top - menu_height - MENU_GAP}
        ]

        def calculate_overflow(pos):
            overflow = 0.0
            if pos["left"] < VIEWPORT_MARGIN:
                overflow += VIEWPORT_MARGIN - pos["left"]
            if pos["left"] + menu_width > curr_pw - VIEWPORT_MARGIN:
                overflow += (pos["left"] + menu_width) - (curr_pw - VIEWPORT_MARGIN)
            if pos["top"] < VIEWPORT_MARGIN:
                overflow += VIEWPORT_MARGIN - pos["top"]
            if pos["top"] + menu_height > curr_ph - VIEWPORT_MARGIN:
                overflow += (pos["top"] + menu_height) - (curr_ph - VIEWPORT_MARGIN)
            return overflow

        best_pos = min(candidates, key=calculate_overflow)

        final_left = max(float(VIEWPORT_MARGIN), min(float(best_pos["left"]), curr_pw - menu_width - float(VIEWPORT_MARGIN)))
        final_top = max(float(VIEWPORT_MARGIN), min(float(best_pos["top"]), curr_ph - menu_height - float(VIEWPORT_MARGIN)))

        self.arc_menu_card.left = final_left
        self.arc_menu_card.top = final_top
        self.arc_menu_card.right = None
        self.arc_menu_card.bottom = None

    def open_arc_menu(self):
        self.arc_menu_open = True
        self.arc_dim_dismiss.visible = True
        self.arc_menu_card.visible = True
        self.set_active_state()
        self.position_arc_menu()
        self.update_active_filter_display()
        self.page.update()

    def close_arc_menu(self):
        self.arc_menu_open = False
        self.arc_dim_dismiss.visible = False
        self.arc_menu_card.visible = False
        self.set_normal_state()
        self.page.update()

    def toggle_arc_menu(self):
        if self.arc_menu_open:
            self.close_arc_menu()
        else:
            self.open_arc_menu()

    def _trigger_toggle(self, e=None):
        now = time.time()
        if now - self.last_toggle_time < 0.20:
            return
        self.last_toggle_time = now
        self.toggle_arc_menu()

    @staticmethod
    def _get_pos_coord(val):
        if val is None:
            return None
        if hasattr(val, 'x') and hasattr(val, 'y'):
            return float(val.x), float(val.y)
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            return float(val[0]), float(val[1])
        return None

    def _on_pan_start(self, e: ft.DragStartEvent):
        self.is_drag_active = False
        self.drag_dist = 0.0
        self.start_btn_left = self.btn_left
        self.start_btn_top = self.btn_top
        coords = self._get_pos_coord(getattr(e, 'global_position', None)) or self._get_pos_coord(getattr(e, 'local_position', None))
        if coords:
            self.start_pointer_x, self.start_pointer_y = coords
        else:
            self.start_pointer_x, self.start_pointer_y = 0.0, 0.0

    def _on_pan_update(self, e: ft.DragUpdateEvent):
        curr_coords = self._get_pos_coord(getattr(e, 'global_position', None))
        if curr_coords and (self.start_pointer_x != 0.0 or self.start_pointer_y != 0.0):
            offset_x = curr_coords[0] - self.start_pointer_x
            offset_y = curr_coords[1] - self.start_pointer_y
        else:
            delta = self._get_pos_coord(getattr(e, 'global_delta', None)) or self._get_pos_coord(getattr(e, 'local_delta', None))
            if delta:
                offset_x, offset_y = delta[0], delta[1]
            else:
                offset_x, offset_y = 0.0, 0.0

        self.drag_dist = (offset_x ** 2 + offset_y ** 2) ** 0.5

        if self.drag_dist > 4.0:
            if not self.is_drag_active:
                self.is_drag_active = True
                if self.arc_menu_open:
                    self.close_arc_menu()

        if self.is_drag_active:
            self.clamp_button_pos(self.start_btn_left + offset_x, self.start_btn_top + offset_y)
            self.arc_fab_wrapper.left = self.btn_left
            self.arc_fab_wrapper.top = self.btn_top
            if self.arc_fab_wrapper.page:
                self.arc_fab_wrapper.update()

    def _on_pan_end(self, e: ft.DragEndEvent):
        if not self.is_drag_active:
            self._trigger_toggle()
        self.is_drag_active = False

    def _on_tap(self, e):
        if not self.is_drag_active:
            self._trigger_toggle()

    def _create_filter_badge(self, text, on_clear_fn):
        return ft.Container(
            content=ft.Row([
                ft.Text(
                    text,
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors.accent_primary,
                    no_wrap=True
                ),
                ft.Icon(
                    ft.Icons.CLOSE_ROUNDED,
                    size=13,
                    color=self.colors.accent_primary
                )
            ], tight=True, spacing=4, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_elevated,
            border=None,
            shadow=self.colors.subtle_shadow(depth=1, blur=3),
            border_radius=10,
            padding=ft.Padding(8, 0, 6, 0),
            height=28,
            alignment=ft.Alignment.CENTER,
            tooltip=f"Delete {text}",
            on_click=on_clear_fn
        )

    def _create_default_badge(self, text, on_click_fn=None):
        return ft.Container(
            content=ft.Text(
                text,
                size=11,
                weight=ft.FontWeight.BOLD,
                color=self.colors.accent_primary,
                no_wrap=True
            ),
            bgcolor=ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_elevated,
            border=None,
            shadow=self.colors.subtle_shadow(depth=1, blur=3),
            border_radius=10,
            padding=ft.Padding(8, 0, 8, 0),
            height=28,
            alignment=ft.Alignment.CENTER,
            tooltip=text,
            on_click=on_click_fn
        )

    def clear_arc_filter(self, e=None):
        self.selected_arc = None
        self.update_active_filter_display()
        self.build_filter_list_items()
        self.on_filter_changed()

    def clear_df_filter(self, e=None):
        self.selected_df = None
        self.update_active_filter_display()
        self.build_filter_list_items()
        self.on_filter_changed()

    def clear_race_filter(self, e=None):
        self.selected_race = None
        self.update_active_filter_display()
        self.build_filter_list_items()
        self.on_filter_changed()

    def clear_mode_filter(self, e=None):
        self.selected_mode = None
        self.update_active_filter_display()
        self.build_filter_list_items()
        self.on_filter_changed()

    def clear_all_filters(self, e=None):
        self.selected_arc = None
        self.selected_df = None
        self.selected_race = None
        self.selected_mode = None
        self.update_active_filter_display()
        self.build_filter_list_items()
        self.on_filter_changed()

    def update_active_filter_display(self):
        self.active_filters_row.controls.clear()

        if self.selected_category == "arcs":
            if self.selected_arc:
                self.active_filters_row.controls.append(self._create_filter_badge(self.selected_arc, self.clear_arc_filter))
            else:
                self.active_filters_row.controls.append(self._create_default_badge("All Characters", lambda e: self.clear_arc_filter(e)))
        elif self.selected_category == "devil_fruit":
            if self.selected_df:
                df_name = "No Fruit" if self.selected_df == "None" else self.selected_df
                self.active_filters_row.controls.append(self._create_filter_badge(df_name, self.clear_df_filter))
            else:
                self.active_filters_row.controls.append(self._create_default_badge("All Characters", lambda e: self.clear_df_filter(e)))
        elif self.selected_category == "race":
            if self.selected_race:
                self.active_filters_row.controls.append(self._create_filter_badge(self.selected_race, self.clear_race_filter))
            else:
                self.active_filters_row.controls.append(self._create_default_badge("All Characters", lambda e: self.clear_race_filter(e)))
        elif self.selected_category == "game_mode":
            if self.selected_mode:
                self.active_filters_row.controls.append(self._create_filter_badge(self.selected_mode, self.clear_mode_filter))
            else:
                self.active_filters_row.controls.append(self._create_default_badge("All Characters", lambda e: self.clear_mode_filter(e)))

        if self.selected_category != "arcs" and self.selected_arc:
            self.active_filters_row.controls.append(self._create_filter_badge(self.selected_arc, self.clear_arc_filter))

        if self.selected_category != "devil_fruit" and self.selected_df:
            df_name = "No Fruit" if self.selected_df == "None" else self.selected_df
            self.active_filters_row.controls.append(self._create_filter_badge(df_name, self.clear_df_filter))

        if self.selected_category != "race" and self.selected_race:
            self.active_filters_row.controls.append(self._create_filter_badge(self.selected_race, self.clear_race_filter))

        if self.selected_category != "game_mode" and self.selected_mode:
            self.active_filters_row.controls.append(self._create_filter_badge(self.selected_mode, self.clear_mode_filter))

        try:
            if self.active_filter_container.page:
                self.active_filter_container.update()
        except Exception:
            pass

    def build_category_menu_items(self):
        categories = [
            ("arcs", "Story Arcs", ft.Icons.AUTO_AWESOME_ROUNDED),
            ("devil_fruit", "Devil Fruit", ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED),
            ("race", "Race", ft.Icons.PEOPLE_ALT_ROUNDED),
            ("game_mode", "Game Mode", ft.Icons.SPEED_ROUNDED),
        ]

        items = []
        for cat_key, label, icon in categories:
            is_selected = self.selected_category == cat_key

            if self.colors.is_dark:
                card_bg = self.colors.card_elevated if is_selected else self.colors.card_surface
                card_border = ft.Border.all(1.5, self.colors.accent_primary) if is_selected else None
                card_shadow = [
                    ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=3,
                        color=self.colors.shadow_bright,
                        offset=ft.Offset(-1, -1),
                    ),
                    ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color=self.colors.shadow_dark,
                        offset=ft.Offset(1.5, 2),
                    ),
                ]
                text_color = self.colors.accent_primary if is_selected else self.colors.text_primary
                icon_color = self.colors.accent_primary if is_selected else self.colors.icon_neutral
            else:
                card_bg = "#F0FDFA" if is_selected else ft.Colors.WHITE
                card_border = ft.Border.all(1.5, self.colors.accent_primary) if is_selected else None
                card_shadow = [
                    ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=3,
                        color="#FFFFFF",
                        offset=ft.Offset(-1, -1),
                    ),
                    ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color=self.colors.shadow_dark,
                        offset=ft.Offset(1.5, 2),
                    ),
                ]
                text_color = self.colors.accent_primary if is_selected else self.colors.text_primary
                icon_color = self.colors.accent_primary

            card = ft.Container(
                content=ft.Row([
                    ft.Icon(icon, size=14, color=icon_color),
                    ft.Text(label, size=11.5, weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.W_500, color=text_color, expand=True),
                    ft.Icon(ft.Icons.CHECK_ROUNDED, size=13, color=self.colors.accent_primary, visible=is_selected),
                ], spacing=6, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=card_bg,
                border=card_border,
                shadow=card_shadow,
                border_radius=11,
                padding=ft.Padding(10, 6, 10, 6),
                width=130,
                animate=ft.Animation(140, ft.AnimationCurve.EASE_OUT),
            )

            items.append(
                ft.PopupMenuItem(
                    content=card,
                    padding=ft.Padding(0, 1, 0, 1),
                    height=34,
                    on_click=lambda e, k=cat_key: self.on_category_select(k),
                )
            )

        return items

    def on_category_select(self, cat_key):
        self.selected_category = cat_key
        self.category_label_text.value = self.category_labels.get(cat_key, "Category")
        self.arc_search_input.value = ""
        if self.selected_category == "arcs":
            self.arc_search_input.hint_text = "Search arcs (Wano, Alabasta...)"
        elif self.selected_category == "devil_fruit":
            self.arc_search_input.hint_text = "Search fruit (Zoan, Logia, Mera...)"
        elif self.selected_category == "race":
            self.arc_search_input.hint_text = "Search race (Human, Fish-man, Mink...)"
        elif self.selected_category == "game_mode":
            self.arc_search_input.hint_text = "Search mode (Easy, Medium, Hard...)"
        self.category_dropdown.items = self.build_category_menu_items()
        self.update_active_filter_display()
        self.build_filter_list_items()
        self.page.update()

    def select_filter(self, category, item_value):
        if category == "arcs":
            self.selected_arc = item_value
        elif category == "devil_fruit":
            self.selected_df = item_value
        elif category == "race":
            self.selected_race = item_value
        elif category == "game_mode":
            self.selected_mode = item_value

        self.update_active_filter_display()
        self.build_filter_list_items()
        self.on_filter_changed()

    def make_filter_item(self, title, count, is_selected, on_click_fn, icon=ft.Icons.AUTO_AWESOME_ROUNDED, badge_label=None, badge_color=None):
        accent_col = badge_color or self.colors.accent_primary
        title_controls = [
            ft.Text(
                title,
                size=13,
                weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.W_500,
                color=self.colors.accent_primary if is_selected else self.colors.text_primary,
                overflow=ft.TextOverflow.ELLIPSIS,
                max_lines=1
            )
        ]
        if badge_label:
            title_controls.append(
                ft.Container(
                    content=ft.Text(badge_label, size=9, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    bgcolor=accent_col,
                    shadow=self.colors.subtle_shadow(depth=1, blur=2),
                    padding=ft.Padding(6, 2, 6, 2),
                    border_radius=10
                )
            )

        # Neumorphic tactile icon box for filter item
        icon_box = ft.Container(
            content=ft.Icon(
                icon,
                size=16,
                color=ft.Colors.WHITE if is_selected else self.colors.accent_primary
            ),
            width=32,
            height=32,
            border_radius=10,
            bgcolor=self.colors.accent_primary if is_selected else self.colors.pressed_surface,
            shadow=self.colors.subtle_shadow(depth=1, blur=2) if not is_selected else None,
            alignment=ft.Alignment.CENTER
        )

        item_bgcolor = (
            (self.colors.card_elevated if is_selected else self.colors.card_surface)
            if self.colors.is_dark
            else ("#F0FDFA" if is_selected else ft.Colors.WHITE)
        )
        item_border = (
            ft.Border.all(1.5, self.colors.accent_primary)
            if is_selected
            else None
        )
        item_shadow = (
            self.colors.subtle_shadow(depth=2, blur=5)
            if is_selected
            else self.colors.subtle_shadow(depth=1, blur=3)
        )

        return ft.Container(
            content=ft.Row([
                icon_box,
                ft.Column([
                    ft.Row(title_controls, spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Text(
                        f"Total {count} characters (No filter)" if title in ("All Characters", "All Character") else (f"{count} character" if count == 1 else f"{count} characters"),
                        size=10,
                        color=self.colors.text_secondary
                    )
                ], spacing=2, expand=True),
                ft.Icon(ft.Icons.CHECK_ROUNDED, color=self.colors.accent_primary, size=16, visible=is_selected)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=item_bgcolor,
            border=item_border,
            shadow=item_shadow,
            border_radius=12,
            padding=ft.Padding(10, 8, 10, 8),
            margin=ft.Margin(left=6, top=2, right=6, bottom=2),
            on_click=on_click_fn,
            animate=ft.Animation(140, ft.AnimationCurve.EASE_OUT)
        )

    def build_filter_list_items(self):
        self.arc_list_col.controls.clear()
        # Top spacer prevents top shadow from being clipped by scroll viewport
        self.arc_list_col.controls.append(ft.Container(height=4))
        search_filter = (self.arc_search_input.value or "").strip().lower()
        all_characters = self.get_all_characters()

        if self.selected_category == "arcs":
            base_pool = [
                c for c in all_characters
                if (not self.selected_race or (c.get('race') or 'Unknown').strip() == self.selected_race)
                and matches_df_filter(c, self.selected_df)
                and matches_game_mode_filter(c, self.selected_mode)
            ]
            dynamic_arc_counts = Counter(get_story_arc(c.get('first_appearance_arc')) for c in base_pool)

            if not search_filter or any(kw in search_filter for kw in ["all", "character", "semua"]):
                is_all_selected = self.selected_arc is None
                self.arc_list_col.controls.append(
                    self.make_filter_item(
                        "All Characters",
                        len(base_pool),
                        is_all_selected,
                        lambda e: self.select_filter("arcs", None),
                        icon=ft.Icons.PEOPLE_ALT_ROUNDED
                    )
                )

            for arc in ARC_ORDER:
                if search_filter and search_filter not in arc.lower():
                    continue
                count = dynamic_arc_counts.get(arc, 0)
                is_selected = self.selected_arc == arc
                self.arc_list_col.controls.append(
                    self.make_filter_item(
                        arc,
                        count,
                        is_selected,
                        lambda e, a=arc: self.select_filter("arcs", a),
                        icon=ft.Icons.AUTO_AWESOME_ROUNDED
                    )
                )

        elif self.selected_category == "devil_fruit":
            base_pool = [
                c for c in all_characters
                if (not self.selected_arc or get_story_arc(c.get('first_appearance_arc')) == self.selected_arc)
                and (not self.selected_race or (c.get('race') or 'Unknown').strip() == self.selected_race)
                and matches_game_mode_filter(c, self.selected_mode)
            ]

            if not search_filter or any(kw in search_filter for kw in ["all", "character", "semua"]):
                is_all_selected = self.selected_df is None
                self.arc_list_col.controls.append(
                    self.make_filter_item(
                        "All Characters",
                        len(base_pool),
                        is_all_selected,
                        lambda e: self.select_filter("devil_fruit", None),
                        icon=ft.Icons.PEOPLE_ALT_ROUNDED
                    )
                )

            fruit_types = [
                ("Zoan", sum(1 for c in base_pool if matches_df_filter(c, 'Zoan')), ft.Icons.PETS_ROUNDED),
                ("Paramecia", sum(1 for c in base_pool if matches_df_filter(c, 'Paramecia')), ft.Icons.AUTO_AWESOME_ROUNDED),
                ("Logia", sum(1 for c in base_pool if matches_df_filter(c, 'Logia')), ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED),
                ("None", sum(1 for c in base_pool if matches_df_filter(c, 'None')), ft.Icons.SHIELD_OUTLINED),
            ]

            clean_sf = re.sub(r'[\s\-_]+', '', search_filter)
            for key, count, icon in fruit_types:
                title = "No Devil Fruit" if key == "None" else f"{key} Type"
                if search_filter and (search_filter not in key.lower() and search_filter not in title.lower() and (not clean_sf or clean_sf not in re.sub(r'[\s\-_]+', '', title.lower()))):
                    continue
                is_selected = self.selected_df == key
                self.arc_list_col.controls.append(
                    self.make_filter_item(
                        title,
                        count,
                        is_selected,
                        lambda e, k=key: self.select_filter("devil_fruit", k),
                        icon=icon
                    )
                )

            df_pool_fruits = []
            for c in base_pool:
                raw = c.get('devil_fruit')
                items = raw if isinstance(raw, list) else ([raw] if raw else [])
                for it in items:
                    clean = re.sub(r'\s*\([^)]*awakened[^)]*\)', '', str(it), flags=re.IGNORECASE).strip()
                    if clean and clean.lower() not in ['none', 'unknown']:
                        df_pool_fruits.append(clean)
            dynamic_df_fruit_counts = Counter(df_pool_fruits)

            if search_filter:
                clean_sf = re.sub(r'[\s\-_]+', '', search_filter)
                sorted_fruits = sorted(dynamic_df_fruit_counts.items(), key=lambda x: (-x[1], x[0]))
                matching_fruits = [
                    (fn, cnt) for fn, cnt in sorted_fruits
                    if search_filter in fn.lower() or (clean_sf and clean_sf in re.sub(r'[\s\-_]+', '', fn.lower()))
                ]

                if matching_fruits:
                    self.arc_list_col.controls.append(
                        ft.Container(
                            content=ft.Text("SPECIFIC FRUITS", size=10, weight=ft.FontWeight.BOLD, color=self.colors.text_secondary),
                            padding=ft.Padding(6, 8, 6, 2)
                        )
                    )
                    for fn, cnt in matching_fruits[:50]:
                        is_selected = self.selected_df == fn
                        f_type = get_devil_fruit_type(fn)
                        self.arc_list_col.controls.append(
                            self.make_filter_item(
                                fn,
                                cnt,
                                is_selected,
                                lambda e, f_name=fn: self.select_filter("devil_fruit", f_name),
                                icon=ft.Icons.AUTO_AWESOME_OUTLINED,
                                badge_label=f_type.upper() if f_type else None
                            )
                        )
            elif self.selected_df and self.selected_df not in ['Zoan', 'Paramecia', 'Logia', 'None']:
                f_type = get_devil_fruit_type(self.selected_df)
                cnt = dynamic_df_fruit_counts.get(self.selected_df, 0)
                self.arc_list_col.controls.append(
                    ft.Container(
                        content=ft.Text("ACTIVE SPECIFIC FRUIT", size=10, weight=ft.FontWeight.BOLD, color=self.colors.text_secondary),
                        padding=ft.Padding(6, 8, 6, 2)
                    )
                )
                self.arc_list_col.controls.append(
                    self.make_filter_item(
                        self.selected_df,
                        cnt,
                        True,
                        lambda e, f_name=self.selected_df: self.select_filter("devil_fruit", f_name),
                        icon=ft.Icons.AUTO_AWESOME_OUTLINED,
                        badge_label=f_type.upper() if f_type else None
                    )
                )

        elif self.selected_category == "race":
            base_pool = [
                c for c in all_characters
                if (not self.selected_arc or get_story_arc(c.get('first_appearance_arc')) == self.selected_arc)
                and matches_df_filter(c, self.selected_df)
                and matches_game_mode_filter(c, self.selected_mode)
            ]
            dynamic_race_counts = Counter((c.get('race') or 'Unknown').strip() for c in base_pool)

            if not search_filter or any(kw in search_filter for kw in ["all", "character", "semua"]):
                is_all_selected = self.selected_race is None
                self.arc_list_col.controls.append(
                    self.make_filter_item(
                        "All Characters",
                        len(base_pool),
                        is_all_selected,
                        lambda e: self.select_filter("race", None),
                        icon=ft.Icons.PEOPLE_ALT_ROUNDED
                    )
                )

            all_known_races = sorted(self.race_counts.keys())
            sorted_races = sorted(all_known_races, key=lambda r: (-dynamic_race_counts.get(r, 0), r))

            for r_name in sorted_races:
                if not r_name or r_name == "Unknown":
                    continue
                count = dynamic_race_counts.get(r_name, 0)
                if search_filter and search_filter not in r_name.lower():
                    continue
                is_selected = self.selected_race == r_name
                self.arc_list_col.controls.append(
                    self.make_filter_item(
                        r_name,
                        count,
                        is_selected,
                        lambda e, r=r_name: self.select_filter("race", r),
                        icon=ft.Icons.PERSON_ROUNDED
                    )
                )

        elif self.selected_category == "game_mode":
            base_pool = [
                c for c in all_characters
                if (not self.selected_arc or get_story_arc(c.get('first_appearance_arc')) == self.selected_arc)
                and matches_df_filter(c, self.selected_df)
                and (not self.selected_race or (c.get('race') or 'Unknown').strip() == self.selected_race)
            ]

            if not search_filter or any(kw in search_filter for kw in ["all", "character", "semua", "mode"]):
                is_all_selected = self.selected_mode is None
                self.arc_list_col.controls.append(
                    self.make_filter_item(
                        "All Characters",
                        len(base_pool),
                        is_all_selected,
                        lambda e: self.select_filter("game_mode", None),
                        icon=ft.Icons.PEOPLE_ALT_ROUNDED
                    )
                )

            modes = [
                ("Easy", ft.Icons.STAR_ROUNDED),
                ("Medium", ft.Icons.SPEED_ROUNDED),
                ("Hard", ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED),
            ]

            for mode_name, mode_icon in modes:
                if search_filter and search_filter not in mode_name.lower():
                    continue
                count = sum(1 for c in base_pool if get_character_game_mode(c) == mode_name)
                is_selected = self.selected_mode == mode_name
                self.arc_list_col.controls.append(
                    self.make_filter_item(
                        mode_name,
                        count,
                        is_selected,
                        lambda e, m=mode_name: self.select_filter("game_mode", m),
                        icon=mode_icon
                    )
                )

        # Bottom spacer for bottom shadow clearance
        if len(self.arc_list_col.controls) > 1:
            self.arc_list_col.controls.append(ft.Container(height=4))
        else:
            self.arc_list_col.controls.clear()
            self.arc_list_col.controls.append(
                ft.Container(
                    content=ft.Text("No results found", size=12, color=self.colors.text_secondary),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding(0, 24, 0, 24)
                )
            )

        try:
            if self.arc_list_col.page:
                self.arc_list_col.update()
        except Exception:
            pass

    def update_theme(self):
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        self.colors = ThemeColors(is_dark=is_dark)

        # Update card container
        self.arc_menu_card.bgcolor = self.colors.bg_main
        self.arc_menu_card.shadow = self.colors.raised_shadow(depth=6, blur=20)
        self.arc_menu_card.border = None

        # Update FAB
        self.arc_fab_container.bgcolor = ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_surface
        self.arc_fab_container.shadow = self.colors.raised_shadow()
        self.fab_inner_center.bgcolor = self.colors.pressed_surface
        self.fab_inner_center.shadow = self.colors.pressed_shadow(depth=1, blur=3)

        # Update search input
        self.arc_search_container.bgcolor = self.colors.card_surface
        self.arc_search_container.border = None
        self.arc_search_container.shadow = self.colors.raised_shadow()
        self.arc_search_icon.color = self.colors.accent_primary
        self.arc_search_input.color = self.colors.text_primary
        self.arc_search_input.hint_style = ft.TextStyle(color=self.colors.text_secondary, size=12)

        # Update title badge
        if hasattr(self, 'title_badge') and self.title_badge:
            self.title_badge.bgcolor = ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_elevated
            self.title_badge.shadow = self.colors.subtle_shadow(depth=1, blur=3)
            self.title_badge.border = None if not self.colors.is_dark else ft.Border.all(1, self.colors.border_subtle)
        if hasattr(self, 'title_text') and self.title_text:
            self.title_text.color = self.colors.accent_primary if not self.colors.is_dark else self.colors.text_secondary

        # Update category dropdown
        if self.category_container:
            self.category_container.bgcolor = ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_elevated
            self.category_container.shadow = self.colors.subtle_shadow(depth=1, blur=3)
            self.category_container.border = None
        if self.category_label_text:
            self.category_label_text.color = self.colors.text_primary
        if self.category_dropdown:
            self.category_dropdown.bgcolor = ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_surface
            self.category_dropdown.padding = 0
            self.category_dropdown.menu_padding = ft.Padding(6, 6, 6, 6)
            self.category_dropdown.size_constraints = ft.BoxConstraints(min_width=142, max_width=142)
            self.category_dropdown.elevation = 4
            self.category_dropdown.shadow_color = ft.Colors.BLACK_12 if not self.colors.is_dark else ft.Colors.BLACK_26
            self.category_dropdown.items = self.build_category_menu_items()

        # Update header buttons & separator
        self.reset_btn.bgcolor = ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_elevated
        self.reset_btn.shadow = self.colors.subtle_shadow(depth=1, blur=3)
        self.reset_btn.content.color = self.colors.accent_primary

        self.close_btn.bgcolor = ft.Colors.WHITE if not self.colors.is_dark else self.colors.card_elevated
        self.close_btn.shadow = self.colors.subtle_shadow(depth=1, blur=3)
        self.close_btn.content.color = self.colors.text_secondary

        self.separator_line.bgcolor = self.colors.accent_primary

        self.update_active_filter_display()
        self.build_filter_list_items()
