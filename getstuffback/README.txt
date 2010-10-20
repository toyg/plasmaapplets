GetStuffBack 1.0
================

GetStuffBack is a simple applet that will remind you of stuff that people borrowed from you.

Requirements
============

* KDE 4.4 or above
* Python 2.5 or above
* PyQt 4.6 or above
* KDE bindings for Python ("PyKDE") for your KDE version.

Note: the applet has been extensively tested only on KDE 4.5.1 / Kubuntu 10.04 / Python 2.6. 

Installation
============

* From zip: plasmapkg -i getstuffback.zip
* From source (presuming you pulled the entire tree athttp://github.com/toyg/plasmaapplets): ./install-getstuffback.sh  

You can then right-click on your desktop, select Add Widget... and double-click to add the applet to desktop.
NOTE: this applet has been optimized for usage on a desktop/dashboard. Adding it to a Panel might give unpredictable results.

Usage
=====

Simply Add or Remove "loans", specifying the date you expect to get the stuff back. 
Once that date and a following "grace period" has passed, the loan will be highlighted as "overdue".
You can configure the "grace period" length (in days) and the highlighting colour. 

Help
====

* If you know how to translate a Plasma Applet built with Python, please get in touch.

License
=======

Copyright @ 2010 Giacomo Lacava, g.lacava@gmail.com

Licensed under the European Union Public License, Version 1.1.
You may not use this work except in compliance with the Licence.
You may obtain a copy of the Licence at http://ec.europa.eu/idabc/eupl5
Unless required by applicable law or agreed to in writing, 
software distributed under the Licence is distributed on an "AS IS" basis, 
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for specific language governing permissions and limitations under the Licence.
