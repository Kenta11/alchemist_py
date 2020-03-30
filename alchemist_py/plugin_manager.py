#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import toml

from importlib import import_module
from pathlib import Path

plugin_dir = os.path.expanduser("~/.alchemist/plugins/")
sys.path.append(str(Path(plugin_dir)))

class PluginManager(object):
    def __init__(self):
        self.plugin_table = {}

        for plugin_name in os.listdir(plugin_dir):
            if not os.path.isdir(Path(plugin_dir)/plugin_name):
                continue

            with open(Path(plugin_dir)/plugin_name/"config.toml") as f:
                self.plugin_table[plugin_name] = toml.load(f)

    def getCommands(self):
        commands = {}
        for plugin_name in self.plugin_table.keys():
            commands[plugin_name] = self.plugin_table[plugin_name]["commands"]

        return commands

    def listPlugins(self):
        print("{:^16}|{:^16}|{:^10}|{:^10}".format("NAME", "HLS", "LANG", "VERSION"))
        print("{}|{}|{}|{}".format("-"*16, "-"*16, "-"*10, "-"*10))
        for name in sorted(self.plugin_table.keys()):
            HLS     = self.plugin_table[name]["description"]["HLS"]
            LANG    = self.plugin_table[name]["description"]["LANG"]
            VERSION = self.plugin_table[name]["description"]["VERSION"]
            print(
                "{name:^16}|{HLS:^16}|{LANG:^10}|{VERSION:^10}".format(
                    name=name,
                    HLS=HLS,
                    LANG=LANG,
                    VERSION=VERSION,
                )
            )

    def loadPlugin(self, name:str):
        if name in self.plugin_table.keys():
            return import_module(".".join([name, name, "plugin"]))
        else:
            return None
