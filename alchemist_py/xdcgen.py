#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import sys
import toml
from pathlib import Path

filename = "constr.xdc"

def searchBoardFile(board_name: str):
    for f in glob.glob(str(Path(os.path.expanduser("~")) / "board_files" / "**" / "**.toml"), recursive = True):
        if f.split("/")[-1] == (board_name + ".toml"):
            return toml.load(open(f))

    for f in glob.glob(str(Path(os.path.dirname(__file__)) / "board_files" / "**" / "**.toml"), recursive = True):
        if f.split("/")[-1] == (board_name + ".toml"):
            return toml.load(open(f))
    return None

def xdcgen(config: dict):
    if "board" not in config.keys():
        print("Error! board name not found!!", file=sys.stderr)
        exit(1)
    board_file = searchBoardFile(config["board"])
    if board_file is None:
        print("Error! board file '{}' not found!".format(config["board"]), file=sys.stderr)
        exit(1)

    pins = config["pins"]
    ports_name = ["clk", "rst"] 
    ports_name += list(map(lambda x: x["name"], config["ports"]))

    error_flag = False
    for port_name in ports_name:
        keyFound = False
        # search pin alias from Alchemist.toml
        for pin in pins:
            if port_name == pin["name"]:
                vars = { "ret": None }
                vars.update(board_file["pins"])
                exec("ret = " + pin["position"], {}, vars)
                if isinstance(vars["ret"], list):
                    for index, var in enumerate(vars["ret"]):
                        print("set_property -dict {{ PACKAGE_PIN {} IOSTANDARD {} }} [get_ports {}[{}]]".format(var["name"], var["type"], port_name, index), file = open(filename, "a"))
                else:
                    print("set_property -dict {{ PACKAGE_PIN {} IOSTANDARD {} }} [get_ports {}]".format(vars["ret"]["name"], vars["ret"]["type"], port_name), file = open(filename, "a"))
                keyFound = True
                break
        if keyFound:
            continue

        # search pin number(s) from the board file
        for pin in board_file["pins"]:
            if port_name == pin:
                ret = board_file["pins"][port_name]
                if isinstance(ret, list):
                    for index, var in enumerate(ret):
                        print("set_property -dict {{ PACKAGE_PIN {} IOSTANDARD {} }} [get_ports {}[{}]]".format(var["name"], var["type"], port_name, index), file = open(filename, "a"))
                else:
                    print("set_property -dict {{ PACKAGE_PIN {} IOSTANDARD {} }} [get_ports {}]".format(ret["name"], ret["type"], port_name), file = open(filename, "a"))
                keyFound = True
                break

        if keyFound:
            continue

        print("Warning: pin for {} not found".format(port_name), file=sys.stderr)
        error_flag = True

    if error_flag:
        exit(1)
