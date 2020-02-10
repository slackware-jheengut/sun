#!/usr/bin/python3
# -*- coding: utf-8 -*-

# sun_gtk is a part of sun.

# Copyright 2015-2020 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# sun is a tray notification applet for informing about
# package updates in Slackware.

# https://gitlab.com/dslackw/sun

# sun is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf
import subprocess
from sun.licenses import lic, abt
from sun.__metadata__ import (
    __all__,
    __email__,
    __author__,
    __version__,
    __website__,
    bin_path,
    icon_path
)
from sun.cli.tool import check_updates, daemon_status
from sun.utils import os_info


class GtkStatusIcon(object):

    def __init__(self):
        self.sun_icon = f'{icon_path}{__all__}.png'
        self.status_icon = Gtk.StatusIcon()
        self.status_icon.set_from_file(self.sun_icon)
        self.status_icon.connect('popup-menu', self.right_click_event)
        self.cmd = "{0}sun_daemon".format(bin_path)
        self.init_daemon()

    def init_daemon(self):
        '''Start daemon when gtk loaded'''
        if daemon_status() == 'SUN not running':
            subprocess.call(f'{self.cmd} &', shell=True)
            return 'Daemon Starts'
        else:
            return 'Daemon is already running...'

    def right_click_event(self, icon, button, time):
        self.menu = Gtk.Menu()

        submenu = Gtk.Menu()
        start = Gtk.MenuItem()
        start.set_label('Start')
        start.connect('activate', self.daemon_start,)
        stop = Gtk.MenuItem()
        stop.set_label('Stop')
        stop.connect('activate', self.daemon_stop)
        restart = Gtk.MenuItem()
        restart.set_label('Restart')
        restart.connect('activate', self.daemon_restart)
        status = Gtk.MenuItem()
        status.set_label('Status')
        status.connect('activate', self.show_daemon_status)
        submenu.append(start)
        submenu.append(stop)
        submenu.append(restart)
        submenu.append(status)
        daemon = Gtk.MenuItem()
        daemon.set_label('Daemon')
        daemon.set_submenu(submenu)
        self.menu.append(daemon)

        check = Gtk.MenuItem()
        check.set_label('Check Updates')
        check.connect('activate', self.show_check_updates)
        self.menu.append(check)

        osInfo = Gtk.MenuItem()
        osInfo.set_label('OS Info')
        osInfo.connect('activate', self.show_os_info)
        self.menu.append(osInfo)

        about = Gtk.MenuItem()
        about.set_label('About')
        about.connect('activate', self.show_about_dialog)
        self.menu.append(about)

        sep = Gtk.SeparatorMenuItem()
        self.menu.append(sep)

        quit = Gtk.MenuItem()
        quit.set_label('Quit')
        quit.connect('activate', Gtk.main_quit)
        self.menu.append(quit)

        self.menu.show_all()

        self.menu.popup(None, None, None, self.status_icon, button, time)

    def message(self, data, title):
        '''Method to display messages to the user'''
        msg = Gtk.MessageDialog(type=Gtk.MessageType.INFO,
                                buttons=Gtk.ButtonsType.CLOSE)
        msg.set_resizable(1)
        msg.set_title(title)

        msg.format_secondary_text(data)
        msg.run()
        msg.destroy()

    def show_check_updates(self, widget):
        '''Show message updates'''
        title = 'SUN - Check Updates'
        msg, count, packages = check_updates()
        data = msg
        if count > 0:
            if len(packages) > 10:
                packages = packages[:10] + ['and more...']
            self.message('{0} \n{1}'.format(data, '\n'.join(packages)))
        else:
            self.message(data, title)

    def show_os_info(self, data):
        '''Show message OS info'''
        title = 'SUN - OS Info'
        self.message(os_info(), title)

    def show_about_dialog(self, widget):
        '''Show message About info'''
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name('SUN - About')
        about_dialog.set_program_name('SUN - Slackware Update Notifier')
        about_dialog.set_version(__version__)
        about_dialog.set_authors([f'{__author__} <{__email__}>'])
        about_dialog.set_license('\n'.join(lic))
        about_dialog.set_website(__website__)
        about_dialog.set_logo(Pixbuf.new_from_file(self.sun_icon))
        about_dialog.set_comments(abt)
        about_dialog.run()
        about_dialog.destroy()

    def daemon_start(self, data):
        '''Show message and start the daemon'''
        title = 'Daemon'
        data = self.init_daemon()
        self.message(data, title)

    def daemon_stop(self, data):
        '''Show message and stop the daemon'''
        title = 'Daemon'
        subprocess.call('killall sun_daemon', shell=True)
        data = 'Daemon stops'
        self.message(data, title)

    def daemon_restart(self, data):
        '''Show message and restart the daemon'''
        title = 'Daemon'
        subprocess.call('killall sun_daemon', shell=True)
        subprocess.call(f'{self.cmd} &', shell=True)
        data = 'Daemon restarts'
        self.message(data, title)

    def show_daemon_status(self, data):
        '''Show message status about the daemon'''
        title = 'Daemon'
        data = daemon_status()
        self.message(data, title)


GtkStatusIcon()
Gtk.main()