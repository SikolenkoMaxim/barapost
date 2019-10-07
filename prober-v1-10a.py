#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Version 1.10.a
# 07.10.2019 edition

# |===== Check python interpreter version =====|

from sys import version_info as verinf

if verinf.major < 3:
    print( "\nYour python interpreter version is " + "%d.%d" % (verinf.major, verinf.minor) )
    print("   Please, use Python 3!\a")
    # In python 2 'raw_input' does the same thing as 'input' in python 3.
    # Neither does 'input' in python2.
    raw_input("Press ENTER to exit:")
    exit(1)
# end if

print("\n |=== prober-v1-10a.py ===|\n")

# |===== Stuff for dealing with time =====|

from time import time, strftime, localtime, sleep, gmtime
start_time = time()


def get_work_time():
    return strftime("%H:%M:%S", gmtime( time() - start_time))
# end def get_work_time

# |===========================================|

import os
from re import search as re_search

# |===== Function that asks to press ENTER on Windows =====|

from sys import platform

def platf_depend_exit(exit_code):
    """
    Function asks to press ENTER press on Windows
        and exits after that.

    :type exit_code: int;
    """

    if platform.startswith("win"):
        input("Press ENTER to exit:")
    # end if
    exit(exit_code)
# end def platf_depend_exit


def err_fmt(text):
    """Function for configuring error messages"""
    return "\n   \a!! - ERROR: " + text + '\n'
# end def print_error


from sys import stdout as sys_stdout
def printn(text):
    """
    Function prints text to the console without adding '\n' in the end of the line.
    Why not just to use 'print(text, end="")'?
    In order to display informative error message if Python 2.X is launched
        instead if awful error traceback.
    """
    sys_stdout.write(text)
# end def printn

# |===== Handle command line arguments =====|
help_msg = """
DESCRIPTION:\n
  prober-v1-10a.py -- this program is designed for determinating the taxonomic position
of nucleotide sequences by sending each of them to NCBI BLAST server and regarding the best hit.\n
  The main goal of this program is to send a probing batch of sequences to NCBI BLAST server
and discover, what Genbank records can be downloaded and used for building a database
on your local machine by "barapost-v3-4a.py".\n
  This program processes FASTQ and FASTA (as well as '.fastq.gz' and '.fasta.gz') files.\n
  Results of the work of this program are written to TSV files, that can be found in result directory:\n
1) There is a file named `...acc_list.tsv`. It contains accessions and names of Genbank records that
    can be used for building a database on your local machine by "barapost-v3-4a.py".\n
2) There is a file named `...result.tsv`. It contains full result of "BLASTing".\n
    Results of barapost-v3-4a.py's work will be appended to this file\n
  Files processed by this program are meant to be processed afterwards by "barapost-v3-4a.py".\n
  If you have your own FASTA files that can be used as database to blast against, you can omit
"prober-v1-10a.py" step and go to "barapost-v3-4a.py" (see `-l` option in "barapost-v3-4a.py" description).
----------------------------------------------------------\n
Default parameters:\n
- all FASTQ and FASTA files in current directory will be processed;
- packet size (see '-p' option): 100 sequences;
- probing batch size (see '-b' option): 200 sequences;
- algorithm (see '-a' option): 'megaBlast';
- organisms (see '-g' option): full 'nt' database, i.e. no slices;
- output directory ('-o' option): directory named "prober_result"
  nested in current directory;\n
  Default behavior of this script is to send certain batch (see '-b' option) of sequences to BLAST server.
It means that you should not process all your data by 'prober-v1-10a.py' -- it would take long time.\n
  Instead of this you should process some sequences by 'prober-v1-10a.py' -- it will determine,
what Genbank records (genomes, if you want) are present in your data and then go to 'barapost-v3.4a.py'.\n
  'barapost-v3.4a.py' will process the rest of you sequences in the same way like 'prober-v1-10a.py', but on your local computer.
'barapost-v3.4a.py' uses 'BLAST+' toolkit for this purpose. It would be much faster.\n
  Obviously, a probing batch cannot cover all variety of a data set,
so some sequences can be recognized as "unknown" while processing by 'barapost-v3-4.py'.
But you always can run 'prober-v1-10a.py' again on "unknown" sequences.
----------------------------------------------------------\n
Files that you want 'prober-v1-10a.py' to process should be specified as positional arguments (see EXAMPLE #2 below).
  Wildcards do work: './prober-v1-10a.py my_directory/*'' will process all files in 'my_directory'.
----------------------------------------------------------\n
OPTIONS:\n
    -h (--help) --- show help message;\n
    -d (--indir) --- directory which contains FASTQ of FASTA files meant to be processed.
        I.e. all FASTQ and FASTA files in this direcory will be processed;
        Input files can be gzipped.\n
    -o (--outdir) --- output directory;\n
    -p (--packet-size) --- size of the packet, i.e. number of sequence to blast in one request.
        Value: integer number [1, 500]. Default value is 100;\n
    -a (--algorithm) --- BLASTn algorithm to use for aligning.
        Available values: 'megaBlast', 'discoMegablast', 'blastn'.
        Default is megaBlast;\n
    -g (--organisms) --- 'nt' database slices, i.e. organisms that you expect to see in result files.
        More clearly, functionality of this option is totally equal to "Organism" text boxes
        on this BLASTn page:
         'https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastn&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome'.
        Format of value: 
          <organism1_name>,<organism1_taxid>+<organism2_name>,<organism2_taxid>+...
        See EXAMPLES #2 and #3 below.
        Spaces are not allowed. Number of organisms can be from 1 to 5 (5 is maximum).
        Default value is full 'nt' database.
        You can find your Taxonomy IDs here: 'https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi'.\n
    -b (--probing-batch-size) --- number of sequences that will be aligned on BLAST server
        during 'prober-v1-10a.py' work.
        You can specify '-b all' to process all your sequeces by 'prober-v1-10a.py'.
        Value: positive integer number.
        Default value is 200;\n
----------------------------------------------------------\n
EXAMPLES:\n
  1. Process all FASTA and FASTQ files in working directory with default settings:\n
    ./prober-v1-10a.py\n
  2. Process all files in the working directory that start with "some_my_fasta". Use default settings:\n
    ./prober-v1-10.py some_my_fasta*\n
  3. Process one file with default settings:\n
    ./prober-v1-10a.py reads.fastq\n
  4. Process a FASTQ file and a FASTA file with discoMegablast, packet size of 100 sequences.
Search only among Erwinia sequences (551 is Erwinia taxid):\n
    ./prober-v1-10a.py reads_1.fastq.gz some_sequences.fasta -a discoMegablast -p 100 -g Erwinia,551\n
  5. Process all FASTQ and FASTA files in directory named `some_dir`. Process 300 sequences, packet size is 100 sequnces (3 packets will be sent).
Search only among Escherichia and viral sequences:\n
    ./prober-v1-10a.py -d some_dir -g Escherichia,561+viruses,10239 -o outdir -b 300 -p 100
"""
from sys import argv
import getopt

try:
    opts, args = getopt.gnu_getopt(argv[1:], "hd:o:p:a:g:b:",
        ["help", "indir=", "outdir=", "packet-size=", "algorithm=", "organisms=", "probing-batch-size="])
except getopt.GetoptError as gerr:
    print( str(gerr) )
    platf_depend_exit(2)
# end try

is_fq_or_fa = lambda f: True if not re_search(r".*\.(m)?f(ast)?(a|q)(\.gz)?$", f) is None else False

# Default values:
fq_fa_list = list()
indir_path = None
outdir_path = "prober_result"
packet_size = 100
probing_batch_size = 200
send_all = False
blast_algorithm = "megaBlast"
organisms = list() # default is whole 'nt' database

# Add positional arguments to fq_fa_list
for arg in args:
    if not os.path.exists(arg) or not is_fq_or_fa(arg):
        print(err_fmt("invalid positional argument: '{}'".format(arg)))
        print("Only FAST(A/Q) files can be specified without an option in command line.")
        platf_depend_exit(1)
    # end if
    fq_fa_list.append( os.path.abspath(arg) )
# end for

for opt, arg in opts:
    
    if opt in ("-h", "--help"):
        print(help_msg)
        platf_depend_exit(0)
    # end if
    
    if opt in ("-d", "--indir"):
        if not os.path.exists(arg):
            print(err_fmt("directory '{}' does not exist!".format(arg)))
            platf_depend_exit(1)
        # end if
        
        if not os.path.isdir(arg):
            print(err_fmt("'{}' is not a directory!".format(arg)))
            platf_depend_exit(1)
        # end if
        
        indir_path = os.path.abspath(arg)

        paths_buff = list( filter(is_fq_or_fa, os.listdir(indir_path)) )
        fq_fa_list.extend(list(map(lambda f: os.path.join(indir_path, f), paths_buff)))
    # end if

    if opt in ("-o", "--outdir"):
        outdir_path = os.path.abspath(arg)
    # end if

    if opt in ("-p", "--packet-size"):
        try:
            packet_size = int(arg)
            if packet_size < 1 or packet_size > 500:
                raise ValueError
            # end if
        except ValueError:
            print(err_fmt("packet_size (-p option) must be integer number from 1 to 500"))
            platf_depend_exit(1)
        # end try
    # end if

    if opt in ("-a", "--algorithm"):
        if not arg in ("megaBlast", "discoMegablast", "blastn"):
            print(err_fmt("invalid value specified by '-a' option!"))
            print("Available values: 'megaBlast', 'discoMegablast', 'blastn'")
            platf_depend_exit(1)
        # end if
        blast_algorithm = arg
    # end if

    if opt in ("-g", "--organisms"):
        max_org = 5

        try:
            org_list = arg.strip().split('+')
            org_list = list( map(str.strip, org_list) )
            if len(org_list) > max_org:
                raise Exception("\nYou can specify from 1 to {} organisms.\a".format(max_org))
            # end if

            for org in org_list:
                name_and_taxid = org.strip().split(',')
                name_and_taxid = list( map(str.strip, name_and_taxid) )
                if len(name_and_taxid) != 2:
                    raise Exception("""\nOrganism's name and it's taxid should be separated by comma (,),
    and different organisms -- by plus (+).\n  Type for help: ./baparost.py -h\a""")
                # end if
                # Validate TaxID integer format: it will raise ValueError if taxid is invalid
                tmp_taxid = int(name_and_taxid[1])
                if tmp_taxid < 1:
                    raise ValueError("\nTaxID should be positive integer number\a")
                # end if
                organisms.append("{} (taxid:{})".format(name_and_taxid[0], name_and_taxid[1]))
            # end for
        except ValueError:
            print("\n" + "=/"*20 + "\n")
            print(err_fmt("TaxID should be positive integer number\a"))
            platf_depend_exit(1)
        except Exception as err:
            print("\n" + "=/"*20 + "\n")
            print(err_fmt("ERROR: invalid organisms (-g option) input format"))
            print( str(err) )
            platf_depend_exit(1)
        # end try
    # end if

    if opt in ("-b", "--probing-batch-size"):
        # Switch 'send_all' to True in order to process all sequences
        if arg == "all":
            send_all = True
            continue
        # end if
        try:
            probing_batch_size = int(arg)
            if probing_batch_size <= 0:
                raise ValueError
            # end if
        except ValueError:
            print(err_fmt("probing batch size ('-b' option) must be positive integer number!"))
            platf_depend_exit(1)
        # end try
    # end if
# end for


# If no FASTQ or FASTA file have been found
if len(fq_fa_list) == 0:
    # If input directory was specified -- exit
    if not indir_path is None:
        print(err_fmt("""no input FASTQ or FASTA files specified
    or there is no FASTQ and FASTA files in the input directory.\n"""))
        platf_depend_exit(1)
    
    # If input directory was not specified -- look for FASTQ files in current directory
    else:
        fq_fa_list = list( filter(is_fq_or_fa, os.listdir('.')) )
        if len(fq_fa_list) == 0:
            print(err_fmt("there is no FASTQ or FASTA files to process found."))
            platf_depend_exit(1)
        # end if
    # end if
# end if

fq_fa_list.sort()

from gzip import open as open_as_gzip # input files might be gzipped
from xml.etree import ElementTree # for retrieving information from XML BLAST report
from sys import intern

import http.client
import urllib.request
from urllib.error import HTTPError
import urllib.parse
import socket

# |===== Functionality for proper processing of gzipped files =====|

OPEN_FUNCS = (open, open_as_gzip)

is_gzipped = lambda file: True if file.endswith(".gz") else False
is_fastq = lambda f: True if not re_search(r".*\.fastq(\.gz)?$", f) is None else False

# Data from plain text and gzipped should be parsed in different way,
#   because data from .gz is read as 'bytes', not 'str'.
FORMATTING_FUNCS = (
    lambda line: line.strip(),   # format text line
    lambda line: line.decode("utf-8").strip()  # format gzipped line
)

# Delimiter for result tsv file:
DELIM = '\t'

# File format constants:
FASTQ_LINES_PER_READ = 4
FASTA_LINES_PER_SEQ = 2


# |=== Check if there are enough sequeneces in files (>= probing_batch_size) ===|
seqs_at_all = 0
print() # just print new line
for file in fq_fa_list:
    how_to_open = OPEN_FUNCS[ is_gzipped(file) ]
    if is_fastq(file):
        n_seqs = int( sum(1 for line in how_to_open(file, 'r')) / FASTQ_LINES_PER_READ )
    else:
        n_seqs = sum(1 if line[0] == '>' else 0 for line in how_to_open(file, 'r'))
    # end if
    seqs_at_all += n_seqs
    if seqs_at_all >= probing_batch_size:
        break
    # end if
# end for

# Print a warning message if a user has specified batch size that is greater than number of sequences he has at all.
# And do not disturb him if he has run 'prober-v1-10a.py' with default batch size.
if seqs_at_all < probing_batch_size and ("-b" in argv or "--probing_batch_size" in argv):
    if send_all:
        probing_batch_size = seqs_at_all
    else:
        print('\n'+'-'*20)
        print("\a  Warning!\n There are totally {} sequences in your files.".format(seqs_at_all))
        print(" Probing batch size specified by you is {}".format(probing_batch_size))

        while True:
            reply = input("\nPress ENTER to process all your sequences anyway.\n  Or enter 'q' to exit:>>")
            if reply == "":
                probing_batch_size = seqs_at_all
                break
            elif reply == 'q':
                platf_depend_exit(0)
            else:
                print(err_fmt("invalid reply"))
                continue
            # end if
        # end while
    # end if
# end if

if seqs_at_all < probing_batch_size and not ("-b" in argv or "--probing_batch_size" in argv):
    probing_batch_size = seqs_at_all
# end if

del help_msg # we do not need this large string object any more

if not os.path.isdir(outdir_path):
    try:
        os.makedirs(outdir_path)
    except OSError as oserr:
        print_error("unable to create result directory")
        print( str(oserr) )
        print("Prober just tried to create directory '{}' and crushed.".format(outdir_path))
        platf_depend_exit(1)
    # end try
# end if

# There some troubles with file extention on Windows, so let's make a .txt file for it:
log_ext = ".log" if not platform.startswith("win") else ".txt"
logfile_path = os.path.join(outdir_path, "prober_log_{}{}".format(strftime("%d-%m-%Y_%H-%M-%S", localtime(start_time)), log_ext))
logfile = open(logfile_path, 'w')

def printl(text=""):
    """
    Function for printing text to console and to log file.
    """
    print(text)
    logfile.write(str(text).strip('\r') + '\n')
    logfile.flush()
# end def printl

def println(text=""):
    """
    Function for printing text to console and to log file.
    The only difference from 'printl' -- text that is printed to console does not end with '\\n'
    """
    printn(text)
    logfile.write(str(text).strip('\r') + '\n')
    logfile.flush()
# end def printl

logfile.write((" |=== prober-v1-10a.py ===|\n\n"))
printl( get_work_time() + " ({}) ".format(strftime("%d.%m.%Y %H:%M:%S", localtime(start_time))) + "- Start working\n")


# |===== Function for checking if 'https://blast.ncbi.nlm.nih.gov' is available =====|

def check_connection():
    """
    Function checks if 'https://blast.ncbi.nlm.nih.gov' is available.

    :return: None if 'https://blast.ncbi.nlm.nih.gov' is available;
    """

    try:
        ncbi_server = "https://blast.ncbi.nlm.nih.gov"
        status_code = urllib.request.urlopen(ncbi_server).getcode()
        # Just in case
        if status_code != 200:
            printl('\n' + get_work_time() + " - Site 'https://blast.ncbi.nlm.nih.gov' is not available.")
            print("Check your Internet connection.\a")
            printl("Status code: {}".format(status_code))
            platf_depend_exit(-2)
        # end if
        return
    except OSError as err:
        printl('\n' + get_work_time() + " - Site 'https://blast.ncbi.nlm.nih.gov' is not available.")
        print("Check your Internet connection.\a")
        printl( str(err) )

        # 'urllib.request.HTTPError' can provide a user with information about the error
        if isinstance(err, HTTPError):
            printl("Status code: {}".format(err.code))
            printl(err.reason)
        # end if
        platf_depend_exit(-2)
    # end try
# end def check_connection


# |===== Question funtions =====|

def is_continued():
    """
    Function asks the user if he/she wants to continue the previous run.

    :return: True if the decision is to continue, else False;
    :return type: bool;
    """

    continuation = None

    while continuation is None:
        continuation = input("""
Would you like to continue the previous run?
    1. Continue!
    2. Start from the beginning.

Enter the number (1 or 2):>> """)
        # Check if entered value is integer number. If no, give another attempt.
        try:
            continuation = int(continuation)
            # Check if input number is 1 or 2
            if continuation != 1 and continuation != 2:
                print("\n   Not a VALID number entered!\a\n" + '~'*20)
                continuation = None
            else:
                print("You have chosen number " + str(continuation) + '\n')
            # end if
        except ValueError:
            print("\nNot an integer NUMBER entered!\a\n" + '~'*20)
            continuation = None
        # end try

    return(True if continuation == 1 else False)


def get_packet_size(num_reads):
    """
    Function asks the user about how many query sequences will be sent 
        to NCBI BLAST as a particular request.

    :return: the number of query sequences;
    :return type: int;
    """

    packet_size = None
    # You cannot sent more query sequences than you have
    limit = num_reads if num_reads <= 500 else 500

    while packet_size is None:
        
        packet_size = input("""
Please, specify the number of sequences that should be sent to the NCBI server in one request.
E.g. if you have 10 sequences in your file, you can send 10 sequences as single
    request -- in this case you should enter number 10. You may send 2 requests containing
    5 sequences both -- in this case you should enter number 5.


There are {} sequences left to process in current file.
Enter the number (from 1 to {}):>> """.format(num_reads, limit))
        # Check if entered value is integer number. If no, give another attempt.
        try:
            packet_size = int(packet_size)
            # Check if input number is in [1, limit]
            if packet_size < 1 or packet_size > limit:
                print("\n   Not a VALID number entered!\a\n" + '~'*20)
                packet_size = None
            else:
                print("You have chosen number " + str(packet_size) + '\n')
            # end if
        except ValueError:
            print("\nNot an integer NUMBER entered!\a\n" + '~'*20)
            packet_size = None
        # end try
    # end while
    return(packet_size)
# end def get_packet_size


# |===== End of question funtions =====|

get_phred33 = lambda q_symb: ord(q_symb) - 33

def get_read_avg_qual(qual_str):

    phred33 = map(get_phred33, list(qual_str))
    read_qual = round( sum(phred33) / len(qual_str), 2 )
    return read_qual
# end def get_read_avg_qual


def configure_qual_dict(fastq_path):

    qual_dict = dict()
    how_to_open = OPEN_FUNCS[ is_gzipped(fastq_path) ]
    fmt_func = FORMATTING_FUNCS[ is_gzipped(fastq_path) ]

    with how_to_open(fastq_path) as fastq_file:
        counter = 1
        line = fmt_func(fastq_file.readline())
        while line != "":
            if counter == 1:
                seq_id = intern( (line.partition(' ')[0])[1:] )
            # end if
            
            counter += 1
            line = fmt_func(fastq_file.readline())
            if counter == 4:
                qual_dict[seq_id] = get_read_avg_qual(line)
                counter = 0
            # end if
        # end while
    # end with

    return qual_dict
# end def configure_qual_dict


def fastq2fasta(fq_fa_path, i, new_dpath):
    """
    Function conwerts FASTQ file to FASTA format, if there is no FASTA file with
        the same name as FASTQ file. Also it counts sequences in this file.

    :param fq_fa_path: path to FASTQ or FASTA file being processed;
    :type fq_fa_path: str;
    :param i: order number of fq_fa_path;
    :type i: int;
    :param new_dpath: path to current (corresponding to fq_fa_path file) result directory;
    :type new_dpath: str;

    Returns dict of the following structure:
    {
        "fpath": path_to_FASTA_file (str),
        "nreads": number_of_reads_in_this_FASTA_file (int)
    }
    """
    
    fasta_path = os.path.basename(fq_fa_path).replace(".fastq", ".fasta") # change extention
    fasta_path = fasta_path.replace(".gz", "") # get rid of ".gz" extention
    fasta_path = os.path.join(new_dpath, fasta_path) # place FASTA file into result directory

    how_to_open = OPEN_FUNCS[ is_gzipped(fq_fa_path) ]

    fastq_patt = r".*\.f(ast)?q(\.gz)?$"

    num_lines = 0 # variable for counting lines in a file
    if not re_search(fastq_patt, fq_fa_path) is None:

        global FASTQ_LINES_PER_READ

        # Get ready to process gzipped files
        # how_to_open = OPEN_FUNCS[ is_gzipped(fq_fa_path) ]
        fmt_func = FORMATTING_FUNCS[ is_gzipped(fq_fa_path) ]

        with how_to_open(fq_fa_path) as fastq_file, open(fasta_path, 'w') as fasta_file:

            counter = 1 # variable for retrieving only 1-st and 2-nd line of FASTQ record
            for line in fastq_file:
                line = fmt_func(line)
                # write only 1-st and 2-nd line out of 4
                if counter <= 2:
                    if line[0] == '@':
                        line = '>' + line[1:]  # replace '@' with '>'
                    # end if
                    fasta_file.write(line + '\n')
                # reset the counter if the 4-th (quality) line has been encountered
                elif counter == 4:
                    counter = 0
                # end if
                counter += 1
                num_lines += 1
            # end for
        # end with
        num_reads = int(num_lines / FASTQ_LINES_PER_READ) # get number of sequences

        printl("\n{}. '{}' ({} reads) --> FASTA".format(i+1, os.path.basename(fq_fa_path), num_reads))
    
    # IF FASTA file is already created
    # We need only number of sequences in it.
    elif not re_search(fastq_patt, fq_fa_path) is None and os.path.exists(fasta_path):
        num_lines = sum(1 for line in how_to_open(fq_fa_path)) # get number of lines
        num_reads = int( num_lines / FASTQ_LINES_PER_READ ) # get number of sequences
    # We've got FASTA source file
    # We need only number of sequences in it.
    else:
        global FASTA_LINES_PER_SEQ

        num_reads = sum(1 if line[0] == '>' else 0 for line in how_to_open(fq_fa_path, 'r'))
        fasta_path = fq_fa_path
    # end if

    printl("\n |===== file: '{}' ({} sequences) =====|".format(os.path.basename(fasta_path), num_reads))
    return {"fpath": fasta_path, "nreads": num_reads}
# end def fastq2fasta



def rename_file_verbosely(file, directory):

    if os.path.exists(file):

        is_analog = lambda f: file[:os.path.basename(file).rfind('.')] in f
        num_analog_files = len( list(filter(is_analog, os.listdir(directory))) )

        printl('\n' + get_work_time() + " - Renaming old file:")
        name_itself = file[: file.rfind('.')]
        ext = file[file.rfind('.'):]
        num_analog_files = str(num_analog_files)
        new_name = name_itself+"_old_"+num_analog_files+ext

        printl("   '{}' --> '{}'".format(os.path.basename(file), new_name))
        os.rename(file, new_name)
    # end if
# end def rename_file_verbosely


def look_around(outdir_path, new_dpath, fasta_path, blast_algorithm):
    """
    Function looks around in order to ckeck if there are results from previous runs of this script.

    Returns None if there is no result from previous run.
    If there are results from previous run, returns a dict of the following structure:
    {
        "pack_size": packet_size (int),
        "sv_npck": saved_number_of_sent_packet (int),
        "RID": saved_RID (str),
        "tsv_respath": path_to_tsv_file_from_previous_run (str),
        "n_done_reads": number_of_successfull_requests_from_currenrt_FASTA_file (int),
        "tmp_fpath": path_to_pemporary_file (str)
    }

    :param new_dpath: path to current (corresponding to fq_fa_path file) result directory;
    :type new_dpath: str;
    :param fasta_path: path to current (corresponding to fq_fa_path file) FASTA file;
    :type fasta_path: str;
    :param blast_algorithm: BLASTn algorithm to use.
        This parameter is necessary because it is included in name of result files;
    :type blast_algorithm: str;
    """

    # "hname" means human readable name (i.e. without file path and extention)
    fasta_hname = os.path.basename(fasta_path) # get rid of absolute path
    fasta_hname = re_search(r"(.*)\.(m)?f(ast)?a", fasta_hname).group(1) # get rid of '.fasta' extention
    how_to_open = OPEN_FUNCS[ is_gzipped(fasta_path) ]

    # Form path to temporary file
    tmp_fpath = "{}_{}_temp.txt".format(os.path.join(new_dpath, fasta_hname), blast_algorithm)
    # Form path to result file
    tsv_res_fpath = "{}_{}_result.tsv".format(os.path.join(new_dpath, fasta_hname), blast_algorithm)
    # Form path to accession file
    acc_fpath = os.path.join(outdir_path, "{}_probe_acc_list.tsv".format(blast_algorithm))

    num_done_reads = None # variable to keep number of succeffdully processed sequences

    continuation = None
    # Check if there are results from previous run.
    if os.path.exists(tsv_res_fpath) or os.path.exists(tmp_fpath):
        printl('\n' + get_work_time() + " - The previous result file is found in the directory:")
        printl("   '{}'".format(new_dpath))
        # Allow politely to continue from last successfully sent packet.
        continuation = is_continued()
        if not continuation:
            rename_file_verbosely(tsv_res_fpath, new_dpath)
            rename_file_verbosely(tmp_fpath, new_dpath)
            rename_file_verbosely(acc_fpath, new_dpath)
        # end if
    # end if
    
    # Find the name of last successfull processed sequence
    if continuation == True:
        printl("Let's try to continue...")

        # Collect information from result file
        if os.path.exists(tsv_res_fpath):
            # There can be invalid information in this file
            try:
                with open(tsv_res_fpath, 'r') as res_file:
                    lines = res_file.readlines()
                    num_done_reads = len(lines) - 1 # the first line is a head
                    last_line = lines[-1]
                    last_seq_id = last_line.split(DELIM)[0]
                # end with
            except Exception as err:
                printl("\nData in result file '{}' not found or broken. Reason:".format(tsv_res_fpath))
                printl( ' ' + str(err) )
                printl("Start from the beginning.")
                rename_file_verbosely(tsv_res_fpath, new_dpath)
                rename_file_verbosely(tmp_fpath, new_dpath)
                rename_file_verbosely(acc_fpath, new_dpath)
                return None
            else:
                printl("Last sent sequence: " + last_seq_id)
            # end try
        # end if
        
        # Collect information from accession file
        global acc_dict
        if os.path.exists(acc_fpath):
            # There can be invalid information in this file
            try:
                with open(acc_fpath, 'r') as acc_file:
                    lines = acc_file.readlines()[9:] # omit description and head of the table
                    local_files_filtered = list( filter(lambda x: False if os.path.exists(x) else True, lines) ) # omit file paths
                    for line in local_files_filtered:
                        vals = line.split(DELIM)
                        acc = intern(vals[0].strip())
                        acc_dict[acc] = (vals[1].strip(), vals[2].strip(), int(vals[3].strip()))
                    # end for
                # end with
            except Exception as err:
                printl("\nData in accession file '{}' not found or broken. Reason:".format(acc_fpath))
                printl( ' ' + str(err) )
                printl("Start from the beginning.")
                rename_file_verbosely(tsv_res_fpath, new_dpath)
                rename_file_verbosely(tmp_fpath, new_dpath)
                rename_file_verbosely(acc_fpath, new_dpath)
                return None
            else:
                printl("\nHere are Genbank records encountered during previous run:")
                for acc in acc_dict.keys():
                    s_letter = "s" if acc_dict[acc][2] > 1 else ""
                    printl(" {} sequence{} - {}, '{}'".format(acc_dict[acc][2], s_letter, acc, acc_dict[acc][1]))
                # end for
                print()
            # end try
        # end if

        # If we start from the beginning, we have no sequences processed
        if num_done_reads is None:
            num_done_reads = 0
        # end if

        # Get packet size, number of the last sent packet and RID
        # There can be invalid information in tmp file of tmp file may not exist
        try:
            with open(tmp_fpath, 'r') as tmp_file:
                temp_lines = tmp_file.readlines()
            # end with
            packet_size = int(re_search(r"packet_size: ([0-9]+)", temp_lines[0]).group(1).strip())
            saved_npack = int(re_search(r"sent_packet_num: ([0-9]+)", temp_lines[1]).group(1).strip())
            RID_save = re_search(r"Request_ID: (.+)", temp_lines[2]).group(1).strip()
            # If aligning is performed on local machine, there is no reason for requesting results.
            # Therefore this packet will be aligned once again.
        
        except Exception as exc:
            total_num_seqs = sum(1 if line[0] == '>' else 0 for line in how_to_open(fasta_path))
            printl("\n    Attention! Temporary file not found or broken! Reason:")
            printl( ' ' + str(exc) )
            printl("{} sequences have been already processed.".format(num_done_reads))
            printl("There are {} sequences totally in file '{}'.".format(total_num_seqs, os.path.basename(fasta_path)))
            printl("Maybe you've already processed this file with 'prober-v1-10a.py'?\n")

            reply = "BULLSHIT"
            global omit_file
            while True:
                reply = input("Press ENTER to omit this file and go to the next one.\n \
 Or enter 'c' to continue processing this file:>>")
                if reply == 'c':
                    if num_done_reads >= total_num_seqs:
                        printl("There are no sequences left to process in this file. Omitting it.")
                        omit_file = True
                        return
                    # end if
                    
                    break
                elif reply == "":
                    omit_file = True
                    # global seqs_processed
                    # seqs_processed += num_done_reads
                    return
                else:
                    print(err_fmt("invalid reply"))
                # end if
            # end while

            printl("{} reads have been already processed".format(num_done_reads))
            printl("{} reads left".format(total_num_seqs - num_done_reads))
            packet_size = get_packet_size(total_num_seqs - num_done_reads)
            return {
                "pack_size": packet_size,
                "sv_npck": int(num_done_reads / packet_size),
                "RID": None,
                "acc_fpath": acc_fpath,
                "tsv_respath": tsv_res_fpath,
                "n_done_reads": num_done_reads,
                "tmp_fpath": tmp_fpath
            }
        else:
            # Return data from previous run
            return {
                "pack_size": packet_size,
                "sv_npck": saved_npack,
                "RID": RID_save,
                "acc_fpath": acc_fpath,
                "tsv_respath": tsv_res_fpath,
                "n_done_reads": num_done_reads,
                "tmp_fpath": tmp_fpath
            }
        # end try
        
    elif continuation == False:
        # If we've decided to start from the beginnning - rename old files
        rename_file_verbosely(tsv_res_fpath, new_dpath)
        rename_file_verbosely(tmp_fpath, new_dpath)
        rename_file_verbosely(acc_fpath, new_dpath)
    # end if
    
    return None
# end def look_around


def pass_processed_seqs(fasta_file, num_done_reads, fmt_func):
    """
    Function passes sequences that have been already processed.

    :param fasta_file: FASTA file instalce;
    :type fasta_file: str;
    :param num_done_reads: amount of sequences that have been already processed;
    :type num_done_reads: int;
    :param fmt_func: function from 'FORMATTING_FUNCS' tuple;
    """
    
    if num_done_reads == 0:
        return None
    else:
        i = 0
        while i <= num_done_reads:
            line = fmt_func(fasta_file.readline())
            if line .startswith('>'):
                if ' ' in line:
                    line = line.partition(' ')[0]
                # end if
                next_id_line = line
                i += 1
            # end if
        # end while
        return next_id_line
    # end if
# end def pass_processed_seqs


def fasta_packets(fasta, packet_size, reads_at_all, num_done_reads):
    """
    Function (actually, generator) retrieves 'packet_size' records from FASTA file.
    This function will pass 'num_done_reads' sequences (i.e. they will not be processed)
        by calling 'pass_processed_files'.

    :param fasta: path to FASTA file;
    :type fasta: str;
    :param packet_size: number of sequences to align in one 'blastn' launching;
    :type packet_size: int;
    :param reads_at_all: number of sequences in current file;
    :type reads_at_all: int;
    :param num_done_reads: number of sequnces in current file that have been already processed;
    :type num_doce_reads: int;
    """

    how_to_open = OPEN_FUNCS[ is_gzipped(fasta) ]
    fmt_func = FORMATTING_FUNCS[ is_gzipped(fasta) ]

    with how_to_open(fasta) as fasta_file:
        # Next line etrieving will be performed as simple line-from-file reading.
        get_next_line = lambda: fmt_func(fasta_file.readline())

        # Variable that contains id of next sequence in current FASTA file.
        # If no or all sequences in current FASTA file have been already processed, this variable is None.
        # There is no way to count sequences in multi-FASTA file, accept of counting sequence IDs.
        # Therefore 'next_id_line' should be saved in memory after moment when packet is formed.
        try:
            next_id_line = pass_processed_seqs(fasta_file, num_done_reads, fmt_func)
        except UnboundLocalError:
            # This exception occurs when 'fasta_file' variable is not defined, i.e. when
            #   'fasta' is actual FASTA data, not path to file.
            # In this case we need all FASTA data.
            next_id_line = None
        # end try

        packet = ""

        line = get_next_line()
        if line.startswith('>') and ' ' in line:
            line = line.partition(' ')[0] # prune sequence ID
        # end if

        # If some sequences have been passed, this if-statement will be executed.
        # New packet should start with sequence ID line.
        if not next_id_line is None:
            packet += next_id_line+'\n'
        # end if
        packet += line+'\n' # add recently read line

        packs_at_all = reads_at_all // packet_size # Calculate total number of packets sent from current FASTA file
        if reads_at_all % packet_size > 0: # And this is ceiling (in order not to import 'math')
            packs_at_all += 1
        # end if
        packs_processed = int( num_done_reads / packet_size ) # number of successfully processed sequences
        packs_left = packs_at_all - packs_processed # number of packets left to send

        # Iterate over packets left to process
        for _ in range(packs_left):

            i = 0 # variable for counting sequenes within packet
            
            while i < packet_size:

                line = get_next_line()
                if line.startswith('>'):
                    if ' ' in line:
                        line = line.partition(' ')[0] # prune sequence ID
                    # end if
                    i += 1
                # end if
                
                if line == "": # if end of file (data) is reached
                    break
                # end if
                packet += line+'\n' # add line to packet
            # end while

            if line != "":
                next_id_line = packet.splitlines()[-1] # save sequence ID next packet will start with
                packet = '\n'.join(packet.splitlines()[:-1]) # exclude 'next_id_line' from packet
            else:
                next_id_line = None
            # end if

            # Get list of sequence IDs:
            names = list( filter(lambda l: True if l.startswith('>') else False, packet.splitlines()) )
            names = list( map(lambda l: l.partition(' ')[0].strip(), names) )

            # Just in case
            if packet is "":
                printl("Recent packet is empty")
                return
            # end if

            yield {"fasta": packet.strip(), "names": names}

            # Reset packet
            if not next_id_line is None:
                packet = next_id_line+'\n'
            else:
                return
            # end if
        # end for
    # end with
# end def fasta_packets


def remove_tmp_files(*paths):
    """
    Function removes files passed to it.
    Actually, passed arguments are paths ('str') to files meant to be removed.
    """

    for path in paths:
        if os.path.exists(path):
            os.unlink(path)
        # end if
    # end for
# end def remove_tmp_files


def configure_request(packet, blast_algorithm, organisms):
    """
    Function configures the request to BLAST server.

    :param packet: FASTA_data_containing_query_sequences;
    :type packet: str;
    :param blast_algorithm: BLASTn algorithm to use;
    :type blast_algorithm: str;
    :param organisms: list of strings performing 'nt' database slices;
    :type organisms: list<str>;

    Returns a dict of the following structure:
    {
        "payload": the_payload_of_the_request (dict),
        "headers": headers of thee request (dict)
    }
    """

    payload = dict()
    payload["CMD"] = "PUT" # method
    payload["PROGRAM"] = "blastn" # program
    payload["MEGABLAST"] = "on" if "megablast" in blast_algorithm.lower() else "" # if megablast
    payload["BLAST_PROGRAMS"] = blast_algorithm # blastn algoeithm
    payload["DATABASE"] = "nt" # db
    payload["QUERY"] = packet # FASTA data
    payload["HITLIST_SIZE"] = 1 # we need only the best hit

    # 'nt' database slices:
    for i, org in enumerate(organisms):
        payload["EQ_MENU{}".format(i if i > 0 else "")] = org
    # end for
    
    payload["NUM_ORG"] = str( len(organisms) )

    payload = urllib.parse.urlencode(payload)
    headers = { "Content-Type" : "application/x-www-form-urlencoded" }

    return {"payload":payload, "headers": headers}
# end def configure_request


def send_request(request, pack_to_send, packs_at_all, filename, tmp_fpath):
    """
    Function sends a request to "blast.ncbi.nlm.nih.gov/blast/Blast.cgi"
        and then waits for satisfaction of the request and retrieves response text.

    :param request: request_data (it is a dict that 'configure_request()' function returns);
    :param request: dict<dict>;
    :param pack_to_send: current number (like id) of packet meant to be sent now.
    :type pack_to_send: int;
    :param packs_at all: total number of packets corresponding to current FASTA file.
        This information is printed to console;
    :type packs_at_all: int;
    :param filename: basename of current FASTA file;
    :type filename: str;

    Returns XML text of type 'str' with BLAST response.
    """
    payload = request["payload"]
    headers = request["headers"]

    server = "blast.ncbi.nlm.nih.gov"
    url = "/blast/Blast.cgi"
    error = True

    # Save packet size
    with open(tmp_fpath, 'w') as tmp_file:
        tmp_file.write("packet_size: {}\n".format(packet_size))
    # end with

    while error:
        try:
            conn = http.client.HTTPSConnection(server) # create a connection
            conn.request("POST", url, payload, headers) # send the request
            response = conn.getresponse() # get the response
            response_text = str(response.read(), "utf-8") # get response text
        except OSError as oserr:
            printl(get_work_time() + "\n - Site 'https://blast.ncbi.nlm.nih.gov' is not available.")
            printl( repr(err) )
            printl("barapost will try to connect again in 30 seconds...\n")
            sleep(30)
        
        # if no exception occured
        else:
            error = False
        # end try
    # end while

    try:
        rid = re_search(r"RID = (.+)", response_text).group(1) # get Request ID
        rtoe = int(re_search(r"RTOE = ([0-9]+)", response_text).group(1)) # get time to wait provided by the NCBI server
    except AttributeError:
        printl(err_fmt("seems, ncbi has denied your request."))
        printl("Response is in file 'request_denial_response.html'")
        with open("request_denial_response.html", 'w') as den_file:
            den_file.write(response_text)
        # end with
        exit(1)
    finally:
        conn.close()
    # end try

    # Save temporary data
    with open(tmp_fpath, 'a') as tmpfile:
        tmpfile.write("sent_packet_num: {}\n".format(pack_to_send))
        tmpfile.write("Request_ID: {}".format(rid))
    # end with

    # /=== Wait for alignment results ===\

    return( wait_for_align(rid, rtoe, pack_to_send, packs_at_all, filename) )
# end def send_request


def wait_for_align(rid, rtoe, pack_to_send, packs_at_all, filename):
    """
    Function waits untill BLAST server accomplishes the request.
    
    :param rid: Request ID to wait for;
    :type rid: str;
    :param rtoe: time in seconds estimated by BLAST server needed to accomplish the request;
    :type rtoe: int;
    :param pack_to_send: current packet (id) number to send;
    :type pack_to_send: int;
    :param packs_at_all: total number of packets corresponding to current FASTA file.
        This information is printed to console;
    :type packs_at_all: int;
    :param filename: basename of current FASTA file;
    :type filename: str;

    Returns XML response ('str').
    """

    printl("\n{} - Requesting for alignment results: Request ID: {},\n '{}' ({}/{})".format(get_work_time(),
    rid, filename, pack_to_send, packs_at_all))
    # RTOE can be zero at the very beginning of continuation
    if rtoe > 0:
        printl("{} - BLAST server estimates that alignment will be accomplished in {} seconds ".format(get_work_time(), rtoe))
        printl("{} - Waiting for {}+3 (+3 extra) seconds...".format(get_work_time(), rtoe))
        # Server migth be wrong -- we will give it 3 extra seconds
        sleep(rtoe + 3)
        printl("{} - {} seconds have passed. Checking if alignment is accomplished...".format(get_work_time(), rtoe+3))
    # end if

    server = "blast.ncbi.nlm.nih.gov"
    wait_url = "/blast/Blast.cgi?CMD=Get&FORMAT_OBJECT=SearchInfo&RID=" + rid
    there_are_hits = False

    while True:
        error = True
        while error:
            try:
                conn = http.client.HTTPSConnection(server) # create connection
                conn.request("GET", wait_url) # ask for if there areresults
            except TimeoutError as err:
                printl("{} - Unable to connect to the NCBI server. Let's try to connect in 30 seconds.".format(get_work_time()))
                printl("   " + str(err))
                error = True
                sleep(30)
            except http.client.RemoteDisconnected as err:
                printl("{} - Unable to connect to the NCBI server. Let's try to connect in 30 seconds.".format(get_work_time()))
                printl("   " + str(err))
                error = True
                sleep(30)
            except socket.gaierror as err:
                printl("{} - Unable to connect to the NCBI server. Let's try to connect in 30 seconds.".format(get_work_time()))
                printl("   " + str(err))
                error = True
                sleep(30)
            except ConnectionResetError as err:
                printl("{} - Unable to connect to the NCBI server. Let's try to connect in 30 seconds.".format(get_work_time()))
                printl("   " + str(err))
                error = True
                sleep(30)
            except FileNotFoundError as err:
                printl("{} - Unable to connect to the NCBI server. Let's try to connect in 30 seconds.".format(get_work_time()))
                printl("   " + str(err))
                error = True
                sleep(30)
            except http.client.CannotSendRequest as err:
                printl("{} - Unable to connect to the NCBI server. Let's try to connect in 30 seconds.".format(get_work_time()))
                printl("   " + str(err))
                error = True
                sleep(30)
            else:
                error = False # if no exception ocured
            # end try
        # end while

        response = conn.getresponse() # get the resonse
        resp_content = str(response.read(), "utf-8") # get response text
        conn.close()

        # if server asks to wait
        if "Status=WAITING" in resp_content:
            println("\r{} - The request is still processing. Waiting for 60 seconds".format(get_work_time()))
            # indicate each 10 seconds with a dot
            for i in range(1, 7):
                sleep(10)
                printn("\r{} - The request is still processing. Waiting for 60 seconds{}".format(get_work_time(), '.'*i))
            # end for
            print() # go to next line
            continue
        # end if
        if "Status=FAILED" in resp_content:
            # if job failed
            printl('\n' + get_work_time() + " - Job failed\a\n")
            response_text = """{} - Job for query {} ({}/{}) with Request ID {} failed.
    Contact NCBI or try to start it again.\n""".format(get_work_time(), filename, pack_to_send, packs_at_all, rid)
            return response_text
        # end if
        # if job expired
        if "Status=UNKNOWN" in resp_content:
            printl('\n' + get_work_time() + " - Job expired\a\n")
            respond_text = """{} - Job for query {} ({}/{}) with Request ID {} expired.
    Try to start it again\n""".format(get_work_time(), filename, pack_to_send, packs_at_all, rid)
            return "expired"
        # end if
        # if results are ready
        if "Status=READY" in resp_content:
            there_are_hits = True
            printl("\n{} - Result for query '{}' ({}/{}) is ready!".format(get_work_time(), filename, pack_to_send, packs_at_all))
            # if there are hits
            if "ThereAreHits=yes" in resp_content:
                for i in range(45, 0, -5):
                    printl('-' * i)
                # end for
                print() # just print a blank line
                break
            # if there are no hits
            else:
                printl(get_work_time() + " - There are no hits. It happens.\n")
                break
            # end if
        # end if
        # Execution should not reach here
        printl('\n' + get_work_time() + " - Fatal error. Please contact the developer.\a\n")
        platf_depend_exit(1)
    # end while

    # Retrieve XML result
    retrieve_xml_url = "/Blast.cgi?CMD=Get&FORMAT_TYPE=XML&ALIGNMENTS=1&RID=" + rid
    conn = http.client.HTTPSConnection(server)
    conn.request("GET", retrieve_xml_url)
    response = conn.getresponse()

    respond_text = str(response.read(), "utf-8")
    conn.close()

    if "[blastsrv4.REAL]" in respond_text:
        printl("BLAST server error:\n  {}".format(re_search(r"(\[blastsrv4\.REAL\].*\))", respond_text).group(1)))
        printl("Let's try to prune these sequences.")
        printl("""All sequences in this packet will be halved
  and the packet will be resent to BLAST server.""")
        return None
    # end if

    # Retrieve human-readable text and put it into result directory
    if there_are_hits:
        save_txt_align_result(server, filename, pack_to_send, rid)
    # end if

    return respond_text
# end def wait_for_align


def halve_seqs(packet):
    """
    Function halves all sequences in packet, leaving 5'-half of the sequence.

    :param packet: FASTA data;
    :type packet: str;
    """

    lines = packet.splitlines()

    for i in range(1, len(lines), 2):
        seq = lines[i]
        lines[i] = seq[: len(seq)//2]
    # end for

    return '\n'.join(lines).strip()
# end def halve_seqs


def save_txt_align_result(server, filename, pack_to_send, rid):

    global outdir_path

    retrieve_text_url = "/Blast.cgi?CMD=Get&FORMAT_TYPE=Text&DESCRIPTIONS=1&ALIGNMENTS=1&RID=" + rid
    conn = http.client.HTTPSConnection(server)
    conn.request("GET", retrieve_text_url)
    response = conn.getresponse()

    txt_hpath = os.path.join(outdir_path, "blast_result_{}.txt".format(pack_to_send))
    # Write text result for a human to read
    with open(txt_hpath, 'w') as txt_file:
        txt_file.write(str(response.read(), "utf-8") + '\n')
    # end with
    conn.close()
# end def save_txt_align_result


def parse_align_results_xml(xml_text, seq_names):
    """
    Function parses BLAST xml response and returns tsv lines containing gathered information:
        1. Query name.
        2. Hit name formatted by 'format_taxonomy_name()' function.
        3. Hit accession.
        4. Length of query sequence.
        5. Length of alignment.
        6. Percent of identity.
        7. Percent of gaps.
        8. E-value.
        9. Average Phred33 quality of a read (if source file is FASTQ).
        10. Read accuracy (%) (if source file is FASTQ).

    Erroneous tsv lines that function may produce:
        1. "<query_name>\\tQuery has been lost: ERROR, Bad Gateway"
            if data packet has been lost.
            # end if
        2. "<query_name>\\tQuery has been lost: BLAST ERROR"
            if BLAST error occured.
            # end if
        3. "<query_name>\\tNo significant similarity found"
            if no significant similarity has been found
            # end if
        Type of return object: list<str>.
    """

    result_tsv_lines = list()

    # /=== Validation ===/

    if "Bad Gateway" in xml_text:
        printl('\n' + '=' * 45)
        printl(get_work_time() + " - ERROR! Bad Gateway! Data from last packet has lost.")
        printl("It would be better if you restart the script.")
        printl("Here are names of lost queries:")
        for i, name in enumerate(seq_names):
            printl("{}. '{}'".format(i+1, name))
            result_tsv_lines.append(name + DELIM + "Query has been lost: ERROR, Bad Gateway")
        # end for
        return result_tsv_lines
    # end if

    if "Status=FAILED" in xml_text:
        printl('\n' + get_work_time() + "BLAST ERROR!: request failed")
        printl("Here are names of lost queries:")
        for i, name in enumerate(seq_names):
            printl("{}. '{}'".format(i+1, name))
            result_tsv_lines.append(name + DELIM +"Query has been lost: BLAST ERROR")
        # end for
        return result_tsv_lines
    # end if

    if "to start it again" in xml_text:
        printl('\n' + get_work_time() + "BLAST ERROR!")

        printl("Here are names of lost queries:")
        for i, name in enumerate(seq_names):
            printl("{}. '{}'".format(i+1, name))
            result_tsv_lines.append(name + DELIM +"Query has been lost: BLAST ERROR")
        # end for
        return result_tsv_lines
    # end if

    # /=== Parse BLAST XML response ===/

    root = ElementTree.fromstring(xml_text) # get tree instance

    global new_acc_dict
    global qual_dict

    # Iterate through "Iteration" and "Iteration_hits" nodes
    for iter_elem, iter_hit in zip(root.iter("Iteration"), root.iter("Iteration_hits")):
        # "Iteration" node contains query name information
        query_name = intern(iter_elem.find("Iteration_query-def").text)
        query_len = iter_elem.find("Iteration_query-len").text

        if not qual_dict is None:
            ph33_qual = qual_dict[query_name]
            miscall_prop = round(10**(ph33_qual/-10), 3)
            accuracy = round( 100*(1 - miscall_prop), 2 ) # expected percent of correctly called bases
            qual_info_to_print = "    Average quality of this read is {}, i.e. accuracy is {}%;\n".format(ph33_qual,
                accuracy)
        else:
            # If FASTA file is processing, print dashed in quality columns
            ph33_qual = "-"
            accuracy = "-" # expected percent of correctly called bases
            qual_info_to_print = ""
        # end if

        # If there are any hits, node "Iteration_hits" contains at least one "Hit" child
        hit = iter_hit.find("Hit")
        if hit is not None:

            # Get full hit name (e.g. "Erwinia amylovora strain S59/5, complete genome")
            hit_name = hit.find("Hit_def").text
            # Format hit name (get rid of stuff after comma)
            hit_taxa_name = hit_name[: hit_name.find(',')] if ',' in hit_name else hit_name
            hit_taxa_name = hit_taxa_name.replace(" complete genome", "") # sometimes there are no comma before it
            hit_taxa_name = hit_taxa_name.replace(' ', '_')

            hit_acc = intern(hit.find("Hit_accession").text) # get hit accession
            gi_patt = r"gi\|([0-9]+)" # pattern for GI number finding
            hit_gi = re_search(gi_patt, hit.find("Hit_id").text).group(1)
            try:
                new_acc_dict[hit_acc][2] += 1
            except KeyError:
                new_acc_dict[hit_acc] = [hit_gi, hit_name, 1]
            # end try

            # Find the first HSP (we need only the first one)
            hsp = next(hit.find("Hit_hsps").iter("Hsp"))

            align_len = hsp.find("Hsp_align-len").text.strip()

            pident = hsp.find("Hsp_identity").text # get number of matched nucleotides

            gaps = hsp.find("Hsp_gaps").text # get number of gaps

            evalue = hsp.find("Hsp_evalue").text # get e-value

            pident_ratio = round( float(pident) / int(align_len) * 100, 2)
            gaps_ratio = round( float(gaps) / int(align_len) * 100, 2)

            printl("""\n '{}' -- '{}';
    Query length - {} nt;
    Identity - {}/{} ({}%); Gaps - {}/{} ({}%);""".format(query_name, hit_taxa_name,
                    query_len, pident, align_len, pident_ratio, gaps, align_len, gaps_ratio))

            # Append new tsv line containing recently collected information
            result_tsv_lines.append( DELIM.join( (query_name, hit_taxa_name, hit_acc, query_len,
                align_len, pident, gaps, evalue, str(ph33_qual), str(accuracy)) ))
        else:
            # If there is no hit for current sequence
            printl("\n '{}' -- No significant similarity found;\n    Query length - {};".format(query_name, query_len))
            result_tsv_lines.append(DELIM.join( (query_name, "No significant similarity found", "-", query_len,
                "-", "-", "-", "-", str(ph33_qual), str(accuracy)) ))
        # end if
        println(qual_info_to_print)
    # end for

    return result_tsv_lines
# end def parse_align_results_xml


def write_result(res_tsv_lines, tsv_res_path, acc_file_path, fasta_hname, outdir_path):
    """
    Function writes result of blasting to result tsv file.

    :param res_tsv_lines: tsv lines returned by 'parse_align_results_xml()' funciton;
    :type res_tsv_lines: list<str>;
    :param tsv_res_path: path to reslut tsv file;
    :type tsv_res_path: str;
    :param new_dpath: path to current result directory;
    :type new_dpath: str;
    """

    # If there is no result tsv file -- create it and write a head of the table.
    if not os.path.exists(tsv_res_path):
        with open(tsv_res_path, 'w') as tsv_res_file:
            tsv_res_file.write(DELIM.join( ["QUERY_ID", "HIT_NAME", "HIT_ACCESSION", "QUERY_LENGTH",
                "ALIGNMENET_LENGTH", "IDENTITY", "GAPS", "E-VALUE", "AVG_PHRED33", "ACCURACY(%)"] ) + '\n')
        # end with
    # end if
    
    # Write reslut tsv lines to this file
    with open(tsv_res_path, 'a') as tsv_res_file:
        for line in res_tsv_lines:
            tsv_res_file.write(line + '\n')
        # end for
    # end with

    # === Write accession information ===

    global acc_dict
    global new_acc_dict
    global blast_algorithm
    acc_file_path = os.path.join(outdir_path, "{}_probe_acc_list.tsv".format(blast_algorithm))

    with open(acc_file_path, 'w') as acc_file:
        acc_file.write("# Here are accessions, GI numbers and descriptions of Genbank records that can be used for sorting by 'barapost-v3.4a.py'\n")
        acc_file.write("# Values in this file are delimited by tabs.\n")
        acc_file.write("# You are welcome to edit this file by adding,\n")
        acc_file.write("#   removing or muting lines (with adding '#' symbol in it's beginning, just like this description).\n")
        acc_file.write("# Lines muted with '#' won't be noticed by 'barapost-v3.4a.py'.\n")
        acc_file.write("# You can specify your own FASTA files that you want to use as database for 'barapost-v3.4a.py'.\n")
        acc_file.write("# To do it, just write your FASTA file's path to this TSV file in new line.\n\n")
        acc_file.write(DELIM.join( ["ACCESSION", "GI_NUMBER", "RECORD_NAME", "OCCURRENCE_NUMBER"] ) + '\n')
    # end with

    for acc, other_info in new_acc_dict.items():
        try:
            acc_dict[acc][2] += other_info[2]
        
        except KeyError:
            acc_dict[acc] = other_info
        # end try
    # end for
    
    # Write accessions and record names
    with open(acc_file_path, 'a') as acc_file:
        for acc, other_info in sorted(acc_dict.items(), key=lambda x: -x[1][2]):
            acc_file.write(DELIM.join( (acc, other_info[0], other_info[1], str(other_info[2]))) + '\n')
        # end for
    # end with
    
    new_acc_dict.clear()
# end def write_result


def create_result_directory(fq_fa_path, outdir_path):
    """
    Function creates a result directory named according 
        to how source FASTQor FASTA file is named.

    :param fq_fa_path: path to source FASTQ or FASTA file;
    :type fq_fa_path: str;

    Returns 'str' path to the recently created result directory.
    """

    # dpath means "directory path"
    new_dpath = os.path.join(outdir_path, os.path.basename(fq_fa_path)) # get rid of absolute path
    new_dpath =re_search(r"(.*)\.(m)?f(ast)?(a|q)", new_dpath).group(1) # get rid of extention
    if not os.path.exists(new_dpath):
        try:
            os.makedirs(new_dpath)
        
        except OSError as oserr:
            printl(err_fmt("error while creating result directory"))
            printl( str(oserr) )
        # end try
    # end if

    return new_dpath
# end def create_result_directory


# =/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=
#                       |===== Proceed =====|


# /=== Comments to the kernel loop ===/

# 1. 'curr_fasta' is a dict of the following structure:
#    {
#        "fpath": path_to_FASTA_file (str),
#        "nreads": number_of_reads_in_this_FASTA_file (int)
#    }
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. 'previous_data' is a dict of the following structure:
#    {
#        "pack_size": packet_size (int),
#        "sv_npck": saved_number_of_sent_packet (int),
#        "RID": saved_RID (str),
#        "tsv_respath": path_to_tsv_file_from_previous_run (str),
#        "n_done_reads": number_of_successfull_requests_from_currenrt_FASTA_file (int),
#        "tmp_fpath": path_to_pemporary_file (str)
#        "acc_fparh": path_to_accessoion_file (str)
#    }
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3. 'packet' is a dict of the following structure:
#    {
#        "fasta": FASTA_data_containing_query_sequences (str),
#        "names": list_of_sequence_ids_from_FASTA_file (list<str>)
#    }
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 4. 'response' is a dict of the following structure:
#    {
#        "RID": Request ID (str),
#        "RTOE", time_to_wait_provided_by_the_NCBI_server (int)
#    }

#                   |===== Kernel loop =====|

print("Checking Internet connection...")
check_connection()
print("OK\n\n")


printl(" - Probing batch size: {} sequences;".format(probing_batch_size))
printl(" - Packet size: {} sequences;".format(packet_size))
printl(" - BLAST algorithm: {};".format(blast_algorithm))
printl(" - Database: nt;")
if len(organisms) > 0:
    for db_slice in organisms:
        printl("   {};".format(db_slice))
    # end for
# end if

printl()

printl(" Following files will be processed:")
for i, path in enumerate(fq_fa_list):
    printl("    {}. '{}'".format(i+1, path))
# end for

printl('-'*30 + '\n')

# Variable for counting accessions of records menat to be downloaded from Genbank.
# Is used only for printing the list of accessions to console.
acc_counter = 0
# Dictionary of accessions and record names.
# Accessions are keys, record names are values.
# This dictionary is filled while processing and at the beginning of continuation.
acc_dict = dict()
# Dictionary of accessions and record names encountered while sending of the current packet.
# Accessions are keys, record names are values.
new_acc_dict = dict()

# Counter of processed sequences
seqs_processed = 0

# Variable that contains id of next sequence in current FASTA file.
# If no or all sequences in current FASTA file have been already processed, this variable is None
# Function 'get_packet' changes this variable
next_id_line = None

# Varible for stopping execution when probing batch is processed completely.
stop = False

# Files that were processed completely will be omited.
# Function 'look_around' changes value of this variable.
omit_file= False


# Iterate through found source FASTQ and FASTA files
for i, fq_fa_path in enumerate(fq_fa_list):

    # Configure quality dictionary
    qual_dict = configure_qual_dict(fq_fa_path) if is_fastq(fq_fa_path) else None
    
    # Create the result directory with the name of FASTQ of FASTA file being processed:
    new_dpath = create_result_directory(fq_fa_path, outdir_path)

    # Convert FASTQ file to FASTA (if it is FASTQ) and get it's path and number of sequences in it:
    curr_fasta = fastq2fasta(fq_fa_path, i, new_dpath)

    # "hname" means human readable name (i.e. without file path and extention)
    fasta_hname = os.path.basename(curr_fasta["fpath"]) # get rid of absolure path
    fasta_hname = re_search(r"(.*)\.(m)?f(ast)?a", fasta_hname).group(1) # get rid of file extention

    # Look around and ckeck if there are results of previous runs of this script
    # If 'look_around' is None -- there is no data from previous run
    previous_data = look_around(outdir_path, new_dpath, curr_fasta["fpath"],
        blast_algorithm)

    if previous_data is None: # If there is no data from previous run
        num_done_reads = 0 # number of successfully processed sequences
        saved_npack = None # number of last sent packet (there is no such stuff for de novo run)
        tsv_res_path = "{}_{}_result.tsv".format(os.path.join(new_dpath,
            fasta_hname), blast_algorithm) # form result tsv file path
        tmp_fpath = "{}_{}_temp.txt".format(os.path.join(new_dpath,
            fasta_hname), blast_algorithm) # form temporary file path
        acc_fpath = os.path.join(outdir_path, "{}_probe_acc_list.tsv".format(blast_algorithm)) # form path to accession file
    else: # if there is data from previous run
        num_done_reads = previous_data["n_done_reads"] # get number of successfully processed sequences
        saved_npack = previous_data["sv_npck"] # get number of last sent packet
        packet_size = previous_data["pack_size"] # packet size sholud be the same as it was in previous run
        tsv_res_path = previous_data["tsv_respath"] # result tsv file sholud be the same as during previous run
        tmp_fpath = previous_data["tmp_fpath"] # temporary file sholud be the same as during previous run
        acc_fpath = previous_data["acc_fpath"] # accession file sholud be the same as during previous run
        saved_RID = previous_data["RID"] # having this RID we can try to get response for last request
        contin_rtoe = 0 # we will not sleep at the very beginning of continuation
    # end if

    # Omit completely processed files.
    if omit_file:
        omit_file = False
        continue
    # end if

    if num_done_reads != 0:
        seqs_processed = num_done_reads
    # end if

    if (probing_batch_size - seqs_processed) <= curr_fasta["nreads"]:
        tmp_num = (probing_batch_size - seqs_processed)
    else:
        tmp_num = curr_fasta["nreads"]
    # end if
    packs_at_all = tmp_num // packet_size # Calculate total number of packets sent from current FASTA file

    if tmp_num % packet_size > 0: # And this is ceiling (in order not to import 'math')
        packs_at_all += 1
    # end if
    packs_received = int( num_done_reads / packet_size ) # number of successfully processed sequences

    if is_gzipped(curr_fasta["fpath"]):
        fmt_func = lambda l: l.decode("utf-8")
        how_to_open = open_as_gzip
    
    else:
        fmt_func = lambda l: l
        how_to_open = open
    # end if

    reads_left = curr_fasta["nreads"] - num_done_reads # number of sequences left to precess
    packs_left = packs_at_all - packs_received # number of packets left to send
    pack_to_send = packs_received+1 if packs_received > 0 else 1 # number of packet meant to be sent now

    # Iterate over packets left to send
    for packet in fasta_packets(curr_fasta["fpath"], packet_size, curr_fasta["nreads"], num_done_reads):

        # Just in case:
        if packet["fasta"] is "":
            printl("Recent packet is empty")
            break
        # end if

        printl("\nGo to BLAST (" + blast_algorithm + ")!")
        printl("Request number {} out of {}.".format(pack_to_send, packs_at_all))

        send = True

        # If current packet has been already send, we can try to get it and not to send it again
        if pack_to_send == saved_npack and saved_RID is not None:

            align_xml_text = wait_for_align(saved_RID, contin_rtoe,
                pack_to_send, packs_at_all, fasta_hname+".fasta") # get BLAST XML response

            # If request is not expired get he result and not send it again
            if align_xml_text != "expired":
                send = False

                result_tsv_lines = parse_align_results_xml(align_xml_text,
                    packet["names"]) # get result tsv lines

                seqs_processed += len( packet["names"] )

                # Write the result to tsv
                write_result(result_tsv_lines, tsv_res_path, acc_fpath, fasta_hname, outdir_path)
            # end if
        # end if

        if send:

            align_xml_text = None
            while align_xml_text is None: # untill successfull attempt

                request = configure_request(packet["fasta"], blast_algorithm, organisms) # get the request

                # Send the request get BLAST XML response
                # 'align_xml_text' will be None if NCBI BLAST server rejects the request due to too large amount of data in it.
                align_xml_text = send_request(request,
                    pack_to_send, packs_at_all, fasta_hname+".fasta", tmp_fpath)

                # If NCBI BLAST server rejects the request due to too large amount of data in it --
                #    shorten all sequences in packet twice and resend it.
                if align_xml_text is None:
                    packet["fasta"] = halve_seqs(packet["fasta"])
                # end if
            # end while

            # Get result tsv lines
            result_tsv_lines = parse_align_results_xml(align_xml_text,
                packet["names"])

            seqs_processed += len( packet["names"] )

            # Write the result to tsv
            write_result(result_tsv_lines, tsv_res_path, acc_fpath, fasta_hname, outdir_path)
        # end if
        pack_to_send += 1

        if seqs_processed >= probing_batch_size:
            remove_tmp_files(tmp_fpath)
            stop = True
            break
        # end if
    # end for
    remove_tmp_files(tmp_fpath)
    if stop:
        break
    # end if
# end for

printl("\n {} sequences have been processed\n".format(seqs_processed))

printl("Here are Genbank records that can be used for further sorting by 'barapost-v3.4a.py'.")
printl("They are sorted by their occurence in probing batch:")

# Print accessions and record names sorted by occurence
# "-x[1][2]:": minus because we need descending order, [1] -- get tuple of "other information",
#   [2] -- get 3-rd element (occurence)
for acc, other_info in sorted(acc_dict.items(), key=lambda x: -x[1][2]):
    s_letter = "s" if other_info[2] > 1 else ""
    printl(" {} sequence{} - {}, '{}'".format(other_info[2], s_letter, acc, other_info[1]))
# end for

# Print number of unkmown sequences, if there are any:
unkn_num = probing_batch_size - sum( map(lambda x: x[2], acc_dict.values()) )
if unkn_num > 0:
    s_letter = "s" if unkn_num > 1 else ""
    printl(" {} sequence{} - No significant similarity found".format(unkn_num, s_letter))
# end if

printl("""\nThey are saved in following file:
    '{}'""".format(acc_fpath))
printl("""\nYou can edit this file before running 'barapost-v3.4a.py' in order to
  modify list of sequences that will be downloaded from Genbank
  and used as local (i.e. on your local computer) database by 'barapost-v3.4a.py'.""")
end_time = time()
printl('\n'+get_work_time() + " ({}) ".format(strftime("%d.%m.%Y %H:%M:%S", localtime(end_time))) + "- Probing task is completed\n")
logfile.close()
platf_depend_exit(0)