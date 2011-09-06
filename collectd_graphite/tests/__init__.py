"""
Test the few parts of collectd_graphite that don't depend on collectd.
"""

import unittest
from StringIO import StringIO

from .. import load_type_db, PluginValueSpec


class TestPlugin(unittest.TestCase):
    def test_type_db(self):
        SAMPLE = """
vs_memory       value:GAUGE:0:9223372036854775807
vs_processes        value:GAUGE:0:65535
vs_threads      value:GAUGE:0:65535
#
# Legacy types
# (required for the v5 upgrade target)
#
arc_counts      demand_data:COUNTER:0:U, demand_metadata:COUNTER:0:U, prefetch_data:COUNTER:0:U, prefetch_metadata:COUNTER:0:U
arc_l2_bytes        read:COUNTER:0:U, write:COUNTER:0:U
arc_l2_size     value:GAUGE:0:U
        """

        db = load_type_db(StringIO(SAMPLE))
        self.assertEqual(len(db), 6)
        self.assertTrue("vs_memory" in db)
        self.assertTrue("arc_l2_bytes" in db)

        self.assertEqual(db["vs_memory"], [
            PluginValueSpec(name="value", type="GAUGE",
                            min="0", max="9223372036854775807")])
        self.assertEqual(db["arc_l2_bytes"], [
            PluginValueSpec(name="read", type="COUNTER", min="0", max="U"),
            PluginValueSpec(name="write", type="COUNTER", min="0", max="U")])
