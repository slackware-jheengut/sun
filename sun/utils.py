#!/usr/bin/python3
# -*- coding: utf-8 -*-

# utils.py is a part of sun.

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

import os
import re
import getpass
import urllib3
from sun.__metadata__ import (
    pkg_path,
    conf_path,
    etc_slackpkg,
    changelog_txt,
    var_lib_slackpkg
)


def url_open(link):
    '''Return urllib urlopen'''
    try:
        http = urllib3.PoolManager()
        con = http.request('GET', link)
    except urllib3.exceptions.NewConnectionError as e:
        print(e)
    except ValueError:
        return ''
    except KeyboardInterrupt:
        print('')
        raise SystemExit()
    return con


def read_file(registry):
    '''Return reading file'''
    with open(registry, 'r', encoding='utf-8') as file_txt:
        read_file = file_txt.read()
        return read_file


def slack_ver():
    '''Open a file and read the Slackware version'''
    dist = read_file('/etc/slackware-version')
    sv = re.findall(r'\d+', dist)
    if len(sv) > 2:
        version = ('.'.join(sv[:2]))
    else:
        version = ('.'.join(sv))
    return dist.split()[0], version


def ins_packages():
    '''Count installed Slackware packages'''
    count = 0
    for pkg in os.listdir(pkg_path):
        if not pkg.startswith('.'):
            count += 1
    return count


def read_config(config):
    '''Read the config file and return an uncomment line'''
    for line in config.splitlines():
        line = line.lstrip()
        if line and not line.startswith('#'):
            return line
    return ''


def mirror():
    '''Get mirror from slackpkg mirrors file'''
    slack_mirror = read_config(read_file(f'{etc_slackpkg}mirrors'))
    if slack_mirror:
        return f'{slack_mirror}{changelog_txt}'
    else:
        print('\nYou do not have any mirror selected in /etc/slackpkg/mirrors'
              '\nPlease edit that file and uncomment ONE mirror.\n')
        return ''


def fetch():
    '''Get the ChangeLog.txt file size and counts the upgraded packages'''
    mir, r, slackpkg_last_date = mirror(), '', ''
    count, upgraded = 0, []
    if mir:
        try:
            r = url_open(mir).data
        except AttributeError:
            print("sun: error: can't read mirror")
    if os.path.isfile(var_lib_slackpkg + changelog_txt):
        slackpkg_last_date = read_file('{0}{1}'.format(
            var_lib_slackpkg, changelog_txt)).split('\n', 1)[0].strip()
    else:
        return [count, upgraded]
    for line in r.splitlines():
        line = line.decode('utf-8')
        if slackpkg_last_date == line.strip():
            break
        if (line.endswith('z:  Upgraded.') or line.endswith('z:  Rebuilt.') or
                line.endswith('z:  Added.') or line.endswith('z:  Removed.')):
            upgraded.append(line.split('/')[-1])
            count += 1
        if (line.endswith('*:  Upgraded.') or line.endswith('*:  Rebuilt.') or
                line.endswith('*:  Added.') or line.endswith('*:  Removed.')):
            upgraded.append(line)
            count += 1
    return [count, upgraded]


def config():
    '''Return sun configuration values'''
    conf_args = {
        'INTERVAL': 60,
        'STANDBY': 3
    }
    config_file = read_file(f'{conf_path}sun.conf')
    for line in config_file.splitlines():
        line = line.lstrip()
        if line and not line.startswith('#'):
            conf_args[line.split('=')[0]] = line.split('=')[1]
    return conf_args


def os_info():
    '''Get the OS info'''
    stype = ''
    slack, ver = slack_ver()
    mir = mirror()
    if mir:
        if 'current' in mir:
            stype = 'Current'
        else:
            stype = 'Stable'
    info = (
        f'User: {getpass.getuser()}\n'
        f'OS: {slack}\n'
        f'Version: {ver}\n'
        f'Type: {stype}\n'
        f'Arch: {os.uname()[4]}\n'
        f'Kernel: {os.uname()[2]}\n'
        f'Packages: {ins_packages()}'
        )
    return info
