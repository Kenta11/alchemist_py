#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import git
import os
import re
import sys
import toml

from pathlib import Path

from alchemist_py.brokergen import createProject
from alchemist_py.deviceinfo import searchDevice
from alchemist_py.plugin_manager import PluginManager

class Manager(object):
    def __init__(self):
        config = toml.load(open("Alchemist.toml"))
        self.board  = config["board"]
        self.nodes  = config["nodes"]
        self.topics = config["topics"]

        self.fpga, self.clock = searchDevice(self.board)

        self.topic_table = {}
        for topic in self.topics:
            self.topic_table[topic["name"]] =\
                "struct {name} {{\n    {message}}};".format(
                    name=topic["name"], message=topic["message"]
                )
        self.p_manager = PluginManager()

        self.ports = []
        for ps in list(map(lambda x:x["ports"], self.nodes)):
            self.ports.extend(ps)

    def updateNode(self, node):
        path_to_project = Path("nodes")/node["name"]

        # make mini alchemist data for the node
        mini_alchemist = {
            "device": {
                "board": self.board,
                "fpga":  self.fpga,
                "clock": self.clock
            },
            "node": node,
            "topics": []
        }

        for port in node["ports"]:
            for topic in self.topics:
                if port["attribute"] in ["wire"]:
                    break
                elif port["attribute"] in ["publisher", "subscriber"] and port["topic"] == topic["name"]:
                    mini_alchemist["topics"].append(topic)
                    break
            else:
                print("Unknown topic:", port["topic"], file=sys.stderr)
                print("node:", node["name"])
                exit(1)

        # write mini alchemist to TOML
        os.makedirs(path_to_project)
        toml.dump(mini_alchemist, open(path_to_project/".Alchemist.toml", "w"))

        # update project
        plugin = self.p_manager.loadPlugin(node["plugin"])
        plugin.createProject(node["name"])

    def updateNodes(self):
        # update projects for nodes
        for node in self.nodes:
            path_to_project = Path("nodes")/node["name"]
            # if no project for a node, make a directory and Alchemist.toml
            if not os.path.exists(path_to_project):
                if "repo" in node.keys():
                    git.Repo.clone_from(node["repo"], "nodes")
                else:
                    self.updateNode(node)

            # if Alchemist.toml was updated, update mini Alchemist.toml
            t_alchemist = os.path.getatime("Alchemist.toml")
            t_mini_alchemist = os.path.getatime(path_to_project/".Alchemist.toml")
            if t_alchemist > t_mini_alchemist:
                if "repo" in node.keys():
                    git.Repo.clone_from(node["repo"], "nodes")
                else:
                    self.updateNode(node)

    def updateTopic(self, topic:dict):
        path_to_project = Path("brokers") / ("broker"+topic["name"])
        if not os.path.exists(path_to_project):
            byte = 0
            for m in re.finditer(r"(?P<type>((unsigned\s+){0,1}(char|short|int|long)|(float|double)|(ap_(u){0,1}int\s*\<\s*[1-9]{1,4}\s*>)))\s+(?P<var>([a-zA-Z_][a-zA-Z0-9_]*(\s*\[\s*([0-9]|[1-9][0-9]*)\s*\]){0,1}))\s*;", topic["message"]):
                byte += self.getByte(m.group("type"), m.group("var"))

            mini_alchemist = {
                "device": {
                    "board": self.board,
                    "fpga":  self.fpga,
                    "clock": self.clock
                },
                "topic": topic,
            }
            mini_alchemist["topic"]["pub"] = len(list(filter(
                lambda x: x["attribute"] == "publisher" and x["topic"] == topic["name"],
                self.ports
            )))
            mini_alchemist["topic"]["sub"] = len(list(filter(
                lambda x: x["attribute"] == "subscriber" and x["topic"] == topic["name"],
                self.ports
            )))
            mini_alchemist["topic"]["width"] = 64
            mini_alchemist["topic"]["count"] = int(byte / 8)

            os.makedirs(path_to_project)
            toml.dump(mini_alchemist, open(path_to_project / ".Alchemist.toml", "w"))

            createProject(topic["name"])

    def updateTopics(self):
        for topic in self.topics:
            self.updateTopic(topic)

    def getByte(self, vType:str, var:str):
        width_of_type = 0
        if vType == "char":
            width_of_type = 1
        elif vType == "short":
            width_of_type = 2
        elif vType == "int":
            width_of_type = 4
        elif vType == "long":
            width_of_type = 8
        elif vType.split()[0] == "unsigned":
            if vType.split()[1] == "char":
                width_of_type = 1
            elif vType.split()[1] == "short":
                width_of_type = 2
            elif vType.split()[1] == "int":
                width_of_type = 4
            elif vType.split()[1] == "long":
                width_of_type = 8
            else:
                print("Unknown type!")
                exit(1)
        else:
            print("Unknown type!")
            exit(1)

        length_of_var = 1
        m = re.match(
            r"[a-zA-Z_][a-zA-Z0-9_]*\s*\[\s*(?P<length>[1-9][0-9]*)\s*\]",
            var
        )
        if m:
            length_of_var = int(m.group("length"))

        return width_of_type * length_of_var
