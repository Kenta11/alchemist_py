#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jinja2
import numpy
import os
import shutil
import sys
import toml

from logzero import logger
from pathlib import Path

from alchemist.yacc import parser

def createProject(broker_name:str):
    logger.info("Generating broker: {}".format(broker_name))

    path_to_project = Path("brokers") / ("broker"+broker_name)
    config = toml.load(open(path_to_project / ".Alchemist.toml"))

    # generate directories
    for d in ["include", "src", "script"]:
        os.makedirs(path_to_project / d)

    # generate source codes
    os.chdir(path_to_project)

    generateMakefile(broker_name, config["device"]["board"])
    generateTcl(config["device"]["fpga"], config["device"]["clock"])
    generateDirectives()
    generateGitignore(broker_name)
    message = parser.parse(config["topic"]["message"])
    count = 0
    for m in message:
        if m["attribute"] == "unit":
            count += 1
        elif m["attribute"] == "array":
            data_size = numpy.prod(m["size"])
            if   m["type"] in ["uint8_t",  "int8_t"]:
                count += int(data_size / 8)
            elif m["type"] in ["uint16_t", "int16_t"]:
                count += int(data_size / 4)
            elif m["type"] in ["uint32_t", "int32_t"]:
                count += int(data_size / 2)
            elif m["type"] in ["uint64_t", "int64_t"]:
                count += int(data_size / 1)
            else:
                print("Uknown type:", m["type"], file=sys.stderr)
        else:
            print("Unknwon message type", file=sys.stderr)
            exit(1)
    generateSourceCode(
        broker_name, config["topic"]["pub"], config["topic"]["sub"],
        config["topic"]["width"], count
    )

    os.chdir("../../")

def generateMakefile(project:str, solution:str):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(
         str(Path(os.path.dirname(__file__)) / "template/broker")
    ))
    template = env.get_template("Makefile")
    data = {
        "TARGET": project,
        "SOLUTION": solution
    }
    rendered = template.render(data)
    with open("Makefile", "w") as f:
        f.write(str(rendered))

def generateTcl(device:str, clock:str):
    ##### init.tcl, export.tcl #####
    for name in ["init.tcl", "export.tcl"]:
        shutil.copy(
            str(Path(os.path.dirname(__file__))
            / "template/broker/tcl/{}".format(name)),
            "script/{}".format(name)
        )

    ##### csynth.tcl #####
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(
         str(Path(os.path.dirname(__file__)) / "template/broker/tcl")
    ))

    template = env.get_template("csynth.tcl")
    data = {
        "PART": "{" + device + "}",
        "CLOCK": clock
    }
    rendered = template.render(data)
    with open("script/csynth.tcl", "w") as f:
        f.write(str(rendered))

def generateDirectives():
    Path("directives.tcl").touch()

def generateGitignore(project:str):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(
        str(Path(os.path.dirname(__file__)) / "template/broker")
    ))
    template = env.get_template("gitignore")
    data = {
        "TARGET": project
    }
    rendered = template.render(data)
    with open(".gitignore", "w") as f:
        f.write(str(rendered))

def generateSourceCode(name:str, pub:int, sub:int, width:int, count:int):
    writeHeader(name, pub, sub, width)
    writeSourceCode(name, pub, sub, width, count)

def writeHeader(name:str, pub:int, sub:int, width:int):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(
        str(Path(os.path.dirname(__file__)) / "template/broker/cc")
    ))
    template = env.get_template("header.h")
    data = {
        "message_name": name,
        "pub":   pub,
        "sub":   sub,
        "width": width
    }
    rendered = template.render(data)
    with open("include/broker"+name+".h", "w") as f:
        f.write(str(rendered))

def writeSourceCode(name:str, pub:int, sub:int, width:int, data_count:int):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(
        str(Path(os.path.dirname(__file__)) / "template/broker/cc")
    ))
    template = env.get_template("code.cc")
    data = {
        "message_name": name,
        "pub":   pub,
        "sub":   sub,
        "width": width,
        "data_count": data_count
    }
    rendered = template.render(data)
    with open("src/broker"+name+".cc", "w") as f:
        f.write(str(rendered))
