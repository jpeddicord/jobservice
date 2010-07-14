#!/bin/bash


echo "Scanning SLS definitions"
rm -f po/POTFILES.in
for s in sls/*.xml.in; do
    echo "    inserting $s"
    echo "[type: gettext/xml] $s" >> po/POTFILES.in
done

echo "Generating template"
cd po
intltool-update -p -x -g sls-default
sed -i "s/charset=CHARSET/charset=UTF-8/" sls-default.pot
for p in *.po; do
    echo "Updating $p"
    msgmerge -U --no-wrap -N $p sls-default.pot 
done

cd ..
echo "Merging existing translations into SLS definitions"
for s in sls/*.xml.in; do
    echo "Merging $s"
    intltool-merge -x -u po $s ${s/.in/}
done
