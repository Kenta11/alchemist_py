# 概要

alchemistはコンポーネント指向によるFPGA開発のための支援ツールです．
ソフトウェア開発言語で記述された回路コンポーネントを組み合わせてディジタル回路を構築します．
コンポーネントは各種の高位合成系によってHDL (Hardware Description Language) に合成され，
回路開発ツールによって論理合成及び配置配線されます．

# 開発環境

- OS: Ubuntu 18.04 LTS
- Python 3.7>=
- FPGA 開発ツール: Xilinx Vivado and Vivado HLS (2019.2)
- eProsima Fast DDS

# インストール

## Xilinx Vivado, Vivado HLS

Refer to [Vivado Design Suite User Guide UG973(v2019.2)](https://www.xilinx.com/support/documentation/sw_manuals/xilinx2019_2/ug973-vivado-release-notes-install-license.pdf).

## Fast DDS

- 依存パッケージ
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

## Veaker - Alchemistのプラグイン

alchemist_pyは`~/.alchemist/`に配置された設定ファイルやプラグインを適宜読み出します．
ここではVivadoとVivadoHLSを使った開発に必要な最低限の設定を示します．

- ~/.alchemist/config.toml

```
path_to_vivado="/path/to/Xilinx/Vivado/2019.1"

[[plugins]]
repo = 'Kenta11/Veaker_py'
```

- ディレクトリ構成

```
$ tree -L 1 .alchemist
.alchemist
├── config.toml
└── plugins

1 directory, 1 file
```

- プラグイン(Veaker)のインストール

```
$ alchemist plugin install
```
