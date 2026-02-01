#!/usr/bin/python3

"""
Create a descendent report from a gedcom file.

This code is released under the MIT License: https://opensource.org/licenses/MIT
Copyright (c) 2026 John A. Andrea

No support provided.
"""

import sys
import re
import argparse
import importlib.util
import os


def get_version():
    return '0.0.3'


def load_my_module( module_name, relative_path ):
    """
    Load a module in my own single .py file. Requires Python 3.6+
    Give the name of the module, not the file name.
    Give the path to the module relative to the calling program.
    Requires:
        import importlib.util
        import os
    Use like this:
        readgedcom = load_my_module( 'readgedcom', '../libs' )
        data = readgedcom.read_file( input-file )
    """
    assert isinstance( module_name, str ), 'Non-string passed as module name'
    assert isinstance( relative_path, str ), 'Non-string passed as relative path'

    file_path = os.path.dirname( os.path.realpath( __file__ ) )
    file_path += os.path.sep + relative_path
    file_path += os.path.sep + module_name + '.py'

    assert os.path.isfile( file_path ), 'Module file not found at ' + str(file_path)

    module_spec = importlib.util.spec_from_file_location( module_name, file_path )
    my_module = importlib.util.module_from_spec( module_spec )
    module_spec.loader.exec_module( my_module )

    return my_module


def get_program_options():
    results = dict()

    results['dots'] = 4
    results['maxgen'] = 1_000_000 #just an impossibly large number
    results['title'] = None
    results['personid'] = None
    results['iditem'] = 'xref'
    results['dates'] = False
    results['libpath'] = '.'
    results['infile'] = None

    arg_help = 'Descendent report.'
    parser = argparse.ArgumentParser( description=arg_help )

    arg_help = 'Show version then exit.'
    parser.add_argument( '--version', action='version', version=get_version() )

    arg_help = 'Number of dots as prefix. Output format. Default: ' + str(results['dots'])
    parser.add_argument( '--dots', default=str(results['dots']), type=int, help=arg_help )

    arg_help = 'Maximum number of generations. Output format. If missing there is no limit'
    parser.add_argument( '--maxgen', default=str(results['maxgen']), type=int, help=arg_help )

    arg_help = 'Title. If missing: name of top pereon.'
    parser.add_argument( '--title', type=str, help=arg_help )

    arg_help = 'Id for the person chosen at the top of the report.'
    parser.add_argument( '--personid', type=str, help=arg_help )

    arg_help = 'How to find the person. Default is the gedcom id "xref".'
    arg_help += ' Othewise choose "exid", "refnum", etc.'
    parser.add_argument( '--iditem', default=results['iditem'], type=str, help=arg_help )

    arg_help = 'Show dates along with the names.'
    parser.add_argument( '--dates', default=results['dates'], action='store_true', help=arg_help )

    # maybe this should be changed to have a type which better matched a directory
    arg_help = 'Location of the gedcom library. Default is current directory.'
    parser.add_argument( '--libpath', default=results['libpath'], type=str, help=arg_help )

    parser.add_argument('infile', type=argparse.FileType('r') )

    args = parser.parse_args()

    results['dots'] = int( args.dots )
    results['maxgen'] = int( args.maxgen )
    results['title'] = args.title
    results['personid'] = args.personid
    results['iditem'] = args.iditem.lower()
    results['dates'] = args.dates
    results['infile'] = args.infile.name
    results['libpath'] = args.libpath

    return results


def get_indi_years( indi ):
    # return ( birth - death ) or (birth-) or (-death)
    # but None if both dates are empty

    def get_indi_year( indi_data, tag ):
        # "best" year for birth, death, ...
        # or an empty string
        result = ''

        best = 0
        if readgedcom.BEST_EVENT_KEY in indi_data:
           if tag in indi_data[readgedcom.BEST_EVENT_KEY]:
              best = indi_data[readgedcom.BEST_EVENT_KEY][tag]
        if tag in indi_data:
           if indi_data[tag][best]['date']['is_known']:
              result = str( indi_data[tag][best]['date']['min']['year'] )
        return result

    result = None

    birth = get_indi_year( data[ikey][indi], 'birt' ).strip()
    death = get_indi_year( data[ikey][indi], 'deat' ).strip()
    if birth or death:
       result = '(' + birth +'-'+ death + ')'

    return result


def find_other_partner( indi, fam ):
    result = None

    other_partners = dict()
    other_partners['husb'] = 'wife'
    other_partners['wife'] = 'husb'

    other = None
    for partner in other_partners:
        if partner in data[fkey][fam]:
           if indi == data[fkey][fam][partner][0]:
              other = other_partners[partner]
              break

    if other:
       if other in data[fkey][fam]:
          result = data[fkey][fam][other][0]

    return result


def get_name( indi, style, line_break=' ' ):
    # ouput formats deal with text in different "styles" for non-ascii characters

    result = 'none'

    if indi is not None:
       result = data[ikey][indi]['name'][0][style]
       if readgedcom.UNKNOWN_NAME in result:
          # change to word with no special characters
          result = 'unknown'
       else:
          # remove any suffix after the end slash
          result = re.sub( r'/[^/]*$', '', result ).replace('/','').strip()

          if style == 'html'
             # escape quotes
             result = result.replace('"','&quot;').replace("'","&rsquo;")

          if options['dates']:
             dates = get_indi_years( indi )
             if dates:
                result += line_break + dates

    return result


def find_person( person, item ):
    # it is possible that the selected person is not found
    # or more than one

    if item == 'xref':
       result = []

       # ensure the person lookup is the same as what it used in gedcom
       # if given  5  change to  @I5@
       person = 'i' + person.lower()
       person = '@' + person.replace( 'ii', 'i' ) + '@'
       person = person.replace( '@@', '@' )

       for indi in data[ikey]:
           rec_no = data[ikey][indi]['file_record']['index']
           rec_key = data[ikey][indi]['file_record']['key']
           if person == data[rec_key][rec_no]['tag'].lower():
              result.append( indi )
              # assume only one xref indi
              break

       return result

    return readgedcom.find_individuals( data, item, person )


def escape_rtf( s ):
    # not yet handling high-bit characters
    s = s.replace( "\\", "\\\\" )
    s = s.replace( "{", "\\{" )
    s = s.replace( "}", "\\}" )
    return s


def output_header( indi, title ):
    #{\\rtf1\\ansi\\deff0
    #
    #{\\fonttbl
    #{\\f0 Times New Roman;}
    #{\\f1 Helvetica;}
    #}
    #
    #\\deflang1033\\widowctrl
    #\\margl275 \\margr275 \\margt275 \\margb275
    #
    #{\\pard\\b1\\fs36
    # <title>
    # \\b0\\par}
    #
    #  {\\footer\\f1\\fs15\\b1\\qr <date> \\tab $url \\b0\\footer}
    if title:
       print( title )
    else:
       print( 'Descendents of', get_name(indi, name_style) )
    print( '' )


def output_trailer():
    print( '}' )


def output_family_names( indi, fam, gen, dots ):
    prefix = dots + str(gen)
    print( prefix, get_name(indi, name_style) )
    partner = find_other_partner( indi, fam )
    prefix = ' ' * len(prefix)
    name = '?'
    if partner:
       name = get_name(partner, name_style)
    print( prefix + '+', name )


def output_indi_name( indi, gen, dots ):
    print( dots + str(gen), get_name(indi, name_style) )


def output( start_indi, max_gen, dots ):
    def output_desc( indi, gen, show_dots ):
        if 'fams' in data[ikey][indi]:
           for fam in data[ikey][indi]['fams']:
               output_family_names( indi, fam, gen, show_dots )
               if fam not in fams_touched:
                  fams_touched.append( fam )
                  if gen < max_gen:
                     if 'chil' in data[fkey][fam]:
                        for child in data[fkey][fam]['chil']:
                            output_desc( child, gen+1, show_dots + dots )
        else:
           output_indi_name( indi, gen, show_dots )

    # prevent loop
    fams_touched = []

    output_desc( start_indi, 1, '' )


# the type of name converted name suited for rtf output
name_style = 'html'

options = get_program_options()

readgedcom = load_my_module( 'readgedcom', options['libpath'] )

ikey = readgedcom.PARSED_INDI
fkey = readgedcom.PARSED_FAM

data = readgedcom.read_file( options['infile'] )

indi_found = find_person( options['personid'], options['iditem'] )
if indi_found:
   if len( indi_found ) == 1:
      output_header( indi_found[0], options['title'] )
      dots = '\\tab'
      if options['dots'] > 0:
         dots = '.' * options['dots']
      output( indi_found[0], options['maxgen'], dots )
      output_trailer()
   else:
      print( 'Found more than one start person', options['personid'], 'in', options['iditem'], file=sys.stderr )
      sys.exit(1)
else:
   print( 'Did not locate start person', options['personid'], 'in', options['iditem'], file=sys.stderr )
   sys.exit(1)
