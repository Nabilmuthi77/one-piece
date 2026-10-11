import flet as ft
import requests
import math
import re
from collections import Counter

API_URL = 'https://oparchive.com/data/characters.json'
BASE_IMG_URL = 'https://oparchive.com'

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
            build_arc_list_items()
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

    selected_arc = None
    arc_counts = {}

    def apply_filters():
        nonlocal current_page, filtered_characters
        query = (search_input.value or "").strip().lower()
        if not query and not selected_arc:
            filtered_characters = all_characters
        else:
            filtered_characters = [
                c for c in all_characters
                if (not query or query in c.get('name', '').lower())
                and (not selected_arc or get_story_arc(c.get('first_appearance_arc')) == selected_arc)
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
        bgcolor=ft.Colors.BLACK,
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
            bgcolor=ft.Colors.BLACK,
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
        tooltip="Filter Arc (Story Arcs)"
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
        menu_width = min(320.0, max(260.0, curr_pw - (VIEWPORT_MARGIN * 2)))
        menu_height = min(460.0, max(300.0, curr_ph - 100))
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

    active_arc_text = ft.Text(
        "Semua Arc",
        size=11,
        weight=ft.FontWeight.W_600,
        color=ACCENT
    )

    arc_search_input = ft.TextField(
        hint_text="Cari arc (Wano, Alabasta...)",
        prefix_icon=ft.Icons.SEARCH,
        border=ft.OutlineInputBorder(border_radius=12, side=ft.BorderSide(color=ft.Colors.TRANSPARENT)),
        content_padding=ft.Padding(10, 8, 10, 8),
        text_size=12,
        height=38,
        bgcolor=DARK_BG if page.theme_mode == ft.ThemeMode.DARK else LIGHT_BG,
        color=get_text_main(),
        on_change=lambda e: build_arc_list_items()
    )

    arc_list_col = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, expand=True)

    def select_arc(arc_name):
        nonlocal selected_arc
        selected_arc = arc_name
        active_arc_text.value = selected_arc if selected_arc else "Semua Arc"
        build_arc_list_items()
        apply_filters()
        close_arc_menu()

    def build_arc_list_items():
        arc_list_col.controls.clear()
        search_filter = (arc_search_input.value or "").strip().lower()

        # Item 0: All Arcs
        if not search_filter or "semua" in search_filter or "all" in search_filter:
            is_all_selected = selected_arc is None
            all_item = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.PUBLIC_ROUNDED,
                            size=16,
                            color=ACCENT if is_all_selected else get_text_muted()
                        ),
                        width=32,
                        height=32,
                        border_radius=8,
                        bgcolor=ft.Colors.with_opacity(0.15, ACCENT) if is_all_selected else (ft.Colors.with_opacity(0.06, ft.Colors.WHITE) if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLACK_12),
                        alignment=ft.Alignment.CENTER
                    ),
                    ft.Column([
                        ft.Text("Semua Arc", size=13, weight=ft.FontWeight.BOLD if is_all_selected else ft.FontWeight.W_500, color=ACCENT if is_all_selected else get_text_main()),
                        ft.Text(f"{len(all_characters)} karakter", size=10, color=get_text_muted())
                    ], spacing=1, expand=True),
                    ft.Icon(ft.Icons.CHECK_ROUNDED, color=ACCENT, size=16, visible=is_all_selected)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.with_opacity(0.12, ACCENT) if is_all_selected else ft.Colors.TRANSPARENT,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.3, ACCENT) if is_all_selected else ft.Colors.TRANSPARENT),
                border_radius=12,
                padding=ft.Padding(10, 8, 10, 8),
                on_click=lambda e: select_arc(None),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
            )
            arc_list_col.controls.append(all_item)

        for arc in ARC_ORDER:
            if search_filter and search_filter not in arc.lower():
                continue
            count = arc_counts.get(arc, 0)
            is_selected = selected_arc == arc
            item = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.AUTO_AWESOME_OUTLINED if not is_selected else ft.Icons.AUTO_AWESOME_ROUNDED,
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
                        ft.Text(arc, size=13, weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.W_500, color=ACCENT if is_selected else get_text_main()),
                        ft.Text(f"{count} karakter", size=10, color=get_text_muted())
                    ], spacing=1, expand=True),
                    ft.Icon(ft.Icons.CHECK_ROUNDED, color=ACCENT, size=16, visible=is_selected)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.with_opacity(0.12, ACCENT) if is_selected else ft.Colors.TRANSPARENT,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.3, ACCENT) if is_selected else ft.Colors.TRANSPARENT),
                border_radius=12,
                padding=ft.Padding(10, 8, 10, 8),
                on_click=lambda e, a=arc: select_arc(a),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
            )
            arc_list_col.controls.append(item)

        if arc_list_col.page:
            arc_list_col.update()

    arc_menu_card = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("FILTER KARAKTER", size=10, weight=ft.FontWeight.BOLD, color=get_text_muted()),
                        ft.Row([
                            ft.Text("Story Arcs", size=16, weight=ft.FontWeight.BOLD, color=get_text_main()),
                            ft.Container(
                                content=active_arc_text,
                                bgcolor=ft.Colors.with_opacity(0.12, ACCENT),
                                padding=ft.Padding(8, 2, 8, 2),
                                border_radius=10,
                                border=ft.Border.all(1, ft.Colors.with_opacity(0.3, ACCENT))
                            )
                        ], spacing=8, alignment=ft.CrossAxisAlignment.CENTER)
                    ], spacing=2, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=18,
                        icon_color=get_text_muted(),
                        on_click=lambda e: close_arc_menu()
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.Padding(16, 14, 16, 8)
            ),
            ft.Container(
                content=arc_search_input,
                padding=ft.Padding(14, 0, 14, 8)
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
        width=320,
        height=450,
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
        resp = requests.get(API_URL)
        if resp.status_code == 200:
            all_characters = resp.json()
            filtered_characters = all_characters
            loading_container.visible = False
            pagination_row.visible = True

            arc_counts = Counter(get_story_arc(c.get('first_appearance_arc')) for c in all_characters)
            build_arc_list_items()

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
