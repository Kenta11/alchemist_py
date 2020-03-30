open_project $env(HLS_TARGET)

add_files $env(HLS_SOURCE) -cflags "-Iinclude/ -std=c++11"
