# Overview

Alchemist is an tool for assisting component-oriented FPGA development.
It builds a digital circuit combining circuit components which are written in software programming language (i.e. C-language).
The components are synthesized into HDL (Hardware Description Language) and synthezied, placed and routed onto FPGA using FPGA tools.

# Environment

- OS: Ubuntu 18.04 LTS
- Python 3.7>=
- FPGA tools: Xilinx Vivado and Vivado HLS (2019.2)
- eProsima Fast DDS

# Installation

## Xilinx Vivado and Vivado HLS

Refer to [Vivado Design Suite User Guide UG973(v2019.2)](https://www.xilinx.com/support/documentation/sw_manuals/xilinx2019_2/ug973-vivado-release-notes-install-license.pdf).

## Fast DDS

- Dependency
  - g++, make
  - CMake
  - Git
  - JDK8
  - Gradle

```
$ sudo apt install build-essential cmake git openjdk-8-jdk gradle -y
$ git clone https://github.com/eProsima/Fast-DDS -b v1.7.2
$ mkdir -p Fast-DDS/build
$ cd Fast-DDS/build
$ cmake -DTHIRDPARTY=ON -DBUILD_JAVA=ON ..
$ make -j$(nproc)
$ sudo make install
```

## Alchemist

```
$ sudo apt install python3-pip
$ sudo pip3 install -U pip
$ sudo pip3 install git+https://github.com/Kenta11/alchemist_py
```

## Veaker - the Alchemist plugin 

alchemist_py uses the configuration files and plugins located at `~/.alchemist/`.
Here, the minimum setting required for the development using Vivado and VivadoHLS.

- ~/.alchemist/config.toml

```
path_to_vivado="/path/to/Xilinx/Vivado/2019.2"

[[plugins]]
repo = 'Kenta11/Veaker_py'
```

- Directory

```
$ tree -L 1 .alchemist
.alchemist
├── config.toml
└── plugins

1 directory, 1 file
```

- Installation of Plugin (Veaker)

```
$ alchemist plugin install
```
