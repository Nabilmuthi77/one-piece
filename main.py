import math
import os
import json
import requests
import flet as ft

from constants import (
    API_URL, DARK_BG, LIGHT_BG, ACCENT
)
from utils.theme import (
    get_card_bg, get_text_main, get_text_muted, ThemeColors
)
from utils.helpers import (
    load_devil_fruits_types, get_story_arc,
    matches_df_filter, matches_game_mode_filter
)
from components.header import HeaderComponent
from components.footer import FooterComponent
from components.character_card import CharacterGridComponent, create_character_card
from components.pagination import PaginationComponent
from components.character_modal import open_character_modal
from components.fullscreen_viewer import FullscreenViewerComponent
from components.filter_menu import FilterMenuComponent
from components.exit_dialog import show_exit_dialog, close_exit_dialog, is_exit_dialog_open
from components.settings_view import SettingsView


def main(page: ft.Page):
    page.title = "One Piece"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = DARK_BG
    page.padding = 0
    page.scroll = None  # Using fixed page, scrolling inner content

    page.fonts = {
        "Outfit": "https://raw.githubusercontent.com/google/fonts/main/ofl/outfit/Outfit%5Bwght%5D.ttf"
    }
    transparent_scrollbar = ft.ScrollbarTheme(
        thickness=0,
        thumb_visibility=False,
        track_visibility=False,
        thumb_color=ft.Colors.TRANSPARENT,
        track_color=ft.Colors.TRANSPARENT,
        track_border_color=ft.Colors.TRANSPARENT,
    )
    transparent_system_overlay_dark = ft.SystemOverlayStyle(
        status_bar_color=ft.Colors.TRANSPARENT,
        system_navigation_bar_color=ft.Colors.TRANSPARENT,
        enforce_system_status_bar_contrast=False,
        status_bar_icon_brightness=ft.Brightness.LIGHT,
    )
    transparent_system_overlay_light = ft.SystemOverlayStyle(
        status_bar_color=ft.Colors.TRANSPARENT,
        system_navigation_bar_color=ft.Colors.TRANSPARENT,
        enforce_system_status_bar_contrast=False,
        status_bar_icon_brightness=ft.Brightness.DARK,
    )
    page.theme = ft.Theme(
        font_family="Outfit",
        scrollbar_theme=transparent_scrollbar,
        system_overlay_style=transparent_system_overlay_light,
    )
    page.dark_theme = ft.Theme(
        font_family="Outfit",
        scrollbar_theme=transparent_scrollbar,
        system_overlay_style=transparent_system_overlay_dark,
    )

    # State
    all_characters = []
    filtered_characters = []
    current_page = 1
    items_per_page = 30
    current_char = None
    last_back_time = 0.0

    # Components forward declarations & hooks
    def on_card_click(char):
        nonlocal current_char
        current_char = char
        open_character_modal(
            page=page,
            char=char,
            on_lock_click=lambda src, n: page.run_task(fullscreen_viewer.open_fs_locked, src, n),
        )

    def reopen_modal():
        if current_char:
            on_card_click(current_char)

    def before_open_fs():
        if filter_menu.arc_menu_open:
            filter_menu.close_arc_menu()

    def on_prev(e):
        nonlocal current_page
        if current_page > 1:
            current_page -= 1
            render_page()

    def on_next(e):
        nonlocal current_page
        total_pages = math.ceil(len(filtered_characters) / items_per_page)
        if current_page < total_pages:
            current_page += 1
            render_page()

    def apply_filters():
        nonlocal current_page, filtered_characters
        query = (header.search_input.value or "").strip().lower()

        filtered_characters = [
            c for c in all_characters
            if (not query or query in c.get('name', '').lower())
            and (not filter_menu.selected_arc or get_story_arc(c.get('first_appearance_arc')) == filter_menu.selected_arc)
            and (not filter_menu.selected_race or (c.get('race') or 'Unknown').strip() == filter_menu.selected_race)
            and matches_df_filter(c, filter_menu.selected_df)
            and matches_game_mode_filter(c, filter_menu.selected_mode)
        ]
        current_page = 1
        render_page()

    current_theme_pref = "dark"

    def handle_theme_change(pref: str):
        nonlocal current_theme_pref
        current_theme_pref = pref

        if pref == "light":
            page.theme_mode = ft.ThemeMode.LIGHT
            page.bgcolor = LIGHT_BG
        elif pref == "dark":
            page.theme_mode = ft.ThemeMode.DARK
            page.bgcolor = DARK_BG
        elif pref == "auto":
            is_dark = "dark" in str(page.platform_brightness).lower() if page.platform_brightness else False
            page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
            page.bgcolor = DARK_BG if is_dark else LIGHT_BG

        header.update_theme(page.theme_mode, get_card_bg(page), get_text_main(page), current_pref=pref)
        filter_menu.update_theme()
        pagination.update_theme(page.theme_mode == ft.ThemeMode.DARK)
        footers.update_theme(page.theme_mode == ft.ThemeMode.DARK)
        if len(page.views) > 1 and page.views[-1].route == "/settings":
            page.views[-1].bgcolor = DARK_BG if page.theme_mode == ft.ThemeMode.DARK else LIGHT_BG
            if len(page.views[-1].controls) > 0 and hasattr(page.views[-1].controls[0], "update_theme"):
                page.views[-1].controls[0].update_theme(pref)
        render_page()
        page.update()

    def toggle_theme(e=None):
        if isinstance(e, str) and e in ("light", "dark", "auto"):
            handle_theme_change(e)
            return
        new_pref = "light" if page.theme_mode == ft.ThemeMode.DARK else "dark"
        handle_theme_change(new_pref)

    def open_settings():
        if filter_menu.arc_menu_open:
            filter_menu.close_arc_menu()
        settings_view = SettingsView(
            page=page,
            current_pref=current_theme_pref,
            on_theme_changed=handle_theme_change,
            on_back=close_settings
        )
        settings_route_view = ft.View(
            route="/settings",
            controls=[settings_view],
            padding=0,
            bgcolor=DARK_BG if page.theme_mode == ft.ThemeMode.DARK else LIGHT_BG,
            can_pop=False
        )
        page.views.append(settings_route_view)
        page.update()

    def close_settings(e=None):
        if len(page.views) > 1 and page.views[-1].route == "/settings":
            page.views.pop()
            page.update()

    # Instantiate Components
    header = HeaderComponent(
        page=page,
        on_toggle_theme=toggle_theme,
        on_search=apply_filters,
        on_open_settings=open_settings
    )

    grid = CharacterGridComponent()
    pagination = PaginationComponent(on_prev=on_prev, on_next=on_next, page=page)
    footers = FooterComponent(page=page)

    fullscreen_viewer = FullscreenViewerComponent(
        page=page,
        on_reopen_modal=reopen_modal,
        on_before_open=before_open_fs
    )

    filter_menu = FilterMenuComponent(
        page=page,
        get_all_characters=lambda: all_characters,
        on_filter_changed=apply_filters
    )

    # Page resize handler
    def on_page_resize(e):
        cols_changed = grid.adjust_columns(page.width if page.width else 1200)
        if cols_changed:
            render_page()

        filter_menu.clamp_button_pos()
        filter_menu.arc_fab_wrapper.left = filter_menu.btn_left
        filter_menu.arc_fab_wrapper.top = filter_menu.btn_top
        if filter_menu.arc_menu_card and filter_menu.arc_menu_open:
            filter_menu.position_arc_menu()

        if len(page.views) > 1 and page.views[-1].route == "/settings":
            if len(page.views[-1].controls) > 0 and hasattr(page.views[-1].controls[0], "update_layout"):
                page.views[-1].controls[0].update_layout()

        page.update()

    page.on_resize = on_page_resize

    def render_page():
        grid.clear()

        pagination.update_state(
            current_page=current_page,
            total_items=len(filtered_characters),
            items_per_page=items_per_page,
            text_muted_color=get_text_muted(page)
        )

        footers.update_visibility(len(filtered_characters))

        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        is_dark = page.theme_mode == ft.ThemeMode.DARK
        for i, char in enumerate(filtered_characters[start_idx:end_idx]):
            card = create_character_card(char, is_dark, on_card_click)
            col_idx = i % len(grid.masonry_columns)
            grid.add_card(col_idx, card)

        page.update()

    # Loading indicator
    loading_text = ft.Text("Fetching characters...", size=20, color=get_text_muted(page))
    loading_container = ft.Container(
        content=ft.Column(
            [ft.ProgressRing(color=ACCENT), loading_text],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.Alignment.CENTER,
        expand=True
    )

    # Main layout assembly
    main_content = ft.Container(
        content=ft.Column([
            loading_container,
            grid.grid,
            pagination.container
        ], alignment=ft.MainAxisAlignment.START)
    )

    root_scroll_col = ft.Column([
        header.container,
        main_content,
        footers.footer_inline
    ], spacing=0, scroll=ft.ScrollMode.HIDDEN, expand=True)

    main_stack = ft.Stack([
        root_scroll_col,
        footers.footer_fixed,
        filter_menu.arc_dim_dismiss,
        filter_menu.arc_menu_card,
        filter_menu.arc_fab_wrapper,
    ], expand=True)

    page.add(main_stack)

    # Back press and exit handling
    def handle_back_press():
        nonlocal last_back_time
        import time
        now = time.time()
        if now - last_back_time < 0.35:
            return
        last_back_time = now

        # 0. If exit dialog is already showing, close it
        if is_exit_dialog_open():
            close_exit_dialog(page)
            return

        # 1. If floating category/arc filter menu is open, close it
        if filter_menu.arc_menu_open:
            filter_menu.close_arc_menu()
            return

        # 2. If fullscreen locked view is open on top, ignore back press (locked mode)
        if len(page.views) > 1 and page.views[-1].route == "/fullscreen":
            return

        # 3. If settings view is open, close it
        if len(page.views) > 1 and page.views[-1].route == "/settings":
            close_settings()
            return

        # 4. If any modal dialog is currently open, close it
        open_dialogs = [d for d in getattr(page, '_dialogs', ft.Column()).controls if getattr(d, 'open', False)]
        if open_dialogs:
            page.pop_dialog()
            return

        # 5. If at root main page, show confirmation exit dialog
        show_exit_dialog(page)

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key and e.key.lower() in ["escape", "back", "goback"]:
            handle_back_press()

    def on_view_pop(e):
        if len(page.views) > 1:
            if page.views[-1].route == "/fullscreen":
                # Fullscreen mode is locked! Back is disabled, must use unlock button.
                return
            page.views.pop()
            page.update()
        else:
            handle_back_press()

    page.on_keyboard_event = on_keyboard
    page.on_view_pop = on_view_pop
    page.on_app_lifecycle_state_change = fullscreen_viewer.on_lifecycle

    def on_platform_brightness_change(e):
        if current_theme_pref == "auto":
            handle_theme_change("auto")

    page.on_platform_brightness_change = on_platform_brightness_change

    if page.platform not in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS):
        try:
            page.window.prevent_close = True

            def on_window_event(e):
                if e.data == "close":
                    show_exit_dialog(page)

            page.window.on_event = on_window_event
        except Exception:
            pass

    def on_disconnect(e):
        import os
        os._exit(0)

    page.on_disconnect = on_disconnect

    if len(page.views) > 0:
        page.views[0].can_pop = False
        page.views[0].on_confirm_pop = lambda e: handle_back_press()

    # Initial data fetching with offline cache fallback
    cached_chars_file = os.path.join(os.path.dirname(__file__), 'data', 'characters.json')

    def retry_data_fetch():
        loading_container.content = ft.Column(
            [ft.ProgressRing(color=ACCENT), loading_text],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        loading_text.value = "Fetching characters..."
        loading_container.visible = True
        page.update()
        fetch_data()

    def fetch_data():
        nonlocal all_characters, filtered_characters
        load_devil_fruits_types()

        raw_characters = None
        # Load from local cache first for instant startup
        if os.path.exists(cached_chars_file):
            try:
                with open(cached_chars_file, 'r', encoding='utf-8') as f:
                    raw_characters = json.load(f)
            except Exception:
                pass

        # Fetch updated data from network with browser User-Agent
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            resp = requests.get(API_URL, headers=headers, timeout=5)
            if resp.status_code == 200:
                net_characters = resp.json()
                if net_characters:
                    raw_characters = net_characters
                    try:
                        os.makedirs(os.path.dirname(cached_chars_file), exist_ok=True)
                        with open(cached_chars_file, 'w', encoding='utf-8') as f:
                            json.dump(net_characters, f)
                    except Exception:
                        pass
        except Exception:
            # Gracefully rely on local cache if network is unreachable
            pass

        # Fallback to local cache if network failed
        if not raw_characters and os.path.exists(cached_chars_file):
            try:
                with open(cached_chars_file, 'r', encoding='utf-8') as f:
                    raw_characters = json.load(f)
            except Exception:
                pass

        if raw_characters:
            unique_chars = {}
            for c in raw_characters:
                raw_name = c.get('name') or ''
                name = raw_name.strip()
                if not name:
                    continue
                c['name'] = name
                key = name.lower()
                if key not in unique_chars:
                    unique_chars[key] = c
                else:
                    old_c = unique_chars[key]
                    old_r = (len(old_c.get('journey') or []) * 2) + len(old_c.get('relationships') or []) + (5 if old_c.get('bounty') else 0)
                    new_r = (len(c.get('journey') or []) * 2) + len(c.get('relationships') or []) + (5 if c.get('bounty') else 0)
                    if new_r > old_r:
                        unique_chars[key] = c
            all_characters = list(unique_chars.values())
            filtered_characters = all_characters
            loading_container.visible = False
            pagination.set_visible(True)

            from collections import Counter
            filter_menu.race_counts = Counter((c.get('race') or 'Unknown').strip() for c in all_characters)
            filter_menu.build_filter_list_items()

            # Trigger resize once to layout columns
            on_page_resize(None)
        else:
            is_dark = page.theme_mode == ft.ThemeMode.DARK
            colors = ThemeColors(is_dark=is_dark)

            retry_btn = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.REFRESH_ROUNDED, size=16, color=ft.Colors.WHITE),
                    ft.Text("Try Again", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
                ], tight=True, spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=colors.accent_primary,
                padding=ft.Padding(18, 10, 18, 10),
                border_radius=14,
                shadow=colors.subtle_shadow(depth=2, blur=4),
                on_click=lambda e: retry_data_fetch(),
            )

            error_card = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.WIFI_OFF_ROUNDED, size=44, color=ft.Colors.RED_400),
                    ft.Text("Connection Issue", size=18, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                    ft.Text(
                        "Failed to connect to oparchive.com.\nPlease check your connection.",
                        size=12.5,
                        color=colors.text_secondary,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=8),
                    retry_btn
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6, tight=True),
                bgcolor=colors.card_surface,
                padding=ft.Padding(24, 20, 24, 20),
                border_radius=20,
                shadow=colors.raised_shadow(),
                width=320,
                alignment=ft.Alignment(0, 0)
            )

            loading_container.content = error_card
            loading_container.visible = True
            page.update()

    fetch_data()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
