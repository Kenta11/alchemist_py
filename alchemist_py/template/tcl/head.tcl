set project_directory "{{directory_name}}"
set project_name      "{{project_name}}"
set board_part        "{{board_name}}"

create_project $project_name $project_directory

set_property "board_part" $board_part [current_project]

# add components
lappend ip_repo_path_list [file join "." "nodes"]
lappend ip_repo_path_list [file join "." "brokers"]
set_property ip_repo_paths $ip_repo_path_list [current_fileset]
update_ip_catalog

# generate block design
create_bd_design "system"
open_bd_design { {{path_to_project}}/{{directory_name}}/{{project_name}}.srcs/sources_1/bd/system/system.bd }

