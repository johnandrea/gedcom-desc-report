@echo off

if exist r.err del r.err
if exist family.rtf del family.rtf
if exist family.pdf del family.pdf

rem note that the library path is relative to the script path

..\gedcom-desc-report.py --title="Example report" --prep="John A." --dots=2 --person=12 --lib=..\readgedcom family.ged >family.rtf 2>r.err

rem convert rft to pdf without interaction

"C:\Program Files\LibreOffice\program\swriter" --headless --convert-to pdf family.rtf
