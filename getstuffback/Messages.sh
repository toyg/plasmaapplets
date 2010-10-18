#!/bin/sh
# extract ui strings
extractrc `find . -name \*.rc -o -name \*.ui -o -name \*.kcfg` --language=Python >> rc.py
# call xgettext on all source files, including the one we just generated
xgettext --copyright-holder="Giacomo Lacava"  --from-code=UTF-8 --kde -ci18n -ki18n:1 -ki18nc:1c,2 -ki18np:1,2 -ki18ncp:1c,2,3 -ktr2i18n:1 -kI18N_NOOP:1 -kI18N_NOOP2:1c,2 -kI18N_NOOP2_NOSTRIP:1c,2 -kaliasLocale -kki18n:1 -kki18nc:1c,2 -kki18np:1,2 -kki18ncp:1c,2,3 --msgid-bugs-address=g.lacava@gmail.com --package-name=getstuffback --package-version=1.0 -L Python -o translations/getstuffback.pot `find . -name \*.py` 

# clean up
rm -f rc.py
