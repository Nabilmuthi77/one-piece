import asyncio
import flet as ft
from utils.theme import ThemeColors

class FullscreenViewerComponent:
    def __init__(self, page: ft.Page, on_reopen_modal=None, on_before_open=None):
        self.page = page
        self.on_reopen_modal = on_reopen_modal
        self.on_before_open = on_before_open
        self.is_locked = False

        self.wakelock = None
        try:
            self.wakelock = ft.Wakelock()
            if self.wakelock not in self.page.services:
                self.page.services.append(self.wakelock)
        except Exception as ex:
            print(f"Wakelock init error: {ex}")

        is_dark = page.theme_mode == ft.ThemeMode.DARK
        colors = ThemeColors(is_dark=is_dark)

        self.fs_dlg_image = ft.Image(src="", fit=ft.BoxFit.CONTAIN, border_radius=18)
        
        # Tactile Neumorphic image frame
        self.fs_image_container = ft.Container(
            content=self.fs_dlg_image,
            padding=ft.Padding.all(12),
            border_radius=28,
            bgcolor=colors.card_surface,
            shadow=colors.raised_shadow(depth=6, blur=18),
            border=None,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS
        )

        self.fs_name_text = ft.Text(
            "",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=colors.text_primary,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS
        )

        # Dark shadow pill badge for character title (no bright white glow onto image)
        self.pill_badge = ft.Container(
            content=ft.Row(
                [self.fs_name_text],
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=colors.card_surface,
            shadow=self._get_pill_shadow(colors),
            padding=ft.Padding(24, 10, 24, 10),
            border_radius=20,
            border=None
        )

        self.fs_image_stack = ft.Stack(
            controls=[
                self.fs_image_container,
                ft.Container(
                    content=self.pill_badge,
                    alignment=ft.Alignment(0, 1),
                    bottom=0, left=0, right=0,
                    offset=ft.Offset(0, 0.38)
                )
            ],
            clip_behavior=ft.ClipBehavior.NONE
        )

        # Circular Tactile Neumorphic lock / unlock button
        self.lock_btn_icon = ft.Icon(
            ft.Icons.LOCK_ROUNDED,
            size=20,
            color=colors.accent_primary
        )

        self.lock_btn = ft.Container(
            content=self.lock_btn_icon,
            width=46,
            height=46,
            border_radius=23,
            bgcolor=colors.card_surface,
            shadow=colors.raised_shadow(),
            alignment=ft.Alignment.CENTER,
            tooltip="Close / Unlock View",
            on_click=self.toggle_lock,
            animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT)
        )

        self.fs_overlay = ft.Container(
            content=ft.Stack([
                ft.Container(
                    content=self.fs_image_stack,
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                    top=0, bottom=0, left=0, right=0
                ),
                ft.Container(
                    content=ft.Row([self.lock_btn], alignment=ft.MainAxisAlignment.END, spacing=0),
                    alignment=ft.Alignment.TOP_RIGHT,
                    padding=ft.Padding(20, 50, 20, 20),
                    top=0, right=0, left=0
                )
            ], expand=True),
            bgcolor=colors.bg_main,
            expand=True,
            visible=False
        )

    async def open_fs_locked(self, img_src: str, name: str):
        if self.on_before_open:
            self.on_before_open()

        self.page.pop_dialog()
        await asyncio.sleep(0.1)

        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        colors = ThemeColors(is_dark=is_dark)

        self.fs_dlg_image.src = img_src
        self.fs_name_text.value = name
        self.fs_name_text.color = colors.text_primary
        self.is_locked = True

        if self.wakelock:
            try:
                await self.wakelock.enable()
            except Exception as ex:
                print(f"Wakelock error (enable): {ex}")
        try:
            self.page.window.prevent_display_sleep = True
        except Exception:
            pass

        self.fs_image_container.bgcolor = colors.card_surface
        self.fs_image_container.shadow = colors.raised_shadow(depth=6, blur=18)
        self.fs_image_container.border = None

        self.pill_badge.bgcolor = colors.card_surface
        self.pill_badge.shadow = self._get_pill_shadow(colors)

        self.lock_btn_icon.icon = ft.Icons.LOCK_ROUNDED
        self.lock_btn_icon.color = colors.accent_primary
        self.lock_btn.bgcolor = colors.card_surface
        self.lock_btn.shadow = colors.raised_shadow()

        self.fs_overlay.bgcolor = colors.bg_main
        self.page.window.full_screen = True

        self.fs_overlay.visible = True
        fs_view = ft.View(
            route="/fullscreen",
            controls=[self.fs_overlay],
            padding=0,
            bgcolor=colors.bg_main,
            can_pop=False,
            on_confirm_pop=lambda e: None,  # Block system back gesture / button completely
        )
        self.page.views.append(fs_view)
        self.page.update()

    async def close_fs(self, e=None):
        self.is_locked = False
        if self.wakelock:
            try:
                await self.wakelock.disable()
            except Exception as ex:
                print(f"Wakelock error (disable): {ex}")
        try:
            self.page.window.prevent_display_sleep = False
        except Exception:
            pass

        self.page.window.full_screen = False

        if len(self.page.views) > 1 and self.page.views[-1].route == "/fullscreen":
            self.page.views.pop()

        self.page.update()

        if self.on_reopen_modal:
            await asyncio.sleep(0.1)
            self.on_reopen_modal()

    async def toggle_lock(self, e=None):
        if self.is_locked:
            await self.close_fs(e)
        else:
            self.is_locked = True
            if self.wakelock:
                try:
                    await self.wakelock.enable()
                except Exception as ex:
                    print(f"Wakelock error (enable): {ex}")
            try:
                self.page.window.prevent_display_sleep = True
            except Exception:
                pass
            is_dark = self.page.theme_mode == ft.ThemeMode.DARK
            colors = ThemeColors(is_dark=is_dark)
            self.lock_btn_icon.icon = ft.Icons.LOCK_ROUNDED
            self.lock_btn_icon.color = colors.accent_primary
            self.lock_btn.bgcolor = colors.card_surface
            self.lock_btn.shadow = colors.raised_shadow()
            self.page.update()

    def _get_pill_shadow(self, colors: ThemeColors):
        return [
            ft.BoxShadow(
                spread_radius=1,
                blur_radius=12,
                color=colors.shadow_dark,
                offset=ft.Offset(0, 4),
            )
        ]

    def on_lifecycle(self, e):
        if e.data == ft.AppLifecycleState.RESUME.name and self.is_locked:
            self.page.window.full_screen = True
            if self.wakelock:
                try:
                    self.page.run_task(self.wakelock.enable)
                except Exception:
                    pass
            try:
                self.page.window.prevent_display_sleep = True
            except Exception:
                pass
            self.page.update()
