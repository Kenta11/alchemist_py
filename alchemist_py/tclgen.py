#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import sys
import toml
import jinja2
from pathlib import Path

filename="generate_bitstream.tcl"

def initialProcedure(directory_name:str, project_name:str, board_name:str, path_to_project:str)->None:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(
         str(Path(os.path.dirname(__file__)) / "template")
    ))  
    template = env.get_template("tcl/head.tcl")
    data = { 
        "directory_name": directory_name,
        "project_name": project_name,
	"board_name": board_name,
        "path_to_project": path_to_project
    }   
    rendered = template.render(data)
    with open(filename, "w") as f:
        f.write(str(rendered))

def finalProcedure(directory_name:str, project_name:str, path_to_project:str)->None:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(
         str(Path(os.path.dirname(__file__)) / "template")
    ))  
    template = env.get_template("tcl/tail.tcl")
    data = { 
        "directory_name": directory_name,
        "project_name": project_name,
        "path_to_project": path_to_project
    }   
    rendered = template.render(data)
    with open(filename, "a") as f:
        f.write(str(rendered))

class TopicGenerator(object):
    def __init__(self):
        self.count = 0

    def generate(self, axis_data_fifo:dict, broker_name:str, input_fifo:int, output_fifo:int)->None:
        _broker_name = "broker"+broker_name
        print("## {}".format(_broker_name), file=open(filename, "a"))
        print("""\
for {{set i {}}} {{$i < {}}} {{incr i}} {{
    create_bd_cell -type ip -vlnv xilinx.com:ip:axis_data_fifo:{} axis_data_fifo_$i
    set_property -dict [list CONFIG.FIFO_DEPTH {{1024}}] [get_bd_cells axis_data_fifo_$i]
    # set_property -dict [list CONFIG.TDATA_NUM_BYTES.VALUE_SRC USER] [get_bd_cells axis_data_fifo_$i]
    set_property -dict [list CONFIG.TDATA_NUM_BYTES {{8}}] [get_bd_cells axis_data_fifo_$i]
}}""".format(self.count, self.count+input_fifo+output_fifo, axis_data_fifo["version"]), file=open(filename, "a"))
        print("create_bd_cell -type ip -vlnv xilinx.com:hls:{broker}:1.0 {broker}_0".format(broker=_broker_name), file=open(filename, "a"))

        print("""\
for {{set i {init}}} {{$i < {condition}}} {{incr i}} {{
    connect_bd_intf_net [get_bd_intf_pins axis_data_fifo_$i/M_AXIS] [get_bd_intf_pins {broker}_0/port_pub_[expr ${{i}}-{init}]_V]
}}""".format(init=self.count, condition=self.count+input_fifo, broker=_broker_name), file=open(filename, "a"))
        print("""\
for {{set i {init}}} {{$i < {condition}}} {{incr i}} {{
    connect_bd_intf_net [get_bd_intf_pins axis_data_fifo_$i/S_AXIS] [get_bd_intf_pins {broker}_0/port_sub_[expr ${{i}}-{init}]_V]
}}""".format(init=self.count+input_fifo, condition=self.count+input_fifo+output_fifo, broker=_broker_name), file=open(filename, "a"))
        print("group_bd_cells topic_{} \"".format(broker_name), file=open(filename, "a"))
        for x in range(self.count, self.count+input_fifo+output_fifo):
            print("    [get_bd_cells axis_data_fifo_{}]".format(x), file=open(filename, "a"))
        print("    [get_bd_cells {}_0]".format(_broker_name), file=open(filename, "a"))
        print("\"", file=open(filename, "a"))

        self.count += input_fifo + output_fifo

class NodeGenerator(object):
    def __init__(self):
        pass

    def generate(self, name:str)->None:
        print("create_bd_cell -type ip -vlnv xilinx.com:hls:{}:1.0 {}_0".format(
            name, name),
            file=open(filename, "a")
        )

def connectPublisher(node_name:str, port_name:str, topic_name:str, fifo_num:int):
    print("connect_bd_intf_net [get_bd_intf_pins {}_0/{}_V] [get_bd_intf_pins {}/axis_data_fifo_{}/S_AXIS]".format(
        node_name, port_name, topic_name, fifo_num), file=open(filename, "a")
    )

def connectSubscriber(node_name:str, port_name:str, topic_name:str, fifo_num:int):
    print("connect_bd_intf_net [get_bd_intf_pins {}/axis_data_fifo_{}/M_AXIS] [get_bd_intf_pins {}_0/{}_V]".format(
        topic_name, fifo_num, node_name, port_name), file=open(filename, "a")
    )

def searchBoardFile(board_name: str):
    for f in glob.glob(str(Path(os.path.dirname(__file__)) / "board_files" / "**" / "**.toml"), recursive = True):
        if f.split("/")[-1] == (board_name + ".toml"):
            return toml.load(open(f))
    return None

def tclgen(config:dict):
    if "board" not in config.keys():
        print("Error! board name not found!!", file=sys.stderr)
        exit(1)
    board_file = searchBoardFile(config["board"])
    if board_file is None:
        print("Error! board file '{}' not found!".format(config["board"]), file=sys.stderr)
        exit(1)

    directory_name = "build"
    project_name = "project"
    board_name = board_file["part"]

    initialProcedure(directory_name, project_name, board_name, os.path.abspath("."))

    print("\n# generate nodes", file=open(filename, "a"))
    node_gen = NodeGenerator()
    for node in config["nodes"]:
        node_gen.generate(node["name"])

    topic_table = {}
    print("\n# generate topics", file=open(filename, "a"))
    topic_gen = TopicGenerator()
    for ip in board_file["IPs"]:
        if ip["name"] == "axis_data_fifo":
            axis_data_fifo = ip
            break
    else:
        print("axis_data_fifo not found! IPs:", board_file["IPs"])
        exit(1)
    for topic in config["topics"]:
        num_of_pub = 0
        for node in config["nodes"]:
            for port in node["ports"]:
                if port["attribute"] == "publisher" and port["topic"] == topic["name"]:
                    num_of_pub += 1
        num_of_sub = 0
        for node in config["nodes"]:
            for port in node["ports"]:
                if port["attribute"] == "subscriber" and port["topic"] == topic["name"]:
                    num_of_sub += 1

        if num_of_pub == 0 or num_of_sub == 0:
            continue

        topic_table[topic["name"]] = (num_of_pub, num_of_sub, topic_gen.count)
        topic_gen.generate(axis_data_fifo, topic["name"], num_of_pub, num_of_sub)

        # connect publishers and subscribers
        count_pub = topic_gen.count - (num_of_pub + num_of_sub)
        count_sub = count_pub + num_of_pub
        for node in config["nodes"]:
            for port in node["ports"]:
                if port["attribute"] == "publisher" and port["topic"] == topic["name"]:
                    connectPublisher(node["name"], port["name"], "topic_" + topic["name"], count_pub)
                    count_pub += 1
                elif port["attribute"] == "subscriber" and port["topic"] == topic["name"]:
                    connectSubscriber(node["name"], port["name"], "topic_" + topic["name"], count_sub)
                    count_sub += 1

    print("\n# clock", file=open(filename, "a"))
    clk_wiz = list(filter(lambda x: x["name"] == "clk_wiz", board_file["IPs"]))[0]
    for ip in board_file["IPs"]:
        if ip["name"] == "clk_wiz":
            clk_wiz = ip
            break
    else:
        print("clk_wiz not found! IPs:", board_file["IPs"])
        exit(1)
    print("create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wiz:{} clk_wiz_0".format(clk_wiz["version"]), file=open(filename, "a"))
    for s in clk_wiz["options"]:
        print("set_property -dict {} [get_bd_cells clk_wiz_0]".format(s), file=open(filename, "a"))
    print("create_bd_port -dir I -type clk clk", file=open(filename, "a"))
    print("set_property CONFIG.FREQ_HZ {} [get_bd_ports clk]".format(board_file["clock"]), file=open(filename, "a"))
    print("connect_bd_net [get_bd_ports clk] [get_bd_pins clk_wiz_0/clk_in1]", file=open(filename, "a"))

    print("## nodes", file=open(filename, "a"))
    for topic in config["nodes"]:
        print("connect_bd_net [get_bd_pins clk_wiz_0/clk_out1] [get_bd_pins {}_0/ap_clk]".format(topic["name"]), file=open(filename, "a"))
    print("## topics", file=open(filename, "a"))
    for info in topic_table.keys():
        print("###", info, file=open(filename, "a"))
        print("for {{set i {}}} {{$i < {}}} {{incr i}} {{".format(topic_table[info][2], sum(topic_table[info])), file=open(filename, "a"))
        print("    connect_bd_net [get_bd_pins clk_wiz_0/clk_out1] [get_bd_pins {topic}/axis_data_fifo_${{i}}/s_axis_aclk]".format(
            topic="topic_"+info,
        ), file=open(filename, "a"))
        print("}", file=open(filename, "a"))
        print("connect_bd_net [get_bd_pins clk_wiz_0/clk_out1] [get_bd_pins {topic}/{broker}_0/ap_clk]".format(
            topic="topic_"+info, broker="broker"+info
        ), file=open(filename, "a"))

    print("\n# reset", file=open(filename, "a"))
    print("create_bd_port -dir I -type rst rst", file=open(filename, "a"))
    print("set_property CONFIG.POLARITY ACTIVE_HIGH [get_bd_ports rst]", file=open(filename, "a"))
    print("create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_0", file=open(filename, "a"))
    print("set_property -dict [list CONFIG.C_SIZE {1} CONFIG.C_OPERATION {not} CONFIG.LOGO_FILE {data/sym_notgate.png}] [get_bd_cells util_vector_logic_0]", file=open(filename, "a"))
    print("connect_bd_net [get_bd_ports rst] [get_bd_pins util_vector_logic_0/Op1]", file=open(filename, "a"))
    print("## nodes", file=open(filename, "a"))
    for topic in config["nodes"]:
        print("connect_bd_net [get_bd_pins util_vector_logic_0/Res] [get_bd_pins {}_0/ap_rst_n]".format(topic["name"]), file=open(filename, "a"))
    print("## topics", file=open(filename, "a"))
    for info in topic_table.keys():
        print("###", info, file=open(filename, "a"))
        print("for {{set i {}}} {{$i < {}}} {{incr i}} {{".format(topic_table[info][2], sum(topic_table[info])), file=open(filename, "a"))
        print("    connect_bd_net [get_bd_pins util_vector_logic_0/Res] [get_bd_pins {topic}/axis_data_fifo_${{i}}/s_axis_aresetn]".format(
            topic="topic_"+info,
        ), file=open(filename, "a"))
        print("}", file=open(filename, "a"))
        print("connect_bd_net [get_bd_pins util_vector_logic_0/Res] [get_bd_pins {topic}/{broker}_0/ap_rst_n]".format(
            topic="topic_"+info, broker="broker"+info
        ), file=open(filename, "a"))

    print("\n# wires", file=open(filename, "a"))
    for port in config["ports"]:
        if port["attribute"] == "output":
            command = "create_bd_port -dir O "
            foundPort = False
            for node in config["nodes"]:
                if node["name"] == port["source"].split(".")[0]:
                    for _port in node["ports"]:
                        if port["source"].split(".")[1] == _port["name"]:
                            if "width" in _port.keys():
                                command += "-from {} -to 0 ".format(_port["width"])
                            foundPort = True
                            break
                    if foundPort:
                        break
            print(command + port["name"], file=open(filename, "a"))
            print("connect_bd_net [get_bd_ports {}] [get_bd_pins {}_0/{}_V]".format(
                port["name"], port["source"].split(".")[0], port["source"].split(".")[1]), file=open(filename, "a")
            )
        else:
            print("Unimplemented:", port)

    finalProcedure(directory_name, project_name, os.path.abspath("."))
