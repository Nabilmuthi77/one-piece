import re
import flet as ft
from constants import BASE_IMG_URL
from utils.theme import ThemeColors
from utils.helpers import get_devil_fruit_type, format_bounty, format_haki

def open_character_modal(page: ft.Page, char: dict, on_lock_click, unfocus_target=None) -> ft.AlertDialog:
    if unfocus_target and hasattr(unfocus_target, "focus"):
        async def unfocus_hack():
            try:
                res = unfocus_target.focus()
                if hasattr(res, "__await__"):
                    await res
            except Exception:
                pass
        page.run_task(unfocus_hack)

    def close_this(e):
        dlg.open = False
        page.update()

    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = ThemeColors(is_dark=is_dark)

    img_src = BASE_IMG_URL + char.get('image', '') if char.get('image') else 'https://via.placeholder.com/400x500?text=No+Image'
    status = char.get('status', 'Unknown')
    status_lower = str(status).strip().lower()
    if status_lower == 'alive':
        status_color = colors.text_primary
    elif status_lower in ('deceased', 'mati', 'dead'):
        status_color = ft.Colors.RED_500 if not is_dark else ft.Colors.RED_400
    else:
        status_color = colors.text_secondary

    item_bg = ft.Colors.WHITE if not is_dark else colors.card_surface
    item_shadow = colors.raised_shadow(depth=2, blur=6) if not is_dark else colors.raised_shadow(depth=1, blur=4)
    item_border = None

    def info_item(label, value):
        return ft.Container(
            content=ft.Column([
                ft.Text(label.upper(), size=11, color=colors.text_secondary, weight=ft.FontWeight.BOLD),
                ft.Text(str(value), size=14, color=colors.text_primary, weight=ft.FontWeight.W_600)
            ], spacing=4),
            bgcolor=item_bg,
            shadow=item_shadow,
            border=item_border,
            padding=ft.Padding(left=16, right=16, top=10, bottom=10),
            border_radius=14,
            width=float('inf')
        )

    def devil_fruit_item(char):
        raw_fruit = char.get('devil_fruit')
        if not raw_fruit or str(raw_fruit).strip().lower() in ['none', 'unknown', '']:
            return ft.Container(
                content=ft.Column([
                    ft.Text('DEVIL FRUIT', size=11, color=colors.text_secondary, weight=ft.FontWeight.BOLD),
                    ft.Text('None', size=14, color=colors.text_primary, weight=ft.FontWeight.W_600)
                ], spacing=4),
                bgcolor=item_bg,
                shadow=item_shadow,
                border=item_border,
                padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                border_radius=14,
                width=float('inf')
            )

        fruit_list = raw_fruit if isinstance(raw_fruit, list) else [raw_fruit]
        fruit_list = [str(f).strip() for f in fruit_list if str(f).strip() and str(f).strip().lower() not in ['none', 'unknown', '']]

        if not fruit_list:
            return ft.Container(
                content=ft.Column([
                    ft.Text('DEVIL FRUIT', size=11, color=colors.text_secondary, weight=ft.FontWeight.BOLD),
                    ft.Text('None', size=14, color=colors.text_primary, weight=ft.FontWeight.W_600)
                ], spacing=4),
                bgcolor=item_bg,
                shadow=item_shadow,
                border=item_border,
                padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                border_radius=14,
                width=float('inf')
            )

        char_name = str(char.get('name', '')).lower()
        fruit_rows = []

        for f_str in fruit_list:
            is_awakened = bool(re.search(r'awakened', f_str, re.IGNORECASE)) or ('luffy' in char_name)
            clean_name = re.sub(r'\s*\(\s*Awakened\s*\)', '', f_str, flags=re.IGNORECASE).strip()
            f_type = get_devil_fruit_type(clean_name)
            formatted_name = clean_name.replace(', ', ' -- ')

            row_controls = []
            if f_type:
                # Neumorphic pill badge for fruit type using my-life accent
                row_controls.append(
                    ft.Container(
                        content=ft.Text(
                            f_type.upper(),
                            size=11,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD
                        ),
                        bgcolor=colors.accent_primary,
                        shadow=colors.subtle_shadow(depth=1, blur=3),
                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                        border_radius=12
                    )
                )

            if is_awakened:
                # Awakening badge
                row_controls.append(
                    ft.Container(
                        content=ft.Text(
                            "AWAKENING",
                            size=11,
                            color="#071A20" if not is_dark else "#FFFFFF",
                            weight=ft.FontWeight.BOLD
                        ),
                        bgcolor="#FFFFFF" if not is_dark else colors.card_elevated,
                        shadow=colors.subtle_shadow(depth=1, blur=3),
                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                        border_radius=12
                    )
                )

            prefix = "-- " if (f_type or is_awakened) else ""
            row_controls.append(
                ft.Text(
                    f"{prefix}{formatted_name}",
                    size=14,
                    color=colors.text_primary,
                    weight=ft.FontWeight.W_600
                )
            )

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
                ft.Text('DEVIL FRUIT', size=11, color=colors.text_secondary, weight=ft.FontWeight.BOLD),
                *fruit_rows
            ], spacing=6),
            bgcolor=item_bg,
            shadow=item_shadow,
            border=item_border,
            padding=ft.Padding(left=16, right=16, top=10, bottom=10),
            border_radius=14,
            width=float('inf')
        )

    # Neumorphic close button shadow: thin bright highlight on top-left, dark shadow on bottom-right
    close_shadow = [
        ft.BoxShadow(
            spread_radius=0,
            blur_radius=2,
            color=colors.shadow_bright if is_dark else ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
            offset=ft.Offset(-1, -1),
        ),
        ft.BoxShadow(
            spread_radius=0,
            blur_radius=5,
            color=colors.shadow_dark if is_dark else ft.Colors.BLACK_38,
            offset=ft.Offset(2, 2.5),
        ),
    ]

    # Tactile Neumorphic close button on top right of the hero image
    close_button = ft.Container(
        content=ft.Icon(ft.Icons.CLOSE_ROUNDED, size=18, color=colors.text_primary),
        width=38,
        height=38,
        border_radius=19,
        bgcolor=ft.Colors.WHITE if not is_dark else colors.card_surface,
        shadow=close_shadow,
        alignment=ft.Alignment(0, 0),
        on_click=close_this,
        tooltip="Close"
    )

    # Tactile Neumorphic lock button next to character name (bulat / circular)
    lock_button = ft.Container(
        content=ft.Icon(ft.Icons.LOCK_ROUNDED, size=18, color=colors.accent_primary),
        width=38,
        height=38,
        border_radius=19,
        bgcolor=ft.Colors.WHITE if not is_dark else colors.card_surface,
        border=None,
        shadow=colors.subtle_shadow(depth=1, blur=3),
        alignment=ft.Alignment(0, 0),
        on_click=lambda e, src=img_src, n=char.get('name', 'Unknown'): on_lock_click(src, n),
        tooltip="Lock View"
    )

    # Tactile Neumorphic name wrap card - width snugly fits character name, height 38px aligned with lock_button
    name_card = ft.Container(
        content=ft.Row([
            ft.Text(
                char.get('name', 'Unknown'),
                size=18,
                weight=ft.FontWeight.BOLD,
                color=colors.text_primary,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS
            )
        ], tight=True, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=item_bg,
        shadow=colors.subtle_shadow(depth=1, blur=3),
        border=None,
        padding=ft.Padding(left=16, right=16, top=0, bottom=0),
        border_radius=14,
        height=38,
    )

    # Compact Soft Neumorphic status badge
    status_badge = ft.Container(
        content=ft.Row([
            ft.Container(
                width=6,
                height=6,
                border_radius=3,
                bgcolor=status_color
            ),
            ft.Text(status.upper(), color=status_color, weight=ft.FontWeight.BOLD, size=10)
        ], tight=True, spacing=5, alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.Padding(9, 4, 9, 4),
        border_radius=10,
        bgcolor=item_bg,
        shadow=colors.subtle_shadow(depth=1, blur=2),
        border=None,
    )

    inner_card = ft.Container(
        content=ft.Column([
            ft.Stack([
                ft.Container(
                    content=ft.Image(src=img_src, height=250, fit=ft.BoxFit.COVER),
                    width=float('inf'),
                    border_radius=ft.BorderRadius(top_left=18, top_right=18, bottom_left=0, bottom_right=0),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                ),
                ft.Container(
                    content=close_button,
                    top=12,
                    right=12
                )
            ]),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Row([name_card], alignment=ft.MainAxisAlignment.START, tight=True),
                            expand=True,
                            alignment=ft.Alignment.CENTER_LEFT,
                        ),
                        lock_button
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    ft.Row([status_badge], alignment=ft.MainAxisAlignment.START),
                    info_item("Bounty", format_bounty(char.get('bounty'))),
                    info_item("Haki Types", format_haki(char.get('haki'))),
                    devil_fruit_item(char),
                    info_item("Affiliation", char.get('affiliation', 'None')),
                    info_item("Origin", char.get('origin', 'Unknown')),
                    info_item("Race", char.get('race', 'Unknown')),
                    info_item("First Appearance", char.get('first_appearance_arc', 'Unknown')),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("DESCRIPTION", size=11, color=colors.text_secondary, weight=ft.FontWeight.BOLD),
                            ft.Text(char.get('description', 'No description available.'), size=14, color=colors.text_primary)
                        ], spacing=5),
                        bgcolor=item_bg,
                        shadow=item_shadow,
                        border=item_border,
                        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                        border_radius=14,
                        width=float('inf')
                    )
                ], spacing=12),
                padding=18
            )
        ], scroll=ft.ScrollMode.HIDDEN, tight=True, spacing=0),
        border_radius=20,
        bgcolor="#EEF2F6" if not is_dark else colors.pressed_surface,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS
    )

    # Tactile Neumorphic Frame wrap (bingkai luar neumorphic)
    frame_shadow = [
        ft.BoxShadow(
            spread_radius=1,
            blur_radius=18,
            color="#CBD5E1" if not is_dark else colors.shadow_dark,
            offset=ft.Offset(8, 8),
        ),
        ft.BoxShadow(
            spread_radius=0 if is_dark else 1,
            blur_radius=18,
            color="#FFFFFF" if not is_dark else colors.shadow_bright,
            offset=ft.Offset(-6, -6) if is_dark else ft.Offset(-8, -8),
        ),
    ]

    modal_frame = ft.Container(
        content=inner_card,
        width=580,
        border_radius=28,
        bgcolor="#EEF2F6" if not is_dark else colors.card_surface,
        padding=ft.Padding.all(10),
        shadow=frame_shadow,
    )

    dlg = ft.AlertDialog(
        content=modal_frame,
        content_padding=0,
        inset_padding=ft.Padding.symmetric(horizontal=16, vertical=24),
        bgcolor="transparent",
        shape=ft.RoundedRectangleBorder(radius=28)
    )

    page.show_dialog(dlg)
    return dlg
