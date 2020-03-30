# alchemistとは

alchemistはコンポーネント指向によるFPGA開発のための支援ツールです．
ソフトウェア開発言語で記述された回路コンポーネントを組み合わせてディジタル回路を構築します．
コンポーネントは各種の高位合成系によってHDL (Hardware Description Language) に合成され，
回路開発ツールによって論理合成及び配置配線されます．

# 開発環境

- OS: Ubuntu 18.04 LTS
- Python 3.7>=
- FPGA 開発ツール: Vivado, Vivado HLS (2019.1)
- Fast RTPS (v1.7.2)

# インストール

## Fast RTPS

### 必要なツール

- g++, make
- CMake
- Git
- JDK8
- Gradle
- checkinstall

```
$ sudo apt install build-essential cmake git openjdk-8-jdk gradle checkinstall -y
```

### Fast-RTPSのコンパイルとインストール

```

$ git clone https://github.com/eProsima/Fast-RTPS
$ cd Fast-RTPS
$ git checkout -b build v1.7.2
$ mkdir bulid
$ cd build
$ cmake -DTHIRDPARTY=ON -DBUILD_JAVA=ON ..
$ make -j`grep processor /proc/cpuinfo | wc -l`
$ sudo checkinstall --maintainer `whoami` --pkgname fast-rtps --default
$ echo "fast-rtps hold" | sudo dpkg --get-selections
```

## Vivado, Vivado HLS

Refer to [Vivado Design Suite User Guide UG973(v2019.1)](https://www.xilinx.com/support/documentation/sw_manuals/xilinx2019_1/ug973-vivado-release-notes-install-license.pdf).

## alchemist

```
$ sudo pip install https://github.com/Kenta11/alchemist
```

# アンインストール

## Fast RTPS

```
$ echo "fast-rtps install" | sudo dpkg --set-selections
$ sudo apt remove --purge fast-rtps -y
```

## alchemist

```
$ sudo pip uninstall alchemist
```

# 準備

alchemistは`~/.alchemist/`に配置された設定ファイルやプラグインを適宜読み出します．
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

- プラグイン(veaker)のインストール

```
$ alchemist plugin install
```
