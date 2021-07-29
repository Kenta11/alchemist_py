# Overview

Alchemist is an tool for assisting component-oriented FPGA development.
It builds a digital circuit combining circuit components which are written in software programming language (i.e. C-language).
The components are synthesized into HDL (Hardware Description Language) and synthezied, placed and routed onto FPGA using FPGA tools.

# Environment

- OS: Ubuntu 18.04 LTS
- Python 3.7>=
- FPGA tools: Vivado, Vivado HLS (2019.2)
- Fast RTPS (v1.7.2)

# Installation

## Fast RTPS

### Dependency

- g++, make
- CMake
- Git
- JDK8
- Gradle

```
$ sudo apt install build-essential cmake git openjdk-8-jdk gradle -y
$ sudo apt install libncurses5 -y
```

### Fast-RTPS compilation and install

```

$ git clone https://github.com/eProsima/Fast-RTPS
$ cd Fast-RTPS
$ git checkout -b v1.7.2 remotes/origin/release/1.7.2
$ mkdir bulid
$ cd build
$ cmake -DTHIRDPARTY=ON -DBUILD_JAVA=ON ..
$ make -j8
$ sudo make install
```

## Vivado, Vivado HLS

Refer to [Vivado Design Suite User Guide UG973(v2019.1)](https://www.xilinx.com/support/documentation/sw_manuals/xilinx2019_1/ug973-vivado-release-notes-install-license.pdf).

## alchemist_py

```
$ git clone https://github.com/ohkawatks/alchemist_py
$ cd alchemist_py
$ sudo python setup.py install
```

# Uninstall

## Fast RTPS

```
$ echo "fast-rtps install" | sudo dpkg --set-selections
$ sudo apt remove --purge fast-rtps -y
```

## alchemist_py

```
$ sudo pip uninstall alchemist_py
```

# Preparation

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
