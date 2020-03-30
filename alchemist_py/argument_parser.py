#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class ArgumentParser(object):
    def __init__(self, argv):
        self.argv = argv
        self.argc = len(self.argv)

    def parse(self):
        ret = {}
        commands = ["new", "update", "build", "test", "list", "clean", "plugin"]

        # get operation
        if len(self.argv) == 0:
            ret["operation"] = None
        elif self.argv[0] in commands:
            ret["operation"] = self.argv[0]
        else:
            ret["operation"] = None

        # get options
        if   ret["operation"] == "new":
            ret["project_name"] = self.argv[1]
        elif ret["operation"] == "plugin":
            ret["options"] = self.argv[1:]
        elif ret["operation"] == "test":
            if self.argv[1] == "--unit":
                ret["kind"]   = "unit"
                ret["node"] = self.argv[2]
                if len(self.argv) > 3:
                    ret["args"] = " "+self.argv[3:]
                else:
                    ret["args"] = ""
            elif self.argv[1] == "--integration":
                ret["kind"] =  "integration"
                if len(self.argv) > 2:
                    ret["args"] = " "+self.argv[2:]
                else:
                    ret["args"] = ""
            else:
                ret["kind"] = ""

        # help
        if "--help" in self.argv or "-h" in self.argv:
            ret["help"] = True
        else:
            ret["help"] = False

        return ret
