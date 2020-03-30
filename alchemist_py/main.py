#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import git
import glob
import os
import re
import shutil
import subprocess
import sys
import toml

from logzero import logger
from pathlib import Path

from alchemist.argument_parser import ArgumentParser
from alchemist.deviceinfo import listDevices
from alchemist.plugin_manager import PluginManager
from alchemist.project_manager import Manager
from alchemist.tclgen import tclgen
from alchemist.xdcgen import xdcgen

def usage():
    operations = [
        ("new <project_name>", "generate project"),
        ("update", "fetch component and generate templates of components"),
        ("test (--unit|--integration)", "test components and system"),
        ("build", "generate bitstream"),
        ("clean", "clean project"),
        ("list", "list usable FPGA boards"),
        ("plugin (list|install|update)", "manage plugins")
    ]
    print("Usage: alchemist <operation> [options]")
    print("operation:")
    for op in operations:
        print("    {:<30}: {}".format(op[0], op[1]))

def main():
    parser = ArgumentParser(sys.argv[1:])
    arg = parser.parse()

    if arg["operation"] is None or arg["help"] == True:
        usage()
    elif arg["operation"] == "new":
        project_name = arg["project_name"]
        if os.path.exists(project_name):
            print(
                "Directory {} already exists.".format(project_name),
                file=sys.stderr
            )
        elif not re.match("[a-zA-Z][a-zA-Z0-9_]*$", project_name):
            print(
                "Project name is illegal.".format(project_name),
                file=sys.stderr
            )
        else:
            for d in ["nodes", "brokers", "log"]:
                os.makedirs(Path(project_name)/d)
            for f in [".gitignore", "README.md", "Alchemist.toml"]:
                (Path(project_name)/f).touch()

            with open(Path(project_name)/"README.md", "w") as f:
                f.write("# {}\n\n\n".format(project_name))
    elif arg["operation"] == "list":
        listDevices()
    elif arg["operation"] == "plugin":
        if len(arg["options"]) > 0:
            if arg["options"][0] == "install":
                with open(os.path.expanduser("~/.alchemist/config.toml")) as f:
                    config_plugin = toml.load(f)

                wd = os.getcwd()
                os.chdir(os.path.expanduser("~/.alchemist/plugins"))

                for plugin in config_plugin["plugins"]:
                    plugin_name = plugin["repo"].split("/")[1]
                    if not os.path.exists(plugin_name):
                        logger.info("Clone "+plugin_name)
                        git.Repo.clone_from("https://github.com/"+plugin["repo"], plugin_name)

                os.chdir(wd)
            elif arg["options"][0] == "list":
                plugin_manager = PluginManager()
                plugin_manager.listPlugins()
            elif arg["options"][0] == "update":
                with open(os.path.expanduser("~/.alchemist/config.toml")) as f:
                    config_plugin = toml.load(f)

                wd = os.getcwd()
                os.chdir(os.path.expanduser("~/.alchemist/plugins"))

                for plugin in config_plugin["plugins"]:
                    plugin_name = plugin["repo"].split("/")[1]
                    if os.path.exists(plugin_name):
                        logger.info("Pull "+plugin_name)
                        git.Repo(plugin_name).git.pull()

                os.chdir(wd)
            else:
                usage()
        else:
            usage()
    else:
        try:
            config = toml.load(open("Alchemist.toml"))
        except FileNotFoundError:
            print("This directory is not alchemist project", file=sys.stderr)
            exit(1)
        except toml.TomlDecodeError:
            print("Alchemist.toml is brokern", file=sys.stderr)
            exit(1)

        commands = PluginManager().getCommands()

        if arg["operation"] == "update":
            manager = Manager()
            manager.updateNodes()
            manager.updateTopics()
        elif arg["operation"] == "test":
            if arg["kind"] == "unit":
                os.chdir(Path("nodes")/arg["node"])
                plugin_name = toml.load(open(".Alchemist.toml"))["node"]["plugin"]
                subprocess.run(
                    commands[plugin_name]["unittest"].format(args=arg["args"]),
                    shell=True
                )
                os.chdir("../..")
            elif arg["kind"] == "integration":
                children_pid = []
                for node in config["nodes"]:
                    pid = os.fork()
                    if pid == 0: # child process
                        os.chdir(Path("nodes")/node["name"])
                        plugin_name = toml.load(open(".Alchemist.toml"))["node"]["plugin"]
                        subprocess.run(
                            commands[plugin_name]["integrationtest"].format(args=arg["args"]),
                            shell=True
                        )
                        sys.exit()
                    else: # parent process
                        children_pid.append(pid)
                for pid in children_pid:
                    os.waitpid(pid, 0)
            else:
                usage()
        elif arg["operation"] == "build":
            # building nodes
            children_pid = []
            for node in config["nodes"]:
                pid = os.fork()
                if pid == 0: # child process
                    logger.info("Building the node: "+node["name"])

                    log_file = open(
                        "log/{name}_{date}.log".format(
                            name=node["name"],
                            date=datetime.datetime.now().strftime(
                                "%Y%m%d%H%M%S"
                            )
                        ),
                        "w"
                    )
                    os.chdir(Path("nodes")/node["name"])

                    plugin_name = toml.load(open(".Alchemist.toml"))["node"]["plugin"]
                    return_code = subprocess.run(
                        commands[plugin_name]["build"].format(),
                        shell=True,
                        stdout=log_file,
                        stderr=subprocess.STDOUT
                    ).returncode
                    if return_code == 0:
                        logger.info("Complete the building: "+node["name"])
                    else:
                        logger.error("Building was failed: "+node["name"])

                    sys.exit()
                else: # parent process
                    children_pid.append(pid)
            for pid in children_pid:
                os.waitpid(pid, 0)

            # building brokers
            children_pid = []
            for broker in config["topics"]:
                pid = os.fork()
                if pid == 0: # child process
                    logger.info("Building the broker: "+broker["name"])
                    log_file = open(
                        "log/{name}_{date}.log".format(
                            name=broker["name"],
                            date=datetime.datetime.now().strftime(
                                "%Y%m%d%H%M%S"
                            )
                        ),
                        "w"
                    )
                    os.chdir(Path("brokers")/("broker"+broker["name"]))

                    return_code = subprocess.run(
                        "make",
                        shell=True,
                        stdout=log_file,
                        stderr=subprocess.STDOUT
                    ).returncode
                    if return_code == 0:
                        logger.info("Complete the building: "+broker["name"])
                    else:
                        logger.error("Building was failed: "+broker["name"])

                    sys.exit()
                else: # parent process
                    children_pid.append(pid)
            for pid in children_pid:
                os.waitpid(pid, 0)

            # generating bitstream
            if not os.path.exists("generate_bitstream.tcl"):
                tclgen(config)
            if not os.path.exists("constr.xdc"):
                xdcgen(config)
            subprocess.run(
                getPathOfVivado()+" -mode batch -source generate_bitstream.tcl",
                shell=True
            )
        elif arg["operation"] == "clean":
            # clean nodes
            for node_name in os.listdir("nodes"):
                os.chdir(Path("nodes")/node_name)
                plugin_name = toml.load(open(".Alchemist.toml"))["node"]["plugin"]
                subprocess.run(commands[plugin_name]["clean"], shell=True)
                os.chdir("../..")
            # clean brokers
            for broker_name in os.listdir("brokers"):
                os.chdir(Path("brokers")/broker_name)
                subprocess.run("make clean", shell=True)
                os.chdir("../..")
            # clean bitstream, tcl script, *.jou and *.log
            if os.path.isdir("directory"):
                shutil.rmtree("directory")
            if os.path.isfile("generate_bitstream.tcl"):
                os.remove("generate_bitstream.tcl")
            for q in ["log/*", "*.jou", "*.log"]:
                for p in glob.glob(q):
                    os.remove(p)
        else:
            print("Unknown operation", file=sys.stderr)
            exit(1)

def getPathOfVivado()->str:
    config = toml.load(open(os.path.expanduser("~/.alchemist/config.toml")))
    return str(Path(config["path_to_vivado"])/"bin"/"vivado")
