#!/usr/bin/python3
# -*- coding: utf-8 -*-

# sun_gtk is a part of sun.

# Copyright 2015-2018 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
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
        self.sun_icon = "{0}{1}.png".format(icon_path, __all__)
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file(self.sun_icon)
        self.statusicon.connect("popup-menu", self.right_click_event)

    def right_click_event(self, icon, button, time):
        self.menu = Gtk.Menu()

        check = Gtk.MenuItem()
        check.set_label("Check Updates")
        check.connect("activate", self.show_check_updates)
        self.menu.append(check)

        osInfo = Gtk.MenuItem()
        osInfo.set_label("OS Info")
        osInfo.connect("activate", self.show_os_info)
        self.menu.append(osInfo)

        about = Gtk.MenuItem()
        about.set_label("About")
        about.connect("activate", self.show_about_dialog)
        self.menu.append(about)

        quit = Gtk.MenuItem()
        quit.set_label("Quit")
        quit.connect("activate", Gtk.main_quit)
        self.menu.append(quit)

        self.menu.show_all()

        self.menu.popup(None, None, None, self.statusicon, button, time)

    def message(self, data, title):
        """Method to display messages to the user"""
        msg = Gtk.MessageDialog()
        msg.set_resizable(1)
        msg.set_title(title)
        msg.format_secondary_text(data)
        msg.run()
        msg.destroy()

    def show_check_updates(self, widget):
        """Show message updates"""
        title = "SUN - Check updates"
        msg, count, packages = check_updates()
        data = msg
        if count > 0:
            if len(packages) > 10:
                packages = packages[:10] + ["and more..."]
            self.message("{0} \n{1}".format(data, "\n".join(packages)))
        else:
            self.message(data, title)

    def show_os_info(self, data):
        """Show message OS info"""
        title = "SUN - OS Info"
        self.message(os_info(), title)

    def show_about_dialog(self, widget):
        """Show message About info"""
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name("SUN - About")
        about_dialog.set_program_name("SUN")
        about_dialog.set_version(__version__)
        about_dialog.set_authors([f"{__author__} <{__email__}>"])
        about_dialog.set_license("\n".join(lic))
        about_dialog.set_website(__website__)
        about_dialog.set_logo(Pixbuf.new_from_file(self.sun_icon))
        about_dialog.set_comments(abt)
        about_dialog.run()
        about_dialog.destroy()


GtkStatusIcon()
Gtk.main()