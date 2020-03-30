open_project  $env(HLS_TARGET)
open_solution $env(HLS_SOLUTION)

set_top $env(HLS_TARGET)
set_part {{PART}}
create_clock -period {{CLOCK}} -name default

config_rtl -module_auto_prefix

source "directives.tcl"

csynth_design
