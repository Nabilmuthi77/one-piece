import flet as ft
import requests
import math

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

def main(page: ft.Page):
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
            
        if page.height:
            pass # we no longer need min_height hack
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

    def do_search():
        nonlocal current_page, filtered_characters
        query = search_input.value.lower()
        filtered_characters = [c for c in all_characters if query in c.get('name', '').lower()]
        current_page = 1
        render_page()

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
        return ', '.join(res)

    dlg = ft.AlertDialog(content=ft.Container(), content_padding=0, shape=ft.RoundedRectangleBorder(radius=24))

    def close_fs(e):
        nonlocal is_locked
        is_locked = False
        try:
            page.window.prevent_display_sleep = False
        except:
            pass
        page.window.full_screen = False
        page.pop_dialog()

    def enforce_lock(e):
        # Prevent Android back button from dismissing dialog while locked
        if is_locked:
            page.show_dialog(fs_dlg)
            page.update()

    is_locked = False
    def toggle_lock(e):
        nonlocal is_locked
        if is_locked:
            close_fs(e)
        else:
            is_locked = True
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
            fs_close_btn.visible = False
            fs_image_container.border = ft.Border.all(12, ft.Colors.BLUE_500)
            page.update()

    fs_dlg_image = ft.Image(src="", fit=ft.BoxFit.CONTAIN, border_radius=12)
    fs_image_container = ft.Container(content=fs_dlg_image, padding=0, border_radius=24, clip_behavior=ft.ClipBehavior.ANTI_ALIAS)
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
    fs_close_btn = ft.IconButton(
        icon=ft.Icons.CLOSE_ROUNDED, 
        on_click=close_fs, 
        icon_color=ft.Colors.WHITE, 
        icon_size=24, 
        tooltip="Close Fullscreen",
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.with_opacity(0.6, "#334155"),
            shape=ft.CircleBorder(),
            padding=12
        )
    )

    fs_dlg_name = ft.Text("", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER)
    fs_dlg = ft.AlertDialog(
        content=ft.Container(
            content=ft.Stack([
                ft.Container(
                    content=ft.Stack([
                        fs_image_container,
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Container(
                                        content=fs_dlg_name,
                                        bgcolor=ft.Colors.BLUE_500,
                                        padding=ft.Padding(left=30, right=30, top=10, bottom=10),
                                        border_radius=30,
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            bottom=-25, left=0, right=0
                        )
                    ], clip_behavior=ft.ClipBehavior.NONE),
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                    top=0, bottom=0, left=0, right=0
                ),
                ft.Container(
                    content=ft.Row([lock_btn, fs_close_btn], alignment=ft.MainAxisAlignment.END, spacing=0),
                    alignment=ft.Alignment.TOP_RIGHT,
                    padding=ft.Padding(20, 50, 20, 20),
                    top=0, right=0, left=0
                )
            ], expand=True),
            bgcolor=ft.Colors.BLACK,
        ),
        content_padding=0,
        inset_padding=0,
        modal=True,
        on_dismiss=enforce_lock
    )

    def open_fs_locked(img_src, name):
        nonlocal is_locked
        fs_dlg_image.src = img_src
        fs_dlg_name.value = name
        is_locked = True
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
        fs_close_btn.visible = False
        fs_image_container.border = ft.Border.all(12, ft.Colors.BLUE_500)
        page.window.full_screen = True
        fs_dlg.content.width = page.width
        fs_dlg.content.height = page.height
        page.show_dialog(fs_dlg)
        page.update()

    def close_modal(e):
        page.pop_dialog()

    def open_modal(char):
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
                        on_click=close_modal, 
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
                        ft.Text(char.get('name', 'Unknown'), size=32, weight=ft.FontWeight.BOLD, color=get_text_main()),
                        ft.IconButton(icon=ft.Icons.LOCK_ROUNDED, on_click=lambda e: open_fs_locked(img_src, char.get('name', 'Unknown')), tooltip="Lock View", icon_color=get_text_muted())
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

        dlg.content_padding = 0
        dlg.bgcolor = get_card_bg()
        dlg.content = ft.Container(content, width=600)
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

    main_stack = ft.Stack([
        root_scroll_col,
        footer_fixed
    ], expand=True)

    page.add(main_stack)

    try:
        resp = requests.get(API_URL)
        if resp.status_code == 200:
            all_characters = resp.json()
            filtered_characters = all_characters
            loading_container.visible = False
            pagination_row.visible = True
            
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
