#!/bin/sh


echo "Building extension for Chrome. . ."

rm tournesol_extension_chrome.zip
cp manifest_chrome.json manifest.json
zip -r -FS tournesol_extension_chrome.zip * -x *.git* *.zip*
rm manifest.json

echo "Building extension for Firefox. . ."

rm tournesol_extension_firefox.zip
cp manifest_firefox.json manifest.json
zip -r -FS tournesol_extension_firefox.zip * -x *.git* *.zip*
rm manifest.json

echo "Done"
