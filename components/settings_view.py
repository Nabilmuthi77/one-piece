from typing import Callable, Optional
import flet as ft
from utils.theme import ThemeColors
from constants import DARK_BG, LIGHT_BG, STATUS_BAR_SPACER_HEIGHT


class SettingsView(ft.Container):
    """Settings page for One Piece Archive application, matching modern neumorphic aesthetics."""

    def __init__(
        self,
        page: ft.Page,
        current_pref: str,
        on_theme_changed: Callable[[str], None],
        on_back: Callable[[], None],
    ):
        self.app_page = page
        self.current_pref = current_pref
        self.on_theme_changed = on_theme_changed
        self.on_back = on_back

        is_dark = page.theme_mode == ft.ThemeMode.DARK
        self.colors = ThemeColors(is_dark=is_dark)

        super().__init__(
            content=self._build_content(),
            padding=0,
            bgcolor=self.colors.bg_main,
            expand=True,
        )

    def _build_content(self) -> ft.Control:
        # 1. Header Card: Pengaturan
        back_btn = ft.Container(
            content=ft.Icon(
                ft.Icons.ARROW_BACK_ROUNDED,
                size=18,
                color=self.colors.accent_primary,
            ),
            width=34,
            height=34,
            border_radius=10,
            bgcolor="#FFFFFF" if not self.colors.is_dark else self.colors.card_elevated,
            shadow=self.colors.subtle_shadow(depth=1, blur=2),
            alignment=ft.Alignment(0, 0),
            on_click=lambda e: self.on_back(),
            tooltip="Kembali",
        )

        header_icon = ft.Container(
            content=ft.Icon(
                ft.Icons.SETTINGS_ROUNDED,
                size=18,
                color=self.colors.accent_primary,
            ),
            width=34,
            height=34,
            border_radius=10,
            bgcolor="#FFFFFF" if not self.colors.is_dark else self.colors.card_elevated,
            shadow=self.colors.subtle_shadow(depth=1, blur=2),
            alignment=ft.Alignment(0, 0),
        )

        system_badge = ft.Container(
            content=ft.Text(
                "Sistem",
                size=9.5,
                weight=ft.FontWeight.BOLD,
                color=self.colors.accent_primary,
            ),
            padding=ft.Padding(8, 3, 8, 3),
            border_radius=8,
            bgcolor=self.colors.pressed_surface,
            shadow=self.colors.pressed_shadow(depth=1, blur=2),
        )

        header_card = ft.Container(
            content=ft.Row(
                controls=[
                    back_btn,
                    header_icon,
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Pengaturan",
                                size=16,
                                weight=ft.FontWeight.W_800,
                                color=self.colors.text_primary if self.colors.is_dark else self.colors.accent_primary,
                            ),
                            ft.Text(
                                "Preferensi & informasi aplikasi",
                                size=11,
                                weight=ft.FontWeight.W_500,
                                color=self.colors.text_secondary,
                            ),
                        ],
                        spacing=1,
                        expand=True,
                    ),
                    system_badge,
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=self.colors.card_surface,
            shadow=self.colors.raised_shadow(),
            padding=ft.Padding(12, 8, 12, 8),
            border_radius=16,
            margin=ft.Margin(left=16, right=16, top=STATUS_BAR_SPACER_HEIGHT, bottom=8),
        )

        # 2. Unified Section Card: Tema Tampilan
        def make_theme_option(label: str, value: str):
            is_active = self.current_pref == value
            radio_icon = ft.Icons.RADIO_BUTTON_CHECKED_ROUNDED if is_active else ft.Icons.RADIO_BUTTON_OFF_ROUNDED
            radio_color = self.colors.accent_primary if is_active else self.colors.text_secondary

            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(radio_icon, size=18, color=radio_color),
                        ft.Text(
                            label,
                            size=13.5,
                            weight=ft.FontWeight.W_700 if is_active else ft.FontWeight.W_500,
                            color=self.colors.text_primary,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(14, 11, 14, 11),
                border_radius=14,
                bgcolor=(
                    ("#FFFFFF" if not self.colors.is_dark else self.colors.card_elevated)
                    if is_active
                    else ft.Colors.TRANSPARENT
                ),
                shadow=self.colors.subtle_shadow(depth=1, blur=3) if is_active else None,
                on_click=lambda e, v=value: self._handle_theme_change(v),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
            )

        self.theme_options_col = ft.Column(
            controls=[
                make_theme_option("Putih (Light Mode)", "light"),
                make_theme_option("Gelap (Dark Mode)", "dark"),
                make_theme_option("Sesuai Sistem (Auto)", "auto"),
            ],
            spacing=4,
        )

        theme_section_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.PALETTE_ROUNDED,
                                    size=18,
                                    color=self.colors.accent_primary,
                                ),
                                width=36,
                                height=36,
                                border_radius=18,
                                bgcolor="#FFFFFF" if not self.colors.is_dark else self.colors.card_elevated,
                                shadow=self.colors.subtle_shadow(depth=1, blur=2),
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Tema Tampilan",
                                        size=14,
                                        weight=ft.FontWeight.W_700,
                                        color=self.colors.text_primary if self.colors.is_dark else self.colors.accent_primary,
                                    ),
                                    ft.Text(
                                        "Pilih tampilan aplikasi sesuai preferensimu.",
                                        size=11,
                                        color=self.colors.text_secondary,
                                    ),
                                ],
                                spacing=1,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(height=4),
                    self.theme_options_col,
                ],
                spacing=4,
            ),
            bgcolor=self.colors.card_surface,
            shadow=self.colors.raised_shadow(),
            padding=ft.Padding(14, 12, 14, 12),
            border_radius=18,
            margin=ft.Margin(left=16, right=16, top=0, bottom=8),
        )

        # 3. Action Cards (Tentang Aplikasi, Sumber Data, Game Mode)
        def make_action_card(icon_name: str, title: str, subtitle: str, on_click: Callable):
            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(
                                getattr(ft.Icons, icon_name),
                                size=18,
                                color=self.colors.accent_primary,
                            ),
                            width=34,
                            height=34,
                            border_radius=10,
                            bgcolor="#FFFFFF" if not self.colors.is_dark else self.colors.card_elevated,
                            shadow=self.colors.subtle_shadow(depth=1, blur=2),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    title,
                                    size=13.5,
                                    weight=ft.FontWeight.W_700,
                                    color=self.colors.text_primary if self.colors.is_dark else self.colors.accent_primary,
                                ),
                                ft.Text(
                                    subtitle,
                                    size=11,
                                    color=self.colors.text_secondary,
                                ),
                            ],
                            spacing=1,
                            expand=True,
                        ),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, size=20, color=self.colors.text_secondary),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=self.colors.card_surface,
                shadow=self.colors.raised_shadow(),
                padding=ft.Padding(12, 10, 12, 10),
                border_radius=16,
                margin=ft.Margin(left=16, right=16, top=0, bottom=8),
                on_click=on_click,
            )

        # 4. Footer Brand Card
        footer_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.SAILING_ROUNDED,
                        size=28,
                        color=self.colors.accent_primary,
                    ),
                    ft.Text(
                        "One Piece Archive",
                        size=14.5,
                        weight=ft.FontWeight.W_800,
                        color=self.colors.text_primary if self.colors.is_dark else self.colors.accent_primary,
                    ),
                    ft.Text(
                        "Versi 1.0.0",
                        size=10.5,
                        weight=ft.FontWeight.W_600,
                        color=self.colors.text_secondary if self.colors.is_dark else self.colors.accent_primary,
                    ),
                    ft.Text(
                        "Inherited Will, the Destiny of the Age, and the Dreams of the People.",
                        size=9.5,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                        color=self.colors.text_secondary if self.colors.is_dark else self.colors.accent_primary,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=3,
            ),
            bgcolor=self.colors.card_surface,
            shadow=self.colors.raised_shadow(),
            padding=ft.Padding(16, 16, 16, 16),
            border_radius=20,
            margin=ft.Margin(left=16, right=16, top=4, bottom=20),
            alignment=ft.Alignment(0, 0),
        )

        controls_list = [
            header_card,
            theme_section_card,
            make_action_card(
                "INFO_OUTLINE_ROUNDED",
                "Tentang Aplikasi",
                "Informasi ensiklopedia karakter & fitur One Piece",
                self._show_about_modal,
            ),
            make_action_card(
                "STORAGE_ROUNDED",
                "Sumber Data & Cache Offline",
                "Koneksi API oparchive.com dan penyimpanan lokal",
                self._show_data_source_modal,
            ),
            make_action_card(
                "SPEED_ROUNDED",
                "Kurasi Game Mode",
                "Klasifikasi tingkat kesulitan Easy, Medium, dan Hard",
                self._show_gamemode_modal,
            ),
            footer_card,
            ft.Container(height=40),
        ]

        is_desktop = bool(self.app_page.width and self.app_page.width > 600)

        self.centered_wrap = ft.Container(
            content=ft.Column(
                controls=controls_list,
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            width=500 if is_desktop else None,
            expand=not is_desktop,
            alignment=ft.Alignment.TOP_CENTER,
        )

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[self.centered_wrap],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            spacing=0,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
        )

    def _handle_theme_change(self, val: str):
        self.current_pref = val
        self.on_theme_changed(val)
        self.update_theme(val)

    def update_theme(self, pref: str):
        self.current_pref = pref
        is_dark = self.app_page.theme_mode == ft.ThemeMode.DARK
        self.colors = ThemeColors(is_dark=is_dark)
        self.bgcolor = self.colors.bg_main
        self.content = self._build_content()
        try:
            self.update()
        except RuntimeError:
            pass

    def update_layout(self):
        is_desktop = bool(self.app_page.width and self.app_page.width > 600)
        if hasattr(self, 'centered_wrap') and self.centered_wrap:
            self.centered_wrap.width = 500 if is_desktop else None
            self.centered_wrap.expand = not is_desktop
            try:
                self.update()
            except RuntimeError:
                pass

    def _show_about_modal(self, e):
        dialog = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SAILING_ROUNDED, size=24, color=self.colors.accent_primary),
                                ft.Text("Tentang One Piece Archive", size=16, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                            ],
                            spacing=8,
                        ),
                        ft.Container(height=1, bgcolor=self.colors.border_subtle),
                        ft.Text(
                            "One Piece Archive adalah ensiklopedia visual dan katalog karakter dunia One Piece berbasis Python & Flet dengan filosofi Modern Neumorphism.\n\n"
                            "Fitur Utama:\n"
                            "• Ensiklopedia karakter lengkap: Bounty, Haki, Devil Fruit, Ras, dan First Appearance.\n"
                            "• Filter multi-kategori: Story Arcs, Tipe Devil Fruit (Zoan, Paramecia, Logia), Ras, dan Game Mode.\n"
                            "• Pencarian instan dinamis dengan respon real-time.\n"
                            "• Mode Fullscreen HD Locked Viewer untuk inspeksi artwork karakter tanpa gangguan layar mati (Wakelock).\n"
                            "• Offline First Cache: Data karakter otomatis tersimpan lokal sehingga tetap dapat diakses tanpa koneksi internet.\n"
                            "• Dukungan tema lengkap: Terang (Light Neumorphism), Gelap (Dark Velvet), dan Otomatis.",
                            size=12,
                            color=self.colors.text_secondary,
                        ),
                    ],
                    spacing=10,
                    tight=True,
                ),
                width=360,
                padding=12,
            ),
            bgcolor=self.colors.card_surface,
            shape=ft.RoundedRectangleBorder(radius=20),
        )
        self.app_page.show_dialog(dialog)

    def _show_data_source_modal(self, e):
        dialog = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CLOUD_DONE_ROUNDED, size=24, color=self.colors.accent_primary),
                                ft.Text("Sumber Data & Cache", size=16, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                            ],
                            spacing=8,
                        ),
                        ft.Container(height=1, bgcolor=self.colors.border_subtle),
                        ft.Text(
                            "Aplikasi ini mengonsumsi data resmi open-source dari:\n"
                            "• API: https://oparchive.com\n\n"
                            "Mekanisme Cache Lokal:\n"
                            "• Saat pertama kali terhubung internet, file data karakter dan devil fruit disimpan di folder local data/characters.json.\n"
                            "• Jika jaringan terputus atau offline, aplikasi secara instan beralih ke cache lokal tanpa loading lambat.",
                            size=12,
                            color=self.colors.text_secondary,
                        ),
                    ],
                    spacing=10,
                    tight=True,
                ),
                width=360,
                padding=12,
            ),
            bgcolor=self.colors.card_surface,
            shape=ft.RoundedRectangleBorder(radius=20),
        )
        self.app_page.show_dialog(dialog)

    def _show_gamemode_modal(self, e):
        dialog = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SPEED_ROUNDED, size=24, color=self.colors.accent_primary),
                                ft.Text("Klasifikasi Game Mode", size=16, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                            ],
                            spacing=8,
                        ),
                        ft.Container(height=1, bgcolor=self.colors.border_subtle),
                        ft.Text(
                            "Kurasi tingkat kesulitan karakter untuk tebak karakter atau eksplorasi:\n\n"
                            "• Easy: 100 karakter paling populer dan berpengaruh di cerita (Kru Topi Jerami, Yonko, Admiral, Shichibukai, dll).\n\n"
                            "• Medium: Komandan Yonko, CP9/CP0, Akazaya Nine, Marinir berpangkat tinggi, dan sekutu arc utama.\n\n"
                            "• Hard: Karakter langka, kameo SBS, bajak laut minor, dan karakter trivia unik di semesta One Piece.",
                            size=12,
                            color=self.colors.text_secondary,
                        ),
                    ],
                    spacing=10,
                    tight=True,
                ),
                width=360,
                padding=12,
            ),
            bgcolor=self.colors.card_surface,
            shape=ft.RoundedRectangleBorder(radius=20),
        )
        self.app_page.show_dialog(dialog)
