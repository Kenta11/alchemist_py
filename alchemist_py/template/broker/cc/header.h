#ifndef BROKER{{message_name.upper()}}_H
#define BROKER{{message_name.upper()}}_H

#include <cstdint>

#include "hls_stream.h"

void
broker{{message_name}}(
{% for num in range(pub) %}    hls::stream< uint{{width}}_t > &port_pub_{{num}},
{% endfor %}{% for num in range(sub) %}    hls::stream< uint{{width}}_t > &port_sub_{{num}}{% if num != sub - 1 %},{% endif %}
{% endfor %});

#endif // BROKER{{message_name.upper()}}_H
