# collectd_graphite - Send measurement data from collectd to graphite

[Graphite](http://graphite.wikidot.com) is a real-time graphing
package that incorporates a fast backend for storing numeric
measurements and a server for reading measurements.

[Collectd](http://collectd.org) is a system monitoring package that
measures many things.

`collectd_graphite` is a very simple python plugin for collectd that
transmits data from collectd to a graphite server.


## Installation

Install the `collectd_graphite` python package:

    $ python setup.py install
    
Import it in the `collectd` configuration file.  For example:

    <LoadPlugin python>
      Globals true
    </LoadPlugin>

    <Plugin python>
      Encoding utf-8
      LogTraces true
      Interactive false
      Import "collectd_graphite"
     
      <Module collectd_graphite>
          TypesDB "/usr/local/share/collectd/types.db"
      </Module>       
    </Plugin>
