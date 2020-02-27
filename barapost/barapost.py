#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "3.11.e"
# Year, month, day
__last_update_date__ = "2020-02-28"

# |===== Check python interpreter version =====|

import sys

if sys.version_info.major < 3:
    print( "\nYour python interpreter version is " + "%d.%d" % (sys.version_info.major,
        sys.version_info.minor) )
    print("   Please, use Python 3.\a")
    # In python 2 'raw_input' does the same thing as 'input' in python 3.
    # Neither does 'input' in python2.
    if sys.platform.startswith("win"):
        raw_input("Press ENTER to exit:")
    # end if
    sys.exit(1)
# end if

from src.platform import platf_depend_exit

# Firstly search for information-providing options (-h and -v):

if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
    print("\n  barapost.py\n  Version {}; {} edition;\n".format(__version__, __last_update_date__))
    print("DESCRIPTION:\n")
    print("""This script is designed for taxonomic classification of nucleotide sequences by finding
  the most similar sequence in a nucleotide database stored on local machine.\n""")

    if "--help" in sys.argv[1:]:
        print(""""barapost.py" downloads records "discovered" by "prober.py" (and all replicons
  related to them: other chromosomes, plasmids) from Genbank according to file (`hits_to_download.tsv`)
  generated by "prober.py" and creates a database on local machine. After that "baraposst.py" classifies
  the rest of data with "BLAST+" toolkit.\n""")
        print("Script processes FASTQ and FASTA (as well as '.fastq.gz' and '.fasta.gz') files.\n")
        print("""If you have your own FASTA files that can be used as database alone to blast against,
  you can omit "prober.py" step and go to "barapost.py" (see `-l` option).""")
        print("----------------------------------------------------------\n")
        print("Default parameters:\n")
        print("- if no input files are specified, all FASTQ and FASTA files in current directory will be processed;")
        print("- packet size (see '-p' option): 100 sequences;")
        print("- algorithm (see '-a' option): 0 (megaBlast);")
        print("- numbers of threads to launch ('-t' option): 1 thread.")
        print("----------------------------------------------------------\n")
    # end if

    print("""Files that you want 'barapost.py' to process should be specified as
  positional arguments (see EXAMPLE #2 running detailed (--help) help message).""")
    print("----------------------------------------------------------\n")
    print("OPTIONS:\n")
    print("""-h (--help) --- show help message.
   '-h' -- brief, '--help' -- full;\n""")
    print("-v (--version) --- show version;\n")
    print("""-r (--taxannot-resdir) --- result directory generated by script 'prober.py'
   This is directory specified to 'prober.py' by '-o' option.
   If you omit 'prober.py' and use your own FASTA files
   to create a database, this directory may not exist before start of 'barapost.py'
   (i.e. it will be a simple output directory).
   Default value is "barapost_result".\n""")
    print("""-d (--indir) --- directory which contains FASTQ of FASTA files meant to be processed.
   I.e. all FASTQ and FASTA files in this direcory will be processed;\n""")
    print("""-p (--packet-size) --- size of the packet, i.e. number of sequence to align in one blastn launching.
   Value: positive integer number. Default value is 100;\n""")
    print("""-a (--algorithm) --- BLASTn algorithm to use for aligning.
   Available values: 0 for megaBlast, 1 for discoMegablast, 2 for blastn.
   Default is 0 (megaBlast);\n""")
    print("""-l (--local-fasta-to-db) --- your own FASTA file that will be included in
   downloaded database, which "barapost.py" creates;\n""")
    print("-t (--threads) --- number of CPU threads to use;")

    if "--help" in sys.argv[1:]:
        print("----------------------------------------------------------\n")
        print("EXAMPLES:\n")
        print("""1. Process all FASTA and FASTQ files in working directory with default settings:\n
   barapost.py\n""")
        print("""2. Process all files starting with "some_fasta" in the working directory with default settings:\n
   barapost.py some_fasta*\n""")
        print("""3. Process one FASTQ file with default settings.
   Directory that contains taxonomic annotation is named 'prober_outdir':\n
   barapost.py reads.fastq -r prober_outdir\n""")
        print("""4. Process FASTQ file and FASTA file with discoMegablast, packet size of 50 sequences.
   Directory that contains taxonomic annotation is named 'prober_outdir':\n
   barapost.py reads.fastq.gz another_sequences.fasta -a discoMegablast -p 50 -r prober_outdir\n""")
        print("""5. Process all FASTQ and FASTA files in directory named 'some_dir'.
   Directory that contains taxonomic annotation is named 'prober_outdir':\n
   barapost.py -d some_dir -r prober_outdir\n""")
        print("""6. Process file named 'some_reads.fastq'.
   Directory that contains taxonomic annotation is named 'prober_outdir'.
   Sequence from file 'my_own_sequence.fasta' will be included to the database.
   Launch 4 threads:\n
   barapost.py some_reads.fastq -l my_own_sequence.fasta -t 4 -r prober_outdir""")
     # end if
    platf_depend_exit(0)
# end if

if "-v" in sys.argv[1:] or "--version" in sys.argv[1:]:
    print(__version__)
    platf_depend_exit(0)
# end if


import os
from glob import glob
from re import search as re_search
from src.printlog import getwt, get_full_time, printn, printl, println, err_fmt

import getopt

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hvd:p:a:r:l:t:",
        ["help", "version", "indir=", "packet-size=", "algorithm=", "taxannot-resdir=",
        "local-fasta-to-bd=", "threads="])
except getopt.GetoptError as gerr:
    print( str(gerr) )
    platf_depend_exit(2)
# end try

is_fq_or_fa = lambda f: True if not re_search(r".*\.(m)?f(ast)?(a|q)(\.gz)?$", f) is None else False

# Default values:
fq_fa_list = list() # list of paths to file meant to be processed
indir_path = None # path to '-d' directory
packet_size = 100
blast_algorithm = "megaBlast"
tax_annot_res_dir = "barapost_result" # directory with taxonomic annotation results
your_own_fasta_lst = list() # list os user's fasta files to be included in database
n_thr = 1 # number of threads

# Add positional arguments to fq_fa_list
for arg in args:
    if not is_fq_or_fa(arg):
        print(err_fmt("invalid positional argument: '{}'".format(arg)))
        print("Only FAST(A/Q) files can be specified without an option in command line.")
        platf_depend_exit(1)
    # end if
    if not os.path.exists(arg):
        print(err_fmt("File '{}' does not exist!".format(arg)))
        platf_depend_exit(1)
    # end if
    fq_fa_list.append( os.path.abspath(arg) )
# end for

for opt, arg in opts:

    if opt in ("-r", "--taxannot-resdir"):
        tax_annot_res_dir = os.path.abspath(arg)

    elif opt in ("-t", "--threads"):
        try:
            n_thr = int(arg)
            if n_thr < 1:
                raise ValueError
            # end if
        except ValueError:
            print(err_fmt("number of threads must be positive integer number!"))
            print(" And here is your value: '{}'".format(arg))
            sys.exit(1)
        # end try
        if n_thr > len(os.sched_getaffinity(0)):
            print("""\nWarning! You have specified {} threads to use
  although {} are available.""".format(n_thr, mp.cpu_count()))
            error = True
            while error:
                reply = input("""\nPress ENTER to switch to {} threads,
  or enter 'c' to continue with {} threads,
  or enter 'q' to exit:>>""".format(mp.cpu_count(), n_thr))
                if reply in ("", 'c', 'q'):
                    error = False
                    if reply == "":
                        n_thr = mp.cpu_count()
                        print("\nNumber of threads switched to {}\n".format(n_thr))
                    elif reply == 'c':
                        pass
                    elif reply == 'q':
                        sys.exit(0)
                    # end if
                else:
                    print("\nInvalid reply!\n")
                # end if
            # end while
        # end if

    elif opt in ("-d", "--indir"):
        if not os.path.isdir(arg):
            print(err_fmt("directory '{}' does not exist!".format(arg)))
            platf_depend_exit(1)
        # end if
        
        indir_path = os.path.abspath(arg)

        # Add all fastq and fasta files from '-d' directory to fq_fa_list
        fq_fa_list.extend(list( filter(is_fq_or_fa, glob("{}{}*".format(indir_path, os.sep))) ))

    elif opt in ("-p", "--packet-size"):
        try:
            packet_size = int(arg)
            if packet_size <= 0:
                raise ValueError
            # end if
        except ValueError:
            print(err_fmt("packet_size (-p option) must be positive integer number"))
            platf_depend_exit(1)
        # end try

    elif opt in ("-l", "--local-fasta-to-bd"):

        if not os.path.exists(arg):
            print(err_fmt("file '{}' does not exist!".format(arg)))
            platf_depend_exit(1)
        # end if

        your_own_fasta_lst.append(os.path.abspath(arg))

    elif opt in ("-a", "--algorithm"):
        if not arg in ("0", "1", "2"):
            print(err_fmt("invalid value specified by '-a' option!"))
            print("Available values: 0 for megaBlast, 1 for discoMegablast, 2 for blastn")
            print("Your value: '{}'".format(arg))
            platf_depend_exit(1)
        # end if
        blast_algorithm = ("megaBlast", "discoMegablast", "blastn")[int(arg)]
    # end if
# end for


# If no FASTQ or FASTA file have been found
if len(fq_fa_list) == 0:
    # If input directory was specified -- exit
    if not indir_path is None:
        print(err_fmt("""no input FASTQ or FASTA files specified
  or there is no FASTQ and FASTA files in the input directory.\n"""))
        platf_depend_exit(1)
    
    # If input directory was not specified -- look for FASTQ files in working directory
    else:
        fq_fa_list = list(filter( is_fq_or_fa, glob("{}{}*".format(os.getcwd(), os.sep)) ))

        # If there are nothing to process -- just show help message
        if len(fq_fa_list) == 0:
            print("\nbarapost.py (Version {})\n".format(__version__))
            print("Usage:")
            print("  barapost.py one.fastq.gz another.fasta -r tax_annotation_dir [...] [OPTIONS]")
            print("For more detailed description, run:")
            print("  barapost.py -h\n")
            platf_depend_exit(0)
        else:
            # Ask if a user wants to proceed or he/she ran it occasionally and wants just help message
            print("\n {} fasta and/or fastq files are found in working directory.\n".format(len(fq_fa_list)))
            error = True
            while error:
                reply = input("""Press ENTER to process them
  or enter 'h' to just see help message:>> """)
                if reply == "":
                    error = False
                    pass
                elif reply == 'h':
                    error = False
                    print('\n' + '-'*15)
                    print("  barapost.py (Version {})\n".format(__version__))
                    print("Usage:")
                    print("  barapost.py one.fastq.gz another.fasta -r tax_annotation_dir [...] [OPTIONS]")
                    print("For more detailed description, run:")
                    print("  barapost.py -h\n")
                    platf_depend_exit(0)
                else:
                    print("Invalid reply: {}\n".format(reply))
                # end if
            # end while
        # end if
    # end if
# end if

# Sort list of files that will be processed -- process them in alphabetical order.
fq_fa_list.sort()


# |== Check if 'blast+' tookit is installed ==|

pathdirs = os.environ["PATH"].split(os.pathsep)

# Add '.exe' extention in order to find executables on Windows
if sys.platform.startswith("win"):
    exe_ext = ".exe"
else:
    exe_ext = ""
# end if

for utility in ("blastn"+exe_ext, "makeblastdb"+exe_ext, "makembindex"+exe_ext):

    utility_found = False

    for directory in pathdirs:
        if os.path.exists(directory) and utility in os.listdir(directory):
            utility_found = True
            break
        # end if
    # end for

    if not utility_found:
        print("  Attention!\n'{}' from BLAST+ toolkit is not installed.".format(utility))
        print("""If this error still occures although you have installed everything 
-- make sure that this program is added to PATH)""")
        platf_depend_exit(1)
    # end if
# end for

acc_fpath = os.path.join(tax_annot_res_dir, "hits_to_download.tsv")
acc_file_exists = os.path.exists(acc_fpath)

db_exists = os.path.exists( os.path.join(tax_annot_res_dir, "local_database") )
if db_exists:
    db_exists = db_exists and len(os.listdir(os.path.join(tax_annot_res_dir, "local_database"))) != 0
# end if

# Create result directory, if it does not exist
if not os.path.exists(tax_annot_res_dir):
    try:
        os.makedirs(tax_annot_res_dir)
    except OSError as oserr:
        print(err_fmt("unable to create result directory"))
        print( str(oserr) )
        print("Prober just tried to create directory '{}' and crushed.".format(tax_annot_res_dir))
        platf_depend_exit(1)
    # end try
# end if

# Check if there is a way to create a databse (or to use old one):
if not acc_file_exists and not db_exists and len(your_own_fasta_lst) == 0:

    print(err_fmt("no way to create a database:"))
    print("1. Database in directory '{}' does not exist.".format(os.path.join(tax_annot_res_dir,
        "local_databse")))
    print("2. File '{}' does not exist.".format(acc_fpath))
    print("3. No fasta file is provided by '-l' option.")
    if tax_annot_res_dir == "barapost_result":
        print("""\nMaybe, the reason is that output directory generated by 'prober.py'
  isn't named 'barapost_result' and you have forgotten to specify it with '-r' option.""")
    # end if
    platf_depend_exit(1)
# end if
del db_exists, acc_file_exists

# Generate path to log file:
from src.platform import get_logfile_path

logfile_path = get_logfile_path("barapost", tax_annot_res_dir)
printl(logfile_path, "\n |=== barapost.py (version {}) ===|\n".format(__version__))
printl(logfile_path,  get_full_time() + "- Start working\n")


# Form paths to auxiliary files:
indsxml_path = os.path.join(tax_annot_res_dir, "indsxml.gbc.xml")
taxonomy_dir = os.path.join(tax_annot_res_dir, "taxonomy")
if not os.path.isdir(taxonomy_dir):
    os.makedirs(taxonomy_dir)
# end if
taxonomy_path = os.path.join(taxonomy_dir, "taxonomy")


#                       |===== Proceed =====|

printl(logfile_path, " - Logging to '{}'".format(logfile_path))
printl(logfile_path, " - Output directory: '{}';".format(tax_annot_res_dir))
printl(logfile_path, " - Packet size: {} sequences;".format(packet_size))
printl(logfile_path, " - BLAST algorithm: {};".format(blast_algorithm))
printl(logfile_path, " - Threads: {};\n".format(n_thr))

s_letter = '' if len(fq_fa_list) == 1 else 's'
printl(logfile_path, " {} file{} will be processed.".format( len(fq_fa_list), s_letter))
with open(logfile_path, 'a') as logfile: # write paths to all input files to log file
    logfile.write("Here they are:\n")
    for i, path in enumerate(fq_fa_list):
        logfile.write("    {}. '{}'\n".format(i+1, path))
    # end for
# end with

if not len(your_own_fasta_lst) == 0:
    preposition = " besides downloaded ones" if not acc_fpath is None else ""
    printl(logfile_path, "\n Following FASTA files will be included in database{}:".format(preposition))
    for i, path in enumerate(your_own_fasta_lst):
        printl(logfile_path, "   {}. '{}'".format(i+1, path))
    # end for
# end if

printl(logfile_path, '-'*30)

# Algorithms in 'blast+' are named in a little different way comparing to BLAST server.
# In order to provide full interface compatibility with 'prober.py' we will merely change values here.
if blast_algorithm == "megaBlast":
    blast_algorithm = "megablast"
elif blast_algorithm == "discoMegablast":
    blast_algorithm = "dc-megablast"
# end if

# Indexed discontiguous searches are not supported:
#    https://www.ncbi.nlm.nih.gov/books/NBK279668/#usermanual.Megablast_indexed_searches
if blast_algorithm != "dc-megablast" and len(glob(os.path.join(tax_annot_res_dir, "local_database", "*idx"))) != 0:
    use_index = "true"
else:
    use_index = "false"
# end if

from src.barapost_modules.barapost_spec import configure_acc_dict

# It is a dictionary of accessions and record names.
# Accessions are keys, tuples of GI numbers and record names are values.
acc_dict = configure_acc_dict(acc_fpath, your_own_fasta_lst, logfile_path)

from src.barapost_modules.build_local_db import build_local_db

# Build a database
local_fasta = build_local_db(acc_dict,
    tax_annot_res_dir,
    acc_fpath,
    your_own_fasta_lst,
    logfile_path)

if not os.path.exists(local_fasta):
    local_fasta = os.path.join(tax_annot_res_dir, "local_database", "local_seq_set.fasta")
else:
    print(err_fmt("database menaging error"))
    platf_depend_exit(1)
# end if

# Create temporary directory for query files:
queries_tmp_dir = os.path.join(tax_annot_res_dir, "queries-tmp")
if not os.path.isdir(queries_tmp_dir):
    try:
        os.makedirs(queries_tmp_dir)
    except OSError as oserr:
        printl(logfile_path, err_fmt("unable to create directory for queries:"))
        printl(logfile_path, "  '{}'".format(queries_tmp_dir))
        printl(logfile_path, "Reason: {}".format(str(oserr) ))
        platf_depend_exit(1)
    # end try
# end if


# Proceeding.
# The main goal of multiprocessing is to isolate processes from one another.
# 
# Two situations are available:
#   1. Number of threads <= number of files meant to be processed ('many_files'-parallel mode):
#      Files will be distribured equally among processes.
#      Processes interact with one another only while printing things to the console
#      for user's entertainment.
#   2. Number of threads > number of files meant to be processed ('few_files'-parallel mode):
#      Files will be processed one by one. They will be divided into equal blocks,
#      and these blocks will be distributed among processes.
#      Processes interact with one another while writing to result file and
#      while printing things to the console.

printl(logfile_path, "{} - Starting classification.".format(getwt()))
printn("  Working...")

if n_thr <= len(fq_fa_list):
    if n_thr != 1:

        # Proceed 'many_files'-parallel processing

        from src.barapost_modules.parallel_mult_files import process

        process(fq_fa_list,
            n_thr,
            packet_size,
            tax_annot_res_dir,
            blast_algorithm,
            use_index,
            logfile_path)

    else:

        # Proceed single-thread processing

        from src.barapost_modules.single_thread_mult_files import process

        process(fq_fa_list,
            packet_size,
            tax_annot_res_dir,
            blast_algorithm,
            use_index,
            logfile_path)
    # end if
else:

    # Proceed 'few_files'-parallel processing

    from src.barapost_modules.parallel_single_file import process

    for fq_fa_path in fq_fa_list:
        process(fq_fa_path,
            n_thr,
            packet_size,
            tax_annot_res_dir,
            blast_algorithm,
            use_index,
            logfile_path)
    # end for
# end if
printl(logfile_path, '\r' + " " * len("  Working..."))

# Remove everything in 'queries_tmp_dir'
try:
    for qpath in glob( os.path.join(queries_tmp_dir, '*') ):
        os.unlink(qpath)
    # end for
    os.rmdir(queries_tmp_dir)
except OSError as oserr:
    printl(logfile_path, err_fmt("unable to delete directory '{}'".format(queries_tmp_dir)))
    printl(logfile_path,  str(oserr) )
    printl(logfile_path, "Don't worry -- barapost has completed it's job just fine,")
    printl(logfile_path, "   the only thing that some temporary files are left in the directory mentioned above.\n")
# end try

printl(logfile_path, get_full_time() + "- Task is completed!\n")
platf_depend_exit(0)