
# close block design
validate_bd_design
save_bd_design
close_bd_design [get_bd_designs system]

# generate HDL files
generate_target all [get_files {{path_to_project}}/{{directory_name}}/{{project_name}}.srcs/sources_1/bd/system/system.bd]
make_wrapper -files [get_files {{path_to_project}}/{{directory_name}}/{{project_name}}.srcs/sources_1/bd/system/system.bd] -top
add_files -norecurse {{path_to_project}}/{{directory_name}}/{{project_name}}.srcs/sources_1/bd/system/hdl/system_wrapper.v

add_files -fileset constrs_1 -norecurse {{path_to_project}}/constr.xdc

# synthesis
launch_runs synth_1 -job 8
wait_on_run synth_1

# place and route
launch_runs impl_1 -job 8
wait_on_run impl_1

# report
open_run    impl_1
report_utilization -file [file join $project_directory "project.rpt" ]
report_timing      -file [file join $project_directory "project.rpt" ] -append

# generate bitstream
launch_runs impl_1 -to_step write_bitstream -job 8
wait_on_run impl_1
