#!/bin/bash
cd taskplasma
zip -r ../taskplasma.zip .
cd ..
plasmapkg -i taskplasma.zip

