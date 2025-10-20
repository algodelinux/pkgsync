#!/usr/bin/env python3
import gi
import psutil
import signal
from datetime import datetime
from threading import Thread

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, AppIndicator3, GLib, Notify

APP_ID = 'pkgsync_indicator'

ICON_RUNNING = "emblem-synchronizing"
PKGSYNC_PATH = "/usr/local/sbin/pkgsync"


class PkgSyncIndicator:
    def __init__(self):
        Notify.init(APP_ID)
        self.indicator = AppIndicator3.Indicator.new(
            APP_ID, ICON_RUNNING, AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.running = True
        self.pkgsync_start = None
        self.was_running = False
        self.first_run_done = False
        self.label_update_id = None
        self.last_duration = "00:00"
        self.notification_shown = False  # Para mostrar la notificación de inicio solo una vez

        self.menu = self.build_menu()
        self.indicator.set_menu(self.menu)

        Thread(target=self.update_loop, daemon=True).start()

    def build_menu(self):
        menu = Gtk.Menu()

        # Título del menú
        title_item = Gtk.MenuItem(label="PkgSync")
        title_item.set_sensitive(False)
        menu.append(title_item)
        menu.append(Gtk.SeparatorMenuItem())

        # Estado, inicio y duración
        self.item_status = Gtk.MenuItem(label="Estado: comprobando...")
        self.item_status.set_sensitive(False)
        menu.append(self.item_status)

        self.item_start = Gtk.MenuItem(label="Inicio: -")
        self.item_start.set_sensitive(False)
        menu.append(self.item_start)

        self.item_duration = Gtk.MenuItem(label="Duración: -")
        self.item_duration.set_sensitive(False)
        menu.append(self.item_duration)

        menu.append(Gtk.SeparatorMenuItem())
        menu.show_all()
        return menu

    def find_pkgsync_process(self):
        for proc in psutil.process_iter(attrs=['exe', 'cmdline', 'name', 'create_time']):
            try:
                exe = proc.info.get('exe') or ""
                cmdline = " ".join(proc.info.get('cmdline', []))
                name = proc.info.get('name', "")
                if PKGSYNC_PATH in exe or PKGSYNC_PATH in cmdline or name == "pkgsync":
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def update_loop(self):
        while self.running:
            self.update_status()
            GLib.usleep(5000000)  # 5 segundos

    def update_status(self):
        proc = self.find_pkgsync_process()
        running = proc is not None

        if running and not self.was_running:
            self.pkgsync_start = datetime.now()
            self.first_run_done = True
            if not self.notification_shown:
                GLib.idle_add(self.show_running_notification_once)
                self.notification_shown = True
            if not self.label_update_id:
                self.label_update_id = GLib.timeout_add_seconds(1, self.update_label)

        elif not running and self.was_running:
            # Notificación de finalización
            notif = Notify.Notification.new(
                "Actualización completada",
                "Las actualizaciones de paquetes han finalizado correctamente.",
                ICON_RUNNING
            )
            notif.set_urgency(Notify.Urgency.CRITICAL)
            notif.show()
            # Desaparece automáticamente tras 5 segundos
            GLib.timeout_add_seconds(5, lambda: (notif.close(), False))
            self.notification_shown = False  # Reiniciar para la siguiente sincronización

        self.was_running = running
        GLib.idle_add(self.set_status, running, self.pkgsync_start)

    def format_duration_short(self):
        if not self.pkgsync_start:
            return self.last_duration
        elapsed = int((datetime.now() - self.pkgsync_start).total_seconds())
        m, s = divmod(elapsed, 60)
        self.last_duration = f"{m:02d}:{s:02d}"
        return self.last_duration

    def set_status(self, running, start_time):
        if running and start_time:
            label_text = self.format_duration_short()
            tooltip = "Sincronización de pkgsync en curso"
        elif not running and self.first_run_done:
            label_text = "✔"
            tooltip = f"Sincronización completada ({self.last_duration})"
        else:
            label_text = ""
            tooltip = "Inactivo"

        # Icono fijo como reloj
        self.indicator.set_icon_full(ICON_RUNNING, tooltip)
        self.indicator.set_label(label_text, "")
        self.item_status.set_label(f"Estado: {'activo' if running else 'detenido'}")
        self.item_start.set_label(f"Inicio: {start_time.strftime('%H:%M:%S') if start_time else '-'}")
        self.item_duration.set_label(f"Duración: {self.last_duration}")
        self.indicator.set_title(tooltip)
        return False

    def show_running_notification_once(self):
        """Muestra la notificación inicial durante 10 segundos y no se repite"""
        message = (
            "Sincronización de pkgsync en curso.\n"
            "Por favor, no apague el equipo mientras se están realizando actualizaciones."
        )
        notif = Notify.Notification.new(
            "Sincronización de pkgsync en curso",
            message,
            ICON_RUNNING
        )
        notif.set_urgency(Notify.Urgency.CRITICAL)
        notif.show()
        # Cerrar automáticamente tras 10 segundos
        GLib.timeout_add_seconds(10, lambda: (notif.close(), False))
        return False

    def update_label(self):
        proc = self.find_pkgsync_process()
        if proc and self.pkgsync_start:
            GLib.idle_add(self.set_status, True, self.pkgsync_start)
            return True
        else:
            self.label_update_id = None
            return False

    def quit(self, _):
        self.running = False
        if self.label_update_id:
            try:
                GLib.source_remove(self.label_update_id)
            except Exception:
                pass
            self.label_update_id = None
        Notify.uninit()
        Gtk.main_quit()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = PkgSyncIndicator()
    Gtk.main()


if __name__ == "__main__":
    main()
