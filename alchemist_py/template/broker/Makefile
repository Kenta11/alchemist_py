# Variable
## Commands
VIVADO_HLS := $(shell python3 -c "import os, toml, pathlib; print(pathlib.Path(toml.load(os.path.expanduser('~/.alchemist/config.toml'))['path_to_vivado'])/'bin'/'vivado_hls')")

## Files
export HLS_TARGET   := broker{{TARGET}}
export HLS_SOLUTION := {{SOLUTION}}
HLS_HEADER          := $(wildcard include/*)
export HLS_SOURCE   := $(wildcard src/*)

## Products
IP  := $(HLS_TARGET)/$(HLS_SOLUTION)/impl
HDL := $(HLS_TARGET)/$(HLS_SOLUTION)/syn

# Rules
.PHONY: all
all: $(IP)

$(IP): $(HDL)
	$(VIVADO_HLS) script/export.tcl
	touch $@

$(HDL): $(HLS_TARGET) $(HLS_HEADER) $(HLS_SOURCE)
	$(VIVADO_HLS) script/csynth.tcl
	touch $@

$(HLS_TARGET):
	$(VIVADO_HLS) script/init.tcl

.PHONY: clean
clean:
	rm -rf $(HLS_TARGET) *.log
