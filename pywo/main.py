#!/usr/bin/env python
#
# PyWO - Python Window Organizer
# Copyright 2010, Wojciech 'KosciaK' Pietrzok
#
# This file is part of PyWO.
#
# PyWO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyWO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyWO.  If not, see <http://www.gnu.org/licenses/>.
#

"""main.py - main module for PyWO."""

import logging
from logging.handlers import RotatingFileHandler

from pywo import actions, commandline, filters
from pywo.config import Config
from pywo.core import Window, WindowManager, State
from pywo.services import daemon


__author__ = "Wojciech 'KosciaK' Pietrzok <kosciak@kosciak.net>"
__version__ = "0.3"


log = logging.getLogger('pywo')


def setup_loggers(debug=False):
    """Setup file, and console loggers."""
    log.setLevel(logging.DEBUG)
    format = '%(levelname)s: %(name)s.%(funcName)s(%(lineno)d): %(message)s'
    rotating = RotatingFileHandler('/tmp/PyWO.log', 'a', 1024*50, 2)
    rotating.setFormatter(logging.Formatter(format))
    rotating.setLevel(logging.DEBUG)
    log.addHandler(rotating)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(message)s'))
    if debug:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)
    log.addHandler(console)


def main():
    # parse commandline
    try:
        (options, args) = commandline.parse_args()
    except commandline.ParserException, e:
        commandline.print_error(str(e))
    # setup loggers
    setup_loggers(options.debug)

    config = Config(options.config)

    if options.start_daemon:
        log.info('Starting PyWO...')
        daemon.setup(config)
        daemon.start(loop=True)
    elif options.list_windows:
        WM = WindowManager()
        windows = WM.windows(filters.NORMAL_TYPE)
        for window in windows:
            geometry = window.geometry
            state = window.state
            win_desktop = window.desktop
            desktop = [win_desktop, -1][State.STICKY in state or \
                                        win_desktop == Window.ALL_DESKTOPS]
            if State.HIDDEN in state and \
               not State.SHADED in state:
                state_flags = 'i'
            elif State.FULLSCREEN in state:
                state_flags = 'F'
            elif State.MAXIMIZED_HORZ in state and \
                 State.MAXIMIZED_VERT in state:
                state_flags = 'M'
            elif State.MAXIMIZED_VERT in state:
                state_flags = 'V'
            elif State.MAXIMIZED_HORZ in state:
                state_flags = 'H'
            else:
                state_flags = ' '
            state_flags += [' ', 's'][State.SHADED in state]# and \
                                      #not State.HIDDEN in state]
            print '%s %s %s %s' % (window.id, desktop, state_flags, window.name)
    elif args or options.action:
        try:
            actions.perform(args, config, options)
        except actions.ActionException, e:
            # TODO: What about other exceptions?
            #       parser exceptions?
            commandline.print_error(e)
    elif options.help_more:
        commandline.print_help_more(config)
    else:
        commandline.print_help()


if __name__ == '__main__':
    main()

