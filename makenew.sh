#!/bin/bash
name=$1
for dir in contents/code config configui ui images translations
do
	mkdir -p $name/$dir
done
echo "[Desktop Entry]
Encoding=UTF-8
Name=$name
Type=Service
ServiceTypes=Plasma/Applet
Icon=icon.png
X-Plasma-API=python
X-Plasma-MainScript=code/main.py
X-KDE-PluginInfo-Author=Giacomo Lacava
X-KDE-PluginInfo-Email=g.lacava@gmail.com
X-KDE-PluginInfo-Name=$name
X-KDE-PluginInfo-Version=1.0
X-KDE-PluginInfo-Website=http://blog.pythonaro.com
X-KDE-PluginInfo-Category=Utilities
X-KDE-PluginInfo-Depends=
X-KDE-PluginInfo-License=GPL
X-KDE-PluginInfo-EnabledByDefault=true" > $name/metadata.desktop
