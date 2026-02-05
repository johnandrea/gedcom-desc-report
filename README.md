# gedcom-desc-report
Create a descendent report from a genealogy GEDCOM file to be used on the command line for non-interactive operation.

The output is an RTF formatted file which can be converted to PDF or other formats.
Converting to PDF on the command line can be performed with LibreOffice:
```
libreoffice --headless --convert-to pdf filename.rtf
```

## Options ##

--version

Display version number then exit.

--personid= id-value
  
The id of the person to select for the top of the tree. Used in combination with the iditem option.
By default this is the the individual xref in the gedcom file and so may be given as for example
as @i42@ or I42 or just 42.

--iditem=  XREF, REFN or user specified such as EXID, REFNUM, etc.
  
The tag in the gedcom file used to match the specified person. Default is xref which is the gedcom individual identifier.
  When using a non-xref tag, the given personid value must match exactly the value in the gedcom file. The match makes
  use of the readgedcom function find_individuals so an id name such as birth.date may be used or for a custom event such as
  event.extraref If more than one match is found the first (unordered) one is taken.
  
--dates
  
Include birth and death years with the names.

--title= page title

If missing the name of the top person is used.

--preparer= name of person who prepared report

If supplied the name will be listed on the page footer along with the current time.

--dots= number of dots

Number of dots to prefix every line. Default is 4. If less than 1, tabs will be used.

--maxgen= maximum generations to show. If missing, there is no limit. The person at the top of the list is generation 1.

--namesize= size of font for the names

--headsize= size of font for the title

--footsize= size of font for the footer

--libpath=directory-containing-readgedcom

Location containing the readgedcom.py library file. The path is relative to the program being used. An absolute path will not work. Default is the same location as the program (".").

## Usage ##

Minimal usage
```
gedcom-desc-report.py gedcom-file > file.rtf
```

More complete usage
```
gedcom-desc-report.py --title="Example report" --preparer="John A." --dots=2 --prerson=12 family.ged > family.rtf
```

## Installation ##

- Requires python 3.6+
- Copy Python file and supporting style file(s).
- also requires gedcom library [readgedcom.py](https://github.com/johnandrea/readgedcom)

## Limitations ##
  
- Not tested with Unicode characters
