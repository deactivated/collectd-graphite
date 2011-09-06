"""
A python plugin for collectd that writes data to a Graphite server
"""

import socket
import re
from collections import namedtuple

try:
    import collectd
except ImportError:
    collectd = None


config = {
    "carbon": {
        "host": "127.0.0.1",
        "port": 2003},
    "type_db": "/opt/collectd/share/collectd/types.db"
}
type_db = {}
sock = None


PluginValueSpec = namedtuple("PluginValueSpec", "name type min max")


def load_type_db(f):
    """
    Read a collectd plugin specification file.  Returns a dictionary mapping
    plugin name to a list of PluginValueSpec objects.
    """
    types = {}
    for l in f:
        m = re.match(
            r"(?P<type_name>[^#\s]+)\s+(?P<type_desc>.*)",
            l.strip())
        if m:
            types[m.group("type_name")] = [
                PluginValueSpec(name=val_name, type=val_type,
                                min=val_min, max=val_max)
                for val_name, val_type, val_min, val_max in
                re.findall(r"([^,\s]+):([^,\s]+):([^,\s]+):([^,\s]+)",
                           m.group("type_desc"))]
    return types


def handle_config(config):
    "The collectd config callback."
    d = dict((c.key, c.values) for c in config.children)
    if "Host" in d:
        config["carbon"]["host"] = d["Host"][0]
    if "Port" in d:
        config["carbon"]["port"] = int(d["Port"][0])
    if "TypeDB" in d:
        config["type_db"] = d["TypeDB"][0]


def init_type_db():
    "Read the collectd type database."
    global type_db
    type_db = load_type_db(config["type_db"])


def init_socket():
    "Initialize the connection to Carbon."
    global sock
    sock = socket.socket()
    sock.settimeout(1)
    sock.connect((config["carbon"]["host"],
                  config["carbon"]["port"]))


def handle_init():
    "The collectd init callback."
    init_type_db()
    init_socket()


def s(f, *args):
    return f % args if all(args) else ""


def value_key(v, value_desc=None):
    "Given a collectd value object, return a formatted key for Graphite."
    plugin = "%s%s" % (v.plugin, s("_%s", v.plugin_instance))

    # Instance name and type.  Order depends on plugin.
    if v.plugin == "interface":
        # e.g. eth0.if_errors
        value_type = "%s.%s" % (v.type_instance, v.type)
    elif v.plugin in ("cpu", "memory"):
        # e.g. idle
        value_type = "%s" % (v.type_instance)
    else:
        # e.g. swap_free
        value_type = "%s%s" % (v.type, s("_%s", v.type_instance))

    # Add plugin name and hostname.
    if plugin == value_type:
        key = "collectd.%s.%s" % (v.host, plugin)
    else:
        key = "collectd.%s.%s.%s" % (v.host, plugin, value_type)

    # Add descriptive name from type database, if available
    if value_desc and len(type_db[v.type]) > 1:
        key = "%s.%s" % (key, value_desc.name)

    return key


def handle_write(vl, data=None):
    "The collectd write callback."
    global sock

    if vl.type not in type_db:
        return

    # Only retry once in this loop to avoid blocking collectd.
    if sock is None:
        try:
            init_socket()
        except socket.error:
            return

    lines = []
    for val_type, val in zip(type_db[vl.type], vl.values):
        key = value_key(vl, val_type)
        lines.append("%s %f %d\n" % (key, val, vl.time))

    try:
        sock.sendall(''.join(lines))
    except socket.error:
        # Wait until the next pass to reconnect
        sock = None


if collectd:
    collectd.register_config(handle_config)
    collectd.register_init(handle_init)
    collectd.register_write(handle_write)
