#include "broker{{message_name}}.h"

template<typename T>
void
outputMessage(hls::stream<T> &din{% for num in range(sub) %}, hls::stream<T> &dout_{{num}}{% endfor %}) {
    T buf;
    for (unsigned i = 0; i < {{data_count}}; i++) {
        din >> buf;

{% for num in range(sub) %}        dout_{{num}} << buf;
{% endfor %}    }
}

void
broker{{message_name}}(
{% for num in range(pub) %}    hls::stream< uint{{width}}_t > &port_pub_{{num}},
{% endfor %}{% for num in range(sub) %}    hls::stream< uint{{width}}_t > &port_sub_{{num}}{% if num != sub - 1 %},{% endif %}
{% endfor %}) {
#pragma HLS INTERFACE ap_ctrl_none port=return
{% for num in range(pub) %}#pragma HLS INTERFACE axis port=port_pub_{{num}}
{% endfor %}{% for num in range(sub) %}#pragma HLS INTERFACE axis port=port_sub_{{num}}
{% endfor %}{% for num_j in range(pub) %}    if (!port_pub_{{num_j}}.empty()) outputMessage(port_pub_{{num_j}}{% for num_i in range(sub) %}, port_sub_{{num_i}}{% endfor %});
{% endfor %}}
