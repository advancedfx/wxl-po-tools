#!/usr/bin/python

# encoding=utf8  
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

import os;
import polib;
from lcid import LCIDs;


if len(sys.argv) <= 2:
    print "Usage: wxl2pot.py <wxl file> <pot file>";
    os._exit(1);

sourcefile = sys.argv[1];
destfile = sys.argv[2];

po = polib.pofile(sourcefile);

if po.percent_translated() < 60:
    print "Skipping " + sourcefile + ": translated at " + str(po.percent_translated()) + "%, below the 60% limit\n";
    os._exit(0);

metadata = po.ordered_metadata();
language = [value for name, value in metadata if name == "Language"]

culture = language[0].lower().replace('_','-');
codepage = LCIDs[culture]['codepage'];
langId = LCIDs[culture]['LCID'];

f = open(destfile,'w');
f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n");
f.write("<WixLocalization Culture=\"" + culture + "\" Codepage=\"" + str(codepage) + "\"\n");
f.write("                 xmlns=\"http://schemas.microsoft.com/wix/2006/localization\">\n");
f.write("\n");
f.write("<!-- This wxl file has been auto generated from a po file -->\n");
f.write("<!-- using https://github.com/sblaisot/wxl-po-tools -->\n");
f.write("<!-- Source File: " + sourcefile + " -->\n");
f.write("\n");

for entry in po:
    if entry.comment != "":
        f.write("\n");
        f.write("  <!--" + entry.comment.replace('\n', ' -->\n  <!--') + " -->\n");
    if entry.msgstr != "":
        translation = entry.msgstr;
    else:
        translation = entry.msgid;
    translation = "&#13;&#10;".join(translation.split("\n")).replace('\r', '');
    f.write("  <String Id=\"" + entry.msgctxt + "\">" + translation + "</String>\n");

f.write("</WixLocalization>\n");
f.close;
