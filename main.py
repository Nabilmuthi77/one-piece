import flet as ft
import requests
import math
import re
from collections import Counter

API_URL = 'https://oparchive.com/data/characters.json'
DEVIL_FRUITS_API_URL = 'https://oparchive.com/data/devil_fruits.json'
BASE_IMG_URL = 'https://oparchive.com'


DEVIL_FRUIT_TYPES = {
    # Fallback alias jika diperlukan
    "gomu gomu no mi": "Zoan",
    "gomu-gomu no mi": "Zoan",
}


def load_devil_fruits_types():
    global DEVIL_FRUIT_TYPES
    try:
        resp = requests.get(DEVIL_FRUITS_API_URL, timeout=10)
        if resp.status_code == 200:
            for item in resp.json():
                name = item.get('name', '').strip()
                f_type = item.get('type', '').strip()
                if name and f_type:
                    clean = re.sub(r'\s*\([^)]*awakened[^)]*\)', '', name, flags=re.IGNORECASE).strip()
                    DEVIL_FRUIT_TYPES[clean.casefold()] = f_type
                    base = clean.split(',')[0].strip()
                    if base.casefold() not in DEVIL_FRUIT_TYPES:
                        DEVIL_FRUIT_TYPES[base.casefold()] = f_type
    except Exception as e:
        print(f"Warning: Failed to fetch devil fruits data: {e}")


def get_devil_fruit_type(fruit_name):
    if not fruit_name:
        return None
    clean = re.sub(r'\s*\([^)]*awakened[^)]*\)', '', str(fruit_name), flags=re.IGNORECASE).strip()
    if 'SMILE' in clean.upper() or 'ZOAN' in clean.upper() or 'MODEL:' in clean.upper():
        return 'Zoan'
    cf = clean.casefold()
    if cf in DEVIL_FRUIT_TYPES:
        return DEVIL_FRUIT_TYPES[cf]
    base = clean.split(',')[0].strip().casefold()
    if base in DEVIL_FRUIT_TYPES:
        return DEVIL_FRUIT_TYPES[base]
    return None


# Colors matching style.css
DARK_BG = "#0f172a"
DARK_CARD = "#1e293b"
DARK_TEXT_MAIN = "#f8fafc"
DARK_TEXT_MUTED = "#94a3b8"

LIGHT_BG = "#f1f5f9"
LIGHT_CARD = "#ffffff"
LIGHT_TEXT_MAIN = "#0f172a"
LIGHT_TEXT_MUTED = "#64748b"

ACCENT = "#0ea5e9"
WHATSAPP = "#25D366"

def get_story_arc(chapter_str):
    if not chapter_str:
        return 'Unknown'
    match = re.search(r'Chapter\s+(\d+)', chapter_str)
    if not match:
        return 'SBS & Extras'
    ch = int(match.group(1))
    if ch >= 1126: return 'Elbaph'
    if ch >= 1058: return 'Egghead'
    if ch >= 909: return 'Wano Country'
    if ch >= 903: return 'Levely'
    if ch >= 825: return 'Whole Cake Island'
    if ch >= 802: return 'Zou'
    if ch >= 700: return 'Dressrosa'
    if ch >= 654: return 'Punk Hazard'
    if ch >= 603: return 'Fish-Man Island'
    if ch >= 598: return 'Return to Sabaody'
    if ch >= 581: return 'Post-War'
    if ch >= 550: return 'Marineford'
    if ch >= 525: return 'Impel Down'
    if ch >= 514: return 'Amazon Lily'
    if ch >= 490: return 'Sabaody Archipelago'
    if ch >= 442: return 'Thriller Bark'
    if ch >= 431: return 'Post-Enies Lobby'
    if ch >= 375: return 'Enies Lobby'
    if ch >= 322: return 'Water 7'
    if ch >= 303: return 'Long Ring Long Land'
    if ch >= 237: return 'Skypiea'
    if ch >= 218: return 'Jaya'
    if ch >= 155: return 'Arabasta'
    if ch >= 130: return 'Drum Island'
    if ch >= 115: return 'Little Garden'
    if ch >= 106: return 'Whisky Peak'
    if ch >= 101: return 'Reverse Mountain'
    if ch >= 96: return 'Loguetown'
    if ch >= 69: return 'Arlong Park'
    if ch >= 42: return 'Baratie'
    if ch >= 22: return 'Syrup Village'
    if ch >= 8: return 'Orange Town'
    if ch >= 1: return 'Romance Dawn'
    return 'SBS & Extras'

ARC_ORDER = [
    "Romance Dawn", "Orange Town", "Syrup Village", "Baratie", "Arlong Park",
    "Loguetown", "Reverse Mountain", "Whisky Peak", "Little Garden", "Drum Island",
    "Arabasta", "Jaya", "Skypiea", "Long Ring Long Land", "Water 7",
    "Enies Lobby", "Post-Enies Lobby", "Thriller Bark", "Sabaody Archipelago",
    "Amazon Lily", "Impel Down", "Marineford", "Post-War", "Return to Sabaody",
    "Fish-Man Island", "Punk Hazard", "Dressrosa", "Zou", "Whole Cake Island",
    "Levely", "Wano Country", "Egghead", "Elbaph", "SBS & Extras"
]

def main(page: ft.Page):
    wakelock = None
    if page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]:
        wakelock = ft.Wakelock()

    page.title = "One Piece"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = DARK_BG
    page.padding = 0
    page.scroll = None  # Using fixed page, scrolling inner content


    # Enable keyboard event to intercept Android back button (Escape)
    def on_keyboard(e: ft.KeyboardEvent):
        pass # we'll handle this in on_dismiss instead
    page.on_keyboard_event = on_keyboard

    page.fonts = {
        "Outfit": "https://raw.githubusercontent.com/google/fonts/main/ofl/outfit/Outfit%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Outfit")

    all_characters = []
    filtered_characters = []
    current_page = 1
    items_per_page = 30
    current_char = None
    category_dropdown = None
    category_container = None
    category_label_text = None
    category_menu_items_text = []
    arc_menu_card = None
    arc_search_input = None
    fab_inner_center = None
    arc_fab_wrapper = None
    clamp_button_pos = None
    position_arc_menu = None

    def get_card_bg(): return LIGHT_CARD if page.theme_mode == ft.ThemeMode.LIGHT else DARK_CARD
    def get_text_main(): return LIGHT_TEXT_MAIN if page.theme_mode == ft.ThemeMode.LIGHT else DARK_TEXT_MAIN
    def get_text_muted(): return LIGHT_TEXT_MUTED if page.theme_mode == ft.ThemeMode.LIGHT else DARK_TEXT_MUTED

    def get_modern_gradient():
        return ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[
                ft.Colors.with_opacity(0.08, ACCENT) if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.with_opacity(0.15, ACCENT),
                ft.Colors.with_opacity(0.02, ACCENT) if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.with_opacity(0.05, ACCENT),
            ]
        )

    def get_modern_border():
        border_color = ft.Colors.with_opacity(0.2, ACCENT) if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.with_opacity(0.3, ACCENT)
        return ft.Border.all(1, border_color)

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        theme_btn.icon = ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE
        page.bgcolor = LIGHT_BG if page.theme_mode == ft.ThemeMode.LIGHT else DARK_BG
        search_input.bgcolor = get_card_bg()
        search_input.color = get_text_main()
        if arc_menu_card:
            arc_menu_card.bgcolor = get_card_bg()
            arc_menu_card.border = get_modern_border()
            arc_search_input.bgcolor = DARK_BG if page.theme_mode == ft.ThemeMode.DARK else LIGHT_BG
            arc_search_input.color = get_text_main()
            if category_container:
                category_container.bgcolor = get_card_bg()
                category_container.border = get_modern_border()
            if category_label_text:
                category_label_text.color = get_text_main()
            if category_dropdown:
                category_dropdown.bgcolor = get_card_bg()
                category_dropdown.shape = ft.RoundedRectangleBorder(
                    radius=12,
                    side=ft.BorderSide(1, ft.Colors.with_opacity(0.3, ACCENT) if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.with_opacity(0.2, ACCENT))
                )
            if category_menu_items_text:
                for item_txt in category_menu_items_text:
                    item_txt.color = get_text_main()
            build_filter_list_items()
        render_page()
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE,
        on_click=toggle_theme,
        tooltip="Toggle Theme",
        icon_color=ft.Colors.WHITE,
        bgcolor=ACCENT,
    )

    import time
    def animate_logo(e):
        logo.scale = 1.05
        logo.update()
        time.sleep(0.15)
        logo.scale = 1.0
        logo.update()

    logo = ft.Container(
        content=ft.Image(src="one-piece-logo.png", height=120, fit=ft.BoxFit.CONTAIN),
        on_click=animate_logo,
        scale=1.0,
        animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
    )

    search_input = ft.TextField(
        hint_text="Search characters...",
        expand=True,
        border=ft.OutlineInputBorder(border_radius=30, side=ft.BorderSide(color=ft.Colors.TRANSPARENT)),
        prefix_icon=ft.Icons.SEARCH,
        on_submit=lambda e: do_search(),
        on_change=lambda e: do_search(),
        bgcolor=DARK_CARD,
        color=DARK_TEXT_MAIN,
        content_padding=15
    )

    masonry_columns = [ft.Column(expand=1, spacing=15) for _ in range(4)]
    grid = ft.Container(
        content=ft.Row(controls=masonry_columns, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),
        padding=20
    )

    arc_fab_wrapper = None
    arc_menu_card = None
    arc_menu_open = False
    btn_left = 300.0
    btn_top = 600.0

    def on_page_resize(e):
        # Adjust masonry columns like the CSS media queries
        cols = 2
        if page.width >= 1200: cols = 5
        elif page.width >= 900: cols = 4
        elif page.width >= 600: cols = 3

        if len(masonry_columns) != cols:
            masonry_columns.clear()
            for _ in range(cols):
                masonry_columns.append(ft.Column(expand=1, spacing=15))
            grid.content.controls = masonry_columns
            render_page()

        if arc_fab_wrapper and clamp_button_pos is not None:
            clamp_button_pos()
            arc_fab_wrapper.left = btn_left
            arc_fab_wrapper.top = btn_top
        if arc_menu_card and arc_menu_open and position_arc_menu is not None:
            position_arc_menu()

        page.update()

    page.on_resize = on_page_resize

    page_info = ft.Text("Page 1", weight=ft.FontWeight.BOLD, color=DARK_TEXT_MUTED)

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

    prev_btn = ft.FilledButton("← Prev", on_click=on_prev, style=ft.ButtonStyle(bgcolor=ACCENT, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=25)))
    next_btn = ft.FilledButton("Next →", on_click=on_next, style=ft.ButtonStyle(bgcolor=ACCENT, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=25)))

    pagination_row = ft.Row([prev_btn, page_info, next_btn], alignment=ft.MainAxisAlignment.CENTER, visible=False)
    pagination_container = ft.Container(content=pagination_row, padding=ft.Padding(0, 20, 0, 40))

    selected_category = "arcs"
    selected_arc = None
    selected_df = None
    selected_race = None
    selected_mode = None

    arc_counts = {}
    race_counts = {}
    df_type_counts = {}
    df_fruit_counts = {}

    def get_character_game_mode(c):
        journey_count = len(c.get('journey') or [])
        if journey_count >= 6:
            return "Easy"
        elif journey_count >= 2:
            return "Medium"
        else:
            return "Hard"

    def matches_game_mode_filter(c, target):
        if not target:
            return True
        return get_character_game_mode(c).lower() == target.lower()

    def matches_df_filter(c, target):
        if not target:
            return True
        raw = c.get('devil_fruit')
        items = raw if isinstance(raw, list) else ([raw] if raw else [])
        items = [str(x).strip() for x in items if x and str(x).strip().lower() not in ['none', 'unknown', '']]

        if target == 'None':
            return len(items) == 0

        if target in ['Paramecia', 'Zoan', 'Logia']:
            for it in items:
                clean = re.sub(r'\s*\([^)]*awakened[^)]*\)', '', it, flags=re.IGNORECASE).strip()
                t = get_devil_fruit_type(clean)
                if t and t.lower() == target.lower():
                    return True
            return False

        for it in items:
            clean = re.sub(r'\s*\([^)]*awakened[^)]*\)', '', it, flags=re.IGNORECASE).strip()
            if target.lower() in clean.lower():
                return True
        return False

    def apply_filters():
        nonlocal current_page, filtered_characters
        query = (search_input.value or "").strip().lower()

        filtered_characters = [
            c for c in all_characters
            if (not query or query in c.get('name', '').lower())
            and (not selected_arc or get_story_arc(c.get('first_appearance_arc')) == selected_arc)
            and (not selected_race or (c.get('race') or 'Unknown').strip() == selected_race)
            and matches_df_filter(c, selected_df)
            and matches_game_mode_filter(c, selected_mode)
        ]
        current_page = 1
        render_page()

    def do_search():
        apply_filters()

    def format_bounty(bounty):
        if not bounty: return 'Unknown'
        if isinstance(bounty, str): return bounty
        return f"{bounty:,} Berries"

    def format_haki(haki):
        if not haki or not len(haki): return 'No Haki or Unknown'
        res = []
        for h in haki:
            hl = h.lower()
            if 'armament' in hl: res.append('Busoshoku')
            elif 'observation' in hl: res.append('Kenbunshoku')
            elif 'conqueror' in hl: res.append('Haoshoku')
            else: res.append(h)
        return ', '.join(res) if res else 'No Haki or Unknown'
 
    def format_devil_fruit(devil_fruit):
        if not devil_fruit:
            return "Unknown"

        fruit_name = devil_fruit.strip()
        fruit_type = get_devil_fruit_type(fruit_name)

        if fruit_type:
            return f"{fruit_type} -- {fruit_name}"

        return fruit_name

    async def close_fs(e):
        nonlocal is_locked
        is_locked = False
        if wakelock:
            try:
                await wakelock.disable()
            except Exception as ex:
                print(f"Wakelock error (disable): {ex}")
        else:
            try:
                page.window.prevent_display_sleep = False
            except:
                pass
        page.window.full_screen = False

        # Pop the fullscreen view if it's currently on top
        if len(page.views) > 1 and page.views[-1].route == "/fullscreen":
            page.views.pop()

        page.update()

        if current_char:
            import asyncio
            await asyncio.sleep(0.1)
            open_modal(current_char)

    def on_view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            page.update()

    page.on_view_pop = on_view_pop

    def on_lifecycle(e):
        if e.data == ft.AppLifecycleState.RESUME.name and is_locked:
            page.window.full_screen = True
            page.update()
    page.on_app_lifecycle_state_change = on_lifecycle

    is_locked = False
    async def toggle_lock(e):
        nonlocal is_locked
        if is_locked:
            await close_fs(e)
        else:
            is_locked = True
            if wakelock:
                try:
                    await wakelock.enable()
                except Exception as ex:
                    print(f"Wakelock error (enable): {ex}")
            else:
                try:
                    page.window.prevent_display_sleep = True
                except:
                    pass
            lock_btn.icon = ft.Icons.LOCK_ROUNDED
            lock_btn.icon_color = ft.Colors.WHITE
            lock_btn.style = ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_500,
                shape=ft.CircleBorder(),
                padding=12
            )
            fs_image_container.border = ft.Border.all(12, ft.Colors.BLUE_500)
            page.update()


    fs_dlg_image = ft.Image(src="", fit=ft.BoxFit.CONTAIN, border_radius=12)
    fs_image_container = ft.Container(content=fs_dlg_image, padding=0, border_radius=24, clip_behavior=ft.ClipBehavior.ANTI_ALIAS)

    fs_name_text = ft.Text(
        "",
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS
    )

    pill_badge = ft.Container(
        content=fs_name_text,
        bgcolor=ft.Colors.BLUE_500,
        padding=ft.Padding(20, 8, 20, 8),
        border_radius=20,
    )

    fs_image_stack = ft.Stack(
        controls=[
            fs_image_container,
            ft.Container(
                content=pill_badge,
                alignment=ft.Alignment(0, 1),
                bottom=0, left=0, right=0,
                offset=ft.Offset(0, 0.35)
            )
        ],
        clip_behavior=ft.ClipBehavior.NONE
    )

    lock_btn = ft.IconButton(
        icon=ft.Icons.LOCK_OPEN_ROUNDED,
        on_click=toggle_lock,
        icon_color=ft.Colors.WHITE,
        icon_size=24,
        tooltip="Unlock View",
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            shape=ft.CircleBorder(),
            padding=12
        )
    )
    fs_overlay = ft.Container(
        content=ft.Stack([
            ft.Container(
                content=fs_image_stack,
                alignment=ft.Alignment.CENTER,
                expand=True,
                top=0, bottom=0, left=0, right=0
            ),
            ft.Container(
                content=ft.Row([lock_btn], alignment=ft.MainAxisAlignment.END, spacing=0),
                alignment=ft.Alignment.TOP_RIGHT,
                padding=ft.Padding(20, 50, 20, 20),
                top=0, right=0, left=0
            )
        ], expand=True),
        bgcolor=ft.Colors.WHITE,
        expand=True,
        visible=False
    )

    async def open_fs_locked(img_src, name):
        nonlocal is_locked
        if arc_menu_open:
            close_arc_menu()
        page.pop_dialog()
        import asyncio
        await asyncio.sleep(0.1)
        fs_dlg_image.src = img_src
        fs_name_text.value = name
        is_locked = True
        if wakelock:
            try:
                await wakelock.enable()
            except Exception as ex:
                print(f"Wakelock error (enable): {ex}")
        else:
            try:
                page.window.prevent_display_sleep = True
            except:
                pass
        lock_btn.icon = ft.Icons.LOCK_ROUNDED
        lock_btn.icon_color = ft.Colors.WHITE
        lock_btn.style = ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_500,
            shape=ft.CircleBorder(),
            padding=12
        )
        fs_image_container.border = ft.Border.all(12, ft.Colors.BLUE_500)
        page.window.full_screen = True

        fs_overlay.visible = True
        fs_view = ft.View(
            route="/fullscreen",
            controls=[fs_overlay],
            padding=0,
            bgcolor=ft.Colors.WHITE,
            can_pop=False
        )
        page.views.append(fs_view)
        page.update()

    def open_modal(char):
        nonlocal current_char
        current_char = char

        async def unfocus_hack():
            await theme_btn.focus()
        page.run_task(unfocus_hack)

        def close_this(e):
            dlg.open = False
            page.update()

        img_src = BASE_IMG_URL + char.get('image', '') if char.get('image') else 'https://via.placeholder.com/400x500?text=No+Image'
        status = char.get('status', 'Unknown')

        status_color = ft.Colors.GREEN if status.lower() == 'alive' else (ft.Colors.RED if status.lower() == 'deceased' else get_text_muted())

        def info_item(label, value):
            return ft.Container(
                content=ft.Column([
                    ft.Text(label.upper(), size=11, color=get_text_muted(), weight=ft.FontWeight.BOLD),
                    ft.Text(str(value), size=14, color=get_text_main(), weight=ft.FontWeight.W_600)
                ], spacing=4),
                gradient=get_modern_gradient(),
                padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                border_radius=12,
                border=get_modern_border(),
                width=float('inf')
            )


        def devil_fruit_item(char):
            raw_fruit = char.get('devil_fruit')
            if not raw_fruit or str(raw_fruit).strip().lower() in ['none', 'unknown', '']:
                return ft.Container(
                    content=ft.Column([
                        ft.Text('DEVIL FRUIT', size=11, color=get_text_muted(), weight=ft.FontWeight.BOLD),
                        ft.Text('None', size=14, color=get_text_main(), weight=ft.FontWeight.W_600)
                    ], spacing=4),
                    gradient=get_modern_gradient(),
                    padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                    border_radius=12,
                    border=get_modern_border(),
                    width=float('inf')
                )

            fruit_list = raw_fruit if isinstance(raw_fruit, list) else [raw_fruit]
            fruit_list = [str(f).strip() for f in fruit_list if str(f).strip() and str(f).strip().lower() not in ['none', 'unknown', '']]

            if not fruit_list:
                return ft.Container(
                    content=ft.Column([
                        ft.Text('DEVIL FRUIT', size=11, color=get_text_muted(), weight=ft.FontWeight.BOLD),
                        ft.Text('None', size=14, color=get_text_main(), weight=ft.FontWeight.W_600)
                    ], spacing=4),
                    gradient=get_modern_gradient(),
                    padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                    border_radius=12,
                    border=get_modern_border(),
                    width=float('inf')
                )

            def get_df_type(f_name):
                return get_devil_fruit_type(f_name)

            char_name = str(char.get('name', '')).lower()
            fruit_rows = []

            for f_str in fruit_list:
                is_awakened = bool(re.search(r'awakened', f_str, re.IGNORECASE)) or ('luffy' in char_name)
                clean_name = re.sub(r'\s*\(\s*Awakened\s*\)', '', f_str, flags=re.IGNORECASE).strip()
                f_type = get_df_type(clean_name)
                formatted_name = clean_name.replace(', ', ' -- ')

                row_controls = []
                if f_type:
                    # Badge tipe buah warna biru wave footer (ACCENT = #0ea5e9)
                    row_controls.append(
                        ft.Container(
                            content=ft.Text(
                                f_type.upper(),
                                size=11,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=ACCENT,
                            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                            border_radius=20
                        )
                    )

                if is_awakened:
                    # Awakening badge putih
                    row_controls.append(
                        ft.Container(
                            content=ft.Text(
                                "AWAKENING",
                                size=11,
                                color="#0f172a",
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=ft.Colors.WHITE,
                            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                            border_radius=20
                        )
                    )

                prefix = "-- " if (f_type or is_awakened) else ""
                row_controls.append(
                    ft.Text(
                        f"{prefix}{formatted_name}",
                        size=14,
                        color=get_text_main(),
                        weight=ft.FontWeight.W_600
                    )
                )

                # Sejajar horizontal dalam satu row
                fruit_rows.append(
                    ft.Row(
                        controls=row_controls,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        wrap=True,
                        spacing=8,
                        run_spacing=4
                    )
                )

            return ft.Container(
                content=ft.Column([
                    ft.Text('DEVIL FRUIT', size=11, color=get_text_muted(), weight=ft.FontWeight.BOLD),
                    *fruit_rows
                ], spacing=6),
                gradient=get_modern_gradient(),
                padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                border_radius=12,
                border=get_modern_border(),
                width=float('inf')
            )


        content = ft.Column([
            ft.Stack([
                ft.Container(
                    content=ft.Image(src=img_src, height=250, fit=ft.BoxFit.COVER),
                    width=float('inf'),
                    border_radius=ft.BorderRadius(top_left=24, top_right=24, bottom_left=0, bottom_right=0)
                ),
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        on_click=close_this,
                        bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
                        icon_color=ft.Colors.WHITE
                    ),
                    top=10,
                    right=10
                )
            ]),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(char.get('name', 'Unknown'), size=32, weight=ft.FontWeight.BOLD, color=get_text_main(), max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                            expand=True
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOCK_ROUNDED,
                            on_click=lambda e, src=img_src, n=char.get('name', 'Unknown'): page.run_task(open_fs_locked, src, n),
                            tooltip="Lock View",
                            icon_color=get_text_muted()
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        content=ft.Text(status.upper(), color=status_color, weight=ft.FontWeight.BOLD, size=12),
                        padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.4, status_color) if status.lower() == 'unknown' else status_color),
                        border_radius=20,
                        bgcolor=ft.Colors.TRANSPARENT if status.lower() == 'unknown' else ft.Colors.with_opacity(0.1, status_color)
                    ),
                    info_item("Bounty", format_bounty(char.get('bounty'))),
                    info_item("Haki Types", format_haki(char.get('haki'))),
                    devil_fruit_item(char),
                    info_item("Affiliation", char.get('affiliation', 'None')),
                    info_item("Origin", char.get('origin', 'Unknown')),
                    info_item("Race", char.get('race', 'Unknown')),
                    info_item("First Appearance", char.get('first_appearance_arc', 'Unknown')),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("DESCRIPTION", size=11, color=get_text_muted(), weight=ft.FontWeight.BOLD),
                            ft.Text(char.get('description', 'No description available.'), size=14, color=get_text_main())
                        ], spacing=4),
                        gradient=get_modern_gradient(),
                        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                        border_radius=12,
                        border=get_modern_border(),
                        width=float('inf')
                    )
                ], spacing=15),
                padding=20
            )
        ], scroll=ft.ScrollMode.AUTO, tight=True, spacing=0)

        dlg = ft.AlertDialog(
            content=ft.Container(content, width=600),
            content_padding=0,
            shape=ft.RoundedRectangleBorder(radius=24),
            bgcolor=get_card_bg()
        )

        page.show_dialog(dlg)

    def render_page():
        for col in masonry_columns:
            col.controls.clear()

        total_pages = max(1, math.ceil(len(filtered_characters) / items_per_page))
        page_info.value = f"Page {current_page} of {total_pages}"
        page_info.color = get_text_muted()

        prev_btn.disabled = current_page == 1
        next_btn.disabled = current_page == total_pages

        # Dynamic footer visibility instead of structural layout changes
        # This completely prevents search field focus drops!
        if len(filtered_characters) <= 2:
            footer_inline.visible = False
            footer_fixed.visible = True
        else:
            footer_inline.visible = True
            footer_fixed.visible = False

        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page

        for i, char in enumerate(filtered_characters[start_idx:end_idx]):
            img_src = BASE_IMG_URL + char.get('image', '') if char.get('image') else 'https://via.placeholder.com/400x500?text=No+Image'

            card_content = ft.Stack([
                ft.Image(
                    src=img_src,
                    fit=ft.BoxFit.FIT_WIDTH,
                    width=float('inf'),
                ),
                ft.Container(
                    left=0, right=0, bottom=0, height=100,
                    padding=ft.Padding(top=0, left=15, right=15, bottom=15),
                    alignment=ft.Alignment.BOTTOM_CENTER,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_CENTER,
                        end=ft.Alignment.BOTTOM_CENTER,
                        colors=[ft.Colors.TRANSPARENT, ft.Colors.with_opacity(0.8, ft.Colors.BLACK), ft.Colors.BLACK],
                        stops=[0.0, 0.6, 1.0]
                    ),
                    content=ft.Text(char.get('name', 'Unknown'), color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=18, text_align=ft.TextAlign.CENTER)
                )
            ])

            card_container = ft.Container(
                content=card_content,
                bgcolor=get_card_bg(),
                border_radius=16,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK_26),
                on_click=lambda e, c=char: open_modal(c)
            )

            col_idx = i % len(masonry_columns)
            masonry_columns[col_idx].controls.append(card_container)

        page.update()

    loading_text = ft.Text("Fetching characters...", size=20, color=get_text_muted())
    loading_container = ft.Container(
        content=ft.Column([ft.ProgressRing(color=ACCENT), loading_text], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.Alignment.CENTER,
        expand=True
    )

    header = ft.Container(
        content=ft.Column([
            ft.Row([ft.Container(expand=True), theme_btn], alignment=ft.MainAxisAlignment.END),
            logo,
            ft.Container(content=search_input, width=500, alignment=ft.Alignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding(20, 50, 20, 10),
    )

    def create_footer():
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Image(src="wave.svg", fit=ft.BoxFit.FILL, width=float('inf'), height=60),
                    width=float('inf'),
                    height=60,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Made for fun by me", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=16),
                        ft.Container(
                            content=ft.Row([
                                ft.Image(src="wa.svg", width=24, height=24),
                                ft.Text("Contact me", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=16)
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                            bgcolor=WHATSAPP,
                            padding=ft.Padding(20, 10, 20, 10),
                            border_radius=30,
                            width=200,
                            url="https://wa.me/6282258941501"
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ACCENT,
                    padding=ft.Padding(20, 0, 20, 40),
                    width=float('inf')
                )
            ], spacing=-2),
            width=float('inf')
        )

    footer_inline = create_footer()
    footer_fixed = create_footer()
    footer_fixed.bottom = 0
    footer_fixed.left = 0
    footer_fixed.right = 0
    footer_fixed.visible = False

    main_content = ft.Container(
        content=ft.Column([
            loading_container,
            grid,
            pagination_container
        ], alignment=ft.MainAxisAlignment.START)
    )

    root_scroll_col = ft.Column([
        header,
        main_content,
        footer_inline
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    # ==========================================
    # ARC FILTER FLOATING BUTTON & POPUP MENU
    # (Draggable & dynamically positioned, replicated from mobile-sidebar.js & sidebar.blade.php)
    # ==========================================
    BUTTON_SIZE = 42
    VIEWPORT_MARGIN = 16
    MENU_GAP = 12

    arc_menu_open = False
    is_dragging = False
    drag_distance = 0.0
    last_toggle_time = 0.0

    # Initial position: bottom-right of viewport
    init_pw = float(page.width if page.width else 400)
    init_ph = float(page.height if page.height else 800)
    btn_left = max(float(VIEWPORT_MARGIN), init_pw - BUTTON_SIZE - float(VIEWPORT_MARGIN))
    btn_top = max(float(VIEWPORT_MARGIN), init_ph - BUTTON_SIZE - 28.0)

    start_pointer_x = 0.0
    start_pointer_y = 0.0
    start_btn_left = btn_left
    start_btn_top = btn_top

    def clamp_button_pos(l=None, t=None):
        nonlocal btn_left, btn_top
        curr_pw = float(page.width if page.width else 400)
        curr_ph = float(page.height if page.height else 800)
        max_left = max(float(VIEWPORT_MARGIN), curr_pw - BUTTON_SIZE - float(VIEWPORT_MARGIN))
        max_top = max(float(VIEWPORT_MARGIN), curr_ph - BUTTON_SIZE - float(VIEWPORT_MARGIN))
        target_l = btn_left if l is None else l
        target_t = btn_top if t is None else t
        btn_left = max(float(VIEWPORT_MARGIN), min(float(target_l), max_left))
        btn_top = max(float(VIEWPORT_MARGIN), min(float(target_t), max_top))
        return btn_left, btn_top

    # Spinner 1: Dual-arc rotating swirl loader (continuous animated WebP in ACCENT blue, 40 FPS)
    fab_spinner_normal = ft.Image(
        src="usc_spinner.webp",
        width=22,
        height=22,
        fit=ft.BoxFit.CONTAIN
    )

    # Spinner 2: Active 3x3 dot matrix sliding puzzle (continuous animated WebP in ACCENT blue, 30 FPS)
    fab_spinner_active = ft.Image(
        src="usc_cog.webp",
        width=22,
        height=22,
        fit=ft.BoxFit.CONTAIN
    )

    # Inner Center: 28x28 white disc (bg-white/90 with soft drop shadow)
    fab_inner_center = ft.Container(
        content=fab_spinner_normal,
        width=28,
        height=28,
        border_radius=14,
        bgcolor=ft.Colors.with_opacity(0.92, ft.Colors.WHITE),
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.10, "#0f172a"),
            offset=ft.Offset(0, 1.5)
        )
    )

    # Outer Button: 42x42 circular container with ACCENT sky gradient,
    # ring-1 ring-white/70 border, and soft sky glow shadow
    arc_fab_container = ft.Container(
        content=fab_inner_center,
        width=42,
        height=42,
        border_radius=21,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[
                ft.Colors.with_opacity(0.25, ACCENT),
                ft.Colors.with_opacity(0.25, "#38bdf8")
            ]
        ),
        border=ft.Border.all(1.2, ft.Colors.with_opacity(0.70, ft.Colors.WHITE)),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.20, ACCENT),
            offset=ft.Offset(0, 4)
        ),
        alignment=ft.Alignment.CENTER,
        tooltip="Filter Characters"
    )

    def set_normal_state():
        arc_fab_container.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[
                ft.Colors.with_opacity(0.25, ACCENT),
                ft.Colors.with_opacity(0.25, "#38bdf8")
            ]
        )
        arc_fab_container.shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.20, ACCENT),
            offset=ft.Offset(0, 4)
        )
        fab_inner_center.content = fab_spinner_normal
        if arc_fab_wrapper and arc_fab_wrapper.page:
            arc_fab_container.update()

    def set_active_state():
        arc_fab_container.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[
                ft.Colors.with_opacity(0.45, ACCENT),
                ft.Colors.with_opacity(0.45, "#38bdf8")
            ]
        )
        arc_fab_container.shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=25,
            color=ft.Colors.with_opacity(0.35, ACCENT),
            offset=ft.Offset(0, 4)
        )
        fab_inner_center.content = fab_spinner_active
        if arc_fab_wrapper and arc_fab_wrapper.page:
            arc_fab_container.update()

    def position_arc_menu():
        if not arc_menu_open:
            return

        curr_pw = float(page.width if page.width else 1200)
        curr_ph = float(page.height if page.height else 800)

        # Dynamic menu dimensions based on viewport
        menu_width = min(340.0, max(280.0, curr_pw - (VIEWPORT_MARGIN * 2)))
        menu_height = min(480.0, max(320.0, curr_ph - 90))
        arc_menu_card.width = menu_width
        arc_menu_card.height = menu_height

        btn_r = btn_left + BUTTON_SIZE
        btn_b = btn_top + BUTTON_SIZE
        btn_cx = btn_left + BUTTON_SIZE / 2.0
        btn_cy = btn_top + BUTTON_SIZE / 2.0

        candidates = [
            # Candidate 1: Right of button
            {"left": btn_r + MENU_GAP, "top": btn_cy - menu_height / 2.0},
            # Candidate 2: Left of button
            {"left": btn_left - menu_width - MENU_GAP, "top": btn_cy - menu_height / 2.0},
            # Candidate 3: Below button
            {"left": btn_cx - menu_width / 2.0, "top": btn_b + MENU_GAP},
            # Candidate 4: Above button
            {"left": btn_cx - menu_width / 2.0, "top": btn_top - menu_height - MENU_GAP}
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

        arc_menu_card.left = final_left
        arc_menu_card.top = final_top
        arc_menu_card.right = None
        arc_menu_card.bottom = None

    def open_arc_menu():
        nonlocal arc_menu_open
        arc_menu_open = True
        arc_dim_dismiss.visible = True
        arc_menu_card.visible = True
        set_active_state()
        position_arc_menu()
        update_active_filter_display()
        page.update()

    def close_arc_menu():
        nonlocal arc_menu_open
        arc_menu_open = False
        arc_dim_dismiss.visible = False
        arc_menu_card.visible = False
        set_normal_state()
        page.update()

    def toggle_arc_menu():
        if arc_menu_open:
            close_arc_menu()
        else:
            open_arc_menu()

    is_drag_active = False
    drag_dist = 0.0
    last_toggle_time = 0.0

    def trigger_toggle(e=None):
        nonlocal last_toggle_time
        import time
        now = time.time()
        if now - last_toggle_time < 0.20:
            return
        last_toggle_time = now
        toggle_arc_menu()

    def get_pos_coord(val):
        if val is None:
            return None
        if hasattr(val, 'x') and hasattr(val, 'y'):
            return float(val.x), float(val.y)
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            return float(val[0]), float(val[1])
        return None

    def on_pan_start(e: ft.DragStartEvent):
        nonlocal is_drag_active, drag_dist, start_btn_left, start_btn_top, start_pointer_x, start_pointer_y
        is_drag_active = False
        drag_dist = 0.0
        start_btn_left = btn_left
        start_btn_top = btn_top
        coords = get_pos_coord(getattr(e, 'global_position', None)) or get_pos_coord(getattr(e, 'local_position', None))
        if coords:
            start_pointer_x, start_pointer_y = coords
        else:
            start_pointer_x, start_pointer_y = 0.0, 0.0

    def on_pan_update(e: ft.DragUpdateEvent):
        nonlocal btn_left, btn_top, is_drag_active, drag_dist
        curr_coords = get_pos_coord(getattr(e, 'global_position', None))
        if curr_coords and (start_pointer_x != 0.0 or start_pointer_y != 0.0):
            offset_x = curr_coords[0] - start_pointer_x
            offset_y = curr_coords[1] - start_pointer_y
        else:
            delta = get_pos_coord(getattr(e, 'global_delta', None)) or get_pos_coord(getattr(e, 'local_delta', None))
            if delta:
                offset_x, offset_y = delta[0], delta[1]
            else:
                offset_x, offset_y = 0.0, 0.0

        drag_dist = (offset_x ** 2 + offset_y ** 2) ** 0.5

        if drag_dist > 4.0:
            if not is_drag_active:
                is_drag_active = True
                if arc_menu_open:
                    close_arc_menu()

        if is_drag_active:
            clamp_button_pos(start_btn_left + offset_x, start_btn_top + offset_y)
            arc_fab_wrapper.left = btn_left
            arc_fab_wrapper.top = btn_top
            if arc_fab_wrapper.page:
                arc_fab_wrapper.update()

    def on_pan_end(e: ft.DragEndEvent):
        nonlocal is_drag_active
        if not is_drag_active:
            trigger_toggle()
        is_drag_active = False

    def on_tap(e):
        if not is_drag_active:
            trigger_toggle()

    arc_fab_wrapper = ft.GestureDetector(
        content=arc_fab_container,
        left=btn_left,
        top=btn_top,
        drag_interval=10,
        on_pan_start=on_pan_start,
        on_pan_update=on_pan_update,
        on_pan_end=on_pan_end,
        on_tap=on_tap
    )

    arc_dim_dismiss = ft.Container(
        top=0, bottom=0, left=0, right=0,
        bgcolor=ft.Colors.TRANSPARENT,
        visible=False,
        on_click=lambda e: close_arc_menu()
    )

    def create_filter_badge(text, on_clear_fn):
        return ft.Container(
            content=ft.Row([
                ft.Text(
                    text,
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=ACCENT,
                    no_wrap=True
                ),
                ft.Icon(
                    ft.Icons.CLOSE_ROUNDED,
                    size=13,
                    color=ACCENT
                )
            ], tight=True, spacing=4, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.with_opacity(0.12, ACCENT),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.35, ACCENT)),
            border_radius=10,
            padding=ft.Padding(10, 0, 8, 0),
            height=36,
            alignment=ft.Alignment.CENTER,
            tooltip=f"Delete {text}",
            on_click=on_clear_fn
        )

    def create_default_badge(text, on_click_fn=None):
        return ft.Container(
            content=ft.Text(
                text,
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ACCENT,
                no_wrap=True
            ),
            bgcolor=ft.Colors.with_opacity(0.12, ACCENT),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.35, ACCENT)),
            border_radius=10,
            padding=ft.Padding(12, 0, 12, 0),
            height=36,
            alignment=ft.Alignment.CENTER,
            tooltip=text,
            on_click=on_click_fn
        )

    active_filters_row = ft.Row(
        controls=[create_default_badge("All Characters")],
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    active_filter_container = ft.Container(
        content=active_filters_row,
        height=36,
        expand=True,
        alignment=ft.Alignment.CENTER_LEFT
    )

    def clear_arc_filter(e=None):
        nonlocal selected_arc
        selected_arc = None
        update_active_filter_display()
        build_filter_list_items()
        apply_filters()

    def clear_df_filter(e=None):
        nonlocal selected_df
        selected_df = None
        update_active_filter_display()
        build_filter_list_items()
        apply_filters()

    def clear_race_filter(e=None):
        nonlocal selected_race
        selected_race = None
        update_active_filter_display()
        build_filter_list_items()
        apply_filters()

    def clear_mode_filter(e=None):
        nonlocal selected_mode
        selected_mode = None
        update_active_filter_display()
        build_filter_list_items()
        apply_filters()

    def clear_all_filters(e=None):
        nonlocal selected_arc, selected_df, selected_race, selected_mode
        selected_arc = None
        selected_df = None
        selected_race = None
        selected_mode = None
        update_active_filter_display()
        build_filter_list_items()
        apply_filters()

    def update_active_filter_display():
        active_filters_row.controls.clear()

        # Suggest/badge default dinamis sesuai kategori yang sedang dipilih
        if selected_category == "arcs":
            if selected_arc:
                active_filters_row.controls.append(create_filter_badge(selected_arc, clear_arc_filter))
            else:
                active_filters_row.controls.append(create_default_badge("All Characters", lambda e: clear_arc_filter(e)))
        elif selected_category == "devil_fruit":
            if selected_df:
                df_name = "No Fruit" if selected_df == "None" else selected_df
                active_filters_row.controls.append(create_filter_badge(df_name, clear_df_filter))
            else:
                active_filters_row.controls.append(create_default_badge("All Characters", lambda e: clear_df_filter(e)))
        elif selected_category == "race":
            if selected_race:
                active_filters_row.controls.append(create_filter_badge(selected_race, clear_race_filter))
            else:
                active_filters_row.controls.append(create_default_badge("All Characters", lambda e: clear_race_filter(e)))
        elif selected_category == "game_mode":
            if selected_mode:
                active_filters_row.controls.append(create_filter_badge(selected_mode, clear_mode_filter))
            else:
                active_filters_row.controls.append(create_default_badge("All Characters", lambda e: clear_mode_filter(e)))

        # Tampilkan juga badge filter aktif dari kategori lain (jika sudah ada filter yang dipilih)
        if selected_category != "arcs" and selected_arc:
            active_filters_row.controls.append(create_filter_badge(selected_arc, clear_arc_filter))

        if selected_category != "devil_fruit" and selected_df:
            df_name = "No Fruit" if selected_df == "None" else selected_df
            active_filters_row.controls.append(create_filter_badge(df_name, clear_df_filter))

        if selected_category != "race" and selected_race:
            active_filters_row.controls.append(create_filter_badge(selected_race, clear_race_filter))

        if selected_category != "game_mode" and selected_mode:
            active_filters_row.controls.append(create_filter_badge(selected_mode, clear_mode_filter))

        if active_filter_container.page:
            active_filter_container.update()

    category_labels = {
        "arcs": "Story Arcs",
        "devil_fruit": "Devil Fruit",
        "race": "Race",
        "game_mode": "Game Mode",
    }

    category_label_text = ft.Text(
        category_labels["arcs"],
        size=11,
        weight=ft.FontWeight.BOLD,
        color=get_text_main(),
        no_wrap=True
    )

    category_container = ft.Container(
        content=ft.Row([
            category_label_text,
            ft.Icon(ft.Icons.ARROW_DROP_DOWN_ROUNDED, size=18, color=ACCENT)
        ], tight=True, spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=get_card_bg(),
        border=get_modern_border(),
        border_radius=10,
        padding=ft.Padding(12, 0, 8, 0),
        height=36,
        alignment=ft.Alignment.CENTER,
    )

    category_dropdown_wrapper = ft.Container(
        content=category_container,
        padding=ft.Padding(0, 0, 0, 4),
    )

    def on_category_select(cat_key):
        nonlocal selected_category
        selected_category = cat_key
        category_label_text.value = category_labels.get(cat_key, "Category")
        arc_search_input.value = ""
        if selected_category == "arcs":
            arc_search_input.hint_text = "Search arcs (Wano, Alabasta...)"
        elif selected_category == "devil_fruit":
            arc_search_input.hint_text = "Search fruit (Zoan, Logia, Mera...)"
        elif selected_category == "race":
            arc_search_input.hint_text = "Search race (Human, Fish-man, Mink...)"
        elif selected_category == "game_mode":
            arc_search_input.hint_text = "Search mode (Easy, Medium, Hard...)"
        update_active_filter_display()
        build_filter_list_items()
        page.update()

    category_menu_items_text = [
        ft.Text("Story Arcs", size=12, weight=ft.FontWeight.W_500, color=get_text_main()),
        ft.Text("Devil Fruit", size=12, weight=ft.FontWeight.W_500, color=get_text_main()),
        ft.Text("Race", size=12, weight=ft.FontWeight.W_500, color=get_text_main()),
        ft.Text("Game Mode", size=12, weight=ft.FontWeight.W_500, color=get_text_main()),
    ]

    category_dropdown = ft.PopupMenuButton(
        content=category_dropdown_wrapper,
        menu_position=ft.PopupMenuPosition.UNDER,
        padding=0,
        bgcolor=get_card_bg(),
        shape=ft.RoundedRectangleBorder(
            radius=12,
            side=ft.BorderSide(1, ft.Colors.with_opacity(0.3, ACCENT) if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.with_opacity(0.2, ACCENT))
        ),
        elevation=0,
        shadow_color=ft.Colors.TRANSPARENT,
        items=[
            ft.PopupMenuItem(
                content=category_menu_items_text[0],
                on_click=lambda e: on_category_select("arcs")
            ),
            ft.PopupMenuItem(
                content=category_menu_items_text[1],
                on_click=lambda e: on_category_select("devil_fruit")
            ),
            ft.PopupMenuItem(
                content=category_menu_items_text[2],
                on_click=lambda e: on_category_select("race")
            ),
            ft.PopupMenuItem(
                content=category_menu_items_text[3],
                on_click=lambda e: on_category_select("game_mode")
            ),
        ],
        tooltip="Select Category",
    )

    arc_search_input = ft.TextField(
        hint_text="Search arcs (Wano, Alabasta...)",
        prefix_icon=ft.Icons.SEARCH,
        border=ft.OutlineInputBorder(border_radius=12, side=ft.BorderSide(color=ft.Colors.TRANSPARENT)),
        content_padding=ft.Padding(10, 8, 10, 8),
        text_size=12,
        height=38,
        bgcolor=DARK_BG if page.theme_mode == ft.ThemeMode.DARK else LIGHT_BG,
        color=get_text_main(),
        on_change=lambda e: build_filter_list_items()
    )

    arc_list_col = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, expand=True)

    def select_filter(category, item_value):
        nonlocal selected_arc, selected_df, selected_race, selected_mode
        if category == "arcs":
            selected_arc = item_value
        elif category == "devil_fruit":
            selected_df = item_value
        elif category == "race":
            selected_race = item_value
        elif category == "game_mode":
            selected_mode = item_value

        update_active_filter_display()
        build_filter_list_items()
        apply_filters()

    def make_filter_item(title, count, is_selected, on_click_fn, icon=ft.Icons.AUTO_AWESOME_ROUNDED, badge_label=None, badge_color=ACCENT):
        title_controls = [
            ft.Text(
                title,
                size=13,
                weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.W_500,
                color=ACCENT if is_selected else get_text_main(),
                overflow=ft.TextOverflow.ELLIPSIS,
                max_lines=1
            )
        ]
        if badge_label:
            title_controls.append(
                ft.Container(
                    content=ft.Text(badge_label, size=9, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    bgcolor=badge_color,
                    padding=ft.Padding(6, 2, 6, 2),
                    border_radius=10
                )
            )

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(
                        icon,
                        size=16,
                        color=ACCENT if is_selected else get_text_muted()
                    ),
                    width=32,
                    height=32,
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.15, ACCENT) if is_selected else (ft.Colors.with_opacity(0.06, ft.Colors.WHITE) if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLACK_12),
                    alignment=ft.Alignment.CENTER
                ),
                ft.Column([
                    ft.Row(title_controls, spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Text(
                        f"Total {count} characters (No filter)" if title in ("All Characters", "All Character") else (f"{count} character" if count == 1 else f"{count} characters"),
                        size=10,
                        color=get_text_muted()
                    )
                ], spacing=2, expand=True),
                ft.Icon(ft.Icons.CHECK_ROUNDED, color=ACCENT, size=16, visible=is_selected)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.with_opacity(0.12, ACCENT) if is_selected else ft.Colors.TRANSPARENT,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.3, ACCENT) if is_selected else ft.Colors.TRANSPARENT),
            border_radius=12,
            padding=ft.Padding(10, 8, 10, 8),
            on_click=on_click_fn,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )

    def build_filter_list_items():
        arc_list_col.controls.clear()
        search_filter = (arc_search_input.value or "").strip().lower()

        if selected_category == "arcs":
            # Base pool contextual to active devil_fruit, race, and game_mode
            base_pool = [
                c for c in all_characters
                if (not selected_race or (c.get('race') or 'Unknown').strip() == selected_race)
                and matches_df_filter(c, selected_df)
                and matches_game_mode_filter(c, selected_mode)
            ]
            dynamic_arc_counts = Counter(get_story_arc(c.get('first_appearance_arc')) for c in base_pool)

            # Item 0: All Characters
            if not search_filter or any(kw in search_filter for kw in ["all", "character", "semua"]):
                is_all_selected = selected_arc is None
                arc_list_col.controls.append(
                    make_filter_item(
                        "All Characters",
                        len(base_pool),
                        is_all_selected,
                        lambda e: select_filter("arcs", None),
                        icon=ft.Icons.PEOPLE_ALT_ROUNDED
                    )
                )

            for arc in ARC_ORDER:
                if search_filter and search_filter not in arc.lower():
                    continue
                count = dynamic_arc_counts.get(arc, 0)
                is_selected = selected_arc == arc
                arc_list_col.controls.append(
                    make_filter_item(
                        arc,
                        count,
                        is_selected,
                        lambda e, a=arc: select_filter("arcs", a),
                        icon=ft.Icons.AUTO_AWESOME_ROUNDED
                    )
                )

        elif selected_category == "devil_fruit":
            # Base pool contextual to active arc, race, and game_mode
            base_pool = [
                c for c in all_characters
                if (not selected_arc or get_story_arc(c.get('first_appearance_arc')) == selected_arc)
                and (not selected_race or (c.get('race') or 'Unknown').strip() == selected_race)
                and matches_game_mode_filter(c, selected_mode)
            ]

            # Item 0: All Characters
            if not search_filter or any(kw in search_filter for kw in ["all", "character", "semua"]):
                is_all_selected = selected_df is None
                arc_list_col.controls.append(
                    make_filter_item(
                        "All Characters",
                        len(base_pool),
                        is_all_selected,
                        lambda e: select_filter("devil_fruit", None),
                        icon=ft.Icons.PEOPLE_ALT_ROUNDED
                    )
                )

            # Main Fruit Types
            fruit_types = [
                ("Zoan", sum(1 for c in base_pool if matches_df_filter(c, 'Zoan')), ft.Icons.PETS_ROUNDED),
                ("Paramecia", sum(1 for c in base_pool if matches_df_filter(c, 'Paramecia')), ft.Icons.AUTO_AWESOME_ROUNDED),
                ("Logia", sum(1 for c in base_pool if matches_df_filter(c, 'Logia')), ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED),
                ("None", sum(1 for c in base_pool if matches_df_filter(c, 'None')), ft.Icons.SHIELD_OUTLINED),
            ]

            for key, count, icon in fruit_types:
                title = "No Devil Fruit" if key == "None" else f"{key} Type"
                if search_filter and (search_filter not in key.lower() and search_filter not in title.lower()):
                    continue
                is_selected = selected_df == key
                arc_list_col.controls.append(
                    make_filter_item(
                        title,
                        count,
                        is_selected,
                        lambda e, k=key: select_filter("devil_fruit", k),
                        icon=icon
                    )
                )

            # Top specific fruits or matching fruits in base_pool
            df_pool_fruits = []
            for c in base_pool:
                raw = c.get('devil_fruit')
                items = raw if isinstance(raw, list) else ([raw] if raw else [])
                for it in items:
                    clean = re.sub(r'\s*\([^)]*awakened[^)]*\)', '', str(it), flags=re.IGNORECASE).strip()
                    if clean and clean.lower() not in ['none', 'unknown']:
                        df_pool_fruits.append(clean)
            dynamic_df_fruit_counts = Counter(df_pool_fruits)

            sorted_fruits = sorted(dynamic_df_fruit_counts.items(), key=lambda x: (-x[1], x[0]))
            matching_fruits = [
                (fn, cnt) for fn, cnt in sorted_fruits
                if not search_filter or search_filter in fn.lower()
            ]

            if matching_fruits:
                arc_list_col.controls.append(
                    ft.Container(
                        content=ft.Text("SPECIFIC FRUITS", size=10, weight=ft.FontWeight.BOLD, color=get_text_muted()),
                        padding=ft.Padding(6, 8, 6, 2)
                    )
                )
                for fn, cnt in matching_fruits[:50]:
                    is_selected = selected_df == fn
                    f_type = get_devil_fruit_type(fn)
                    arc_list_col.controls.append(
                        make_filter_item(
                            fn,
                            cnt,
                            is_selected,
                            lambda e, f_name=fn: select_filter("devil_fruit", f_name),
                            icon=ft.Icons.AUTO_AWESOME_OUTLINED,
                            badge_label=f_type.upper() if f_type else None
                        )
                    )

        elif selected_category == "race":
            # Base pool contextual to active arc, devil_fruit, and game_mode
            base_pool = [
                c for c in all_characters
                if (not selected_arc or get_story_arc(c.get('first_appearance_arc')) == selected_arc)
                and matches_df_filter(c, selected_df)
                and matches_game_mode_filter(c, selected_mode)
            ]
            dynamic_race_counts = Counter((c.get('race') or 'Unknown').strip() for c in base_pool)

            # Item 0: All Characters
            if not search_filter or any(kw in search_filter for kw in ["all", "character", "semua"]):
                is_all_selected = selected_race is None
                arc_list_col.controls.append(
                    make_filter_item(
                        "All Characters",
                        len(base_pool),
                        is_all_selected,
                        lambda e: select_filter("race", None),
                        icon=ft.Icons.PEOPLE_ALT_ROUNDED
                    )
                )

            all_known_races = sorted(race_counts.keys())
            sorted_races = sorted(all_known_races, key=lambda r: (-dynamic_race_counts.get(r, 0), r))

            for r_name in sorted_races:
                if not r_name or r_name == "Unknown":
                    continue
                count = dynamic_race_counts.get(r_name, 0)
                if search_filter and search_filter not in r_name.lower():
                    continue
                is_selected = selected_race == r_name
                arc_list_col.controls.append(
                    make_filter_item(
                        r_name,
                        count,
                        is_selected,
                        lambda e, r=r_name: select_filter("race", r),
                        icon=ft.Icons.PERSON_ROUNDED
                    )
                )

        elif selected_category == "game_mode":
            # Base pool contextual to active arc, devil_fruit, and race
            base_pool = [
                c for c in all_characters
                if (not selected_arc or get_story_arc(c.get('first_appearance_arc')) == selected_arc)
                and matches_df_filter(c, selected_df)
                and (not selected_race or (c.get('race') or 'Unknown').strip() == selected_race)
            ]

            # Item 0: All Characters
            if not search_filter or any(kw in search_filter for kw in ["all", "character", "semua", "mode"]):
                is_all_selected = selected_mode is None
                arc_list_col.controls.append(
                    make_filter_item(
                        "All Characters",
                        len(base_pool),
                        is_all_selected,
                        lambda e: select_filter("game_mode", None),
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
                is_selected = selected_mode == mode_name
                arc_list_col.controls.append(
                    make_filter_item(
                        mode_name,
                        count,
                        is_selected,
                        lambda e, m=mode_name: select_filter("game_mode", m),
                        icon=mode_icon
                    )
                )

        if arc_list_col.page:
            arc_list_col.update()

    arc_menu_card = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("CHARACTER FILTER", size=10, weight=ft.FontWeight.BOLD, color=get_text_muted()),
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.RESTART_ALT_ROUNDED,
                                icon_size=18,
                                icon_color=get_text_muted(),
                                tooltip="Clear Suggest",
                                on_click=lambda e: clear_all_filters()
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=18,
                                icon_color=get_text_muted(),
                                tooltip="Close",
                                on_click=lambda e: close_arc_menu()
                            )
                        ], spacing=4, alignment=ft.CrossAxisAlignment.CENTER)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([
                        category_dropdown,
                        active_filter_container
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START)
                ], spacing=10),
                padding=ft.Padding(16, 14, 16, 4)
            ),
            ft.Container(
                content=arc_search_input,
                padding=ft.Padding(14, 4, 14, 10)
            ),
            ft.Container(
                height=1,
                bgcolor=ft.Colors.with_opacity(0.1, DARK_TEXT_MUTED if page.theme_mode == ft.ThemeMode.DARK else LIGHT_TEXT_MUTED)
            ),
            ft.Container(
                content=arc_list_col,
                expand=True,
                padding=ft.Padding(10, 6, 10, 10)
            )
        ], spacing=0),
        width=340,
        height=480,
        border_radius=22,
        bgcolor=get_card_bg(),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.3, ACCENT) if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.with_opacity(0.4, ACCENT)),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=40,
            color=ft.Colors.with_opacity(0.25, "#0f172a"),
            offset=ft.Offset(0, 12)
        ),
        left=btn_left,
        top=btn_top,
        visible=False
    )

    main_stack = ft.Stack([
        root_scroll_col,
        footer_fixed,
        arc_dim_dismiss,
        arc_menu_card,
        arc_fab_wrapper,
    ], expand=True)

    page.add(main_stack)

    try:
        load_devil_fruits_types()
        resp = requests.get(API_URL)
        if resp.status_code == 200:
            all_characters = resp.json()
            filtered_characters = all_characters
            loading_container.visible = False
            pagination_row.visible = True

            arc_counts = Counter(get_story_arc(c.get('first_appearance_arc')) for c in all_characters)
            race_counts = Counter((c.get('race') or 'Unknown').strip() for c in all_characters)

            zoan_c = sum(1 for c in all_characters if matches_df_filter(c, 'Zoan'))
            paramecia_c = sum(1 for c in all_characters if matches_df_filter(c, 'Paramecia'))
            logia_c = sum(1 for c in all_characters if matches_df_filter(c, 'Logia'))
            no_fruit_c = sum(1 for c in all_characters if matches_df_filter(c, 'None'))
            df_type_counts = {
                'Zoan': zoan_c,
                'Paramecia': paramecia_c,
                'Logia': logia_c,
                'None': no_fruit_c
            }

            f_list = []
            for c in all_characters:
                raw = c.get('devil_fruit')
                items = raw if isinstance(raw, list) else ([raw] if raw else [])
                for it in items:
                    clean = re.sub(r'\s*\([^)]*awakened[^)]*\)', '', str(it), flags=re.IGNORECASE).strip()
                    if clean and clean.lower() not in ['none', 'unknown']:
                        f_list.append(clean)
            df_fruit_counts = Counter(f_list)

            build_filter_list_items()

            # Trigger resize once to layout columns
            on_page_resize(None)
        else:
            loading_text.value = "Failed to load characters."
            page.update()
    except Exception as e:
        loading_text.value = f"Error: {e}"
        page.update()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
