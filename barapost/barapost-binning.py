#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "4.9.a"
# Year, month, day
__last_update_date__ = "2021-11-19"

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
    print("\n  barapost-binning.py\n  Version {}; {} edition;\n".format(__version__, __last_update_date__))
    print("DESCRIPTION:\n")
    print("""barapost-binning.py -- this script is designed for binning (dividing into separate files)
    FASTQ and FASTA files processed by `barapost-local.py`.""")
    print("""Moreover, it can bin FAST5 files according to taxonomical annotation of basecallsed
  FASTQ files. For details, see README.md on github page
  (`FAST5 binning` section): https://github.com/masikol/barapost\n""")
    if "--help" in sys.argv[1:]:
        print("----------------------------------------------------------\n")
        print("""Default parameters:\n
 - if no input files are specified, all FASTQ, FASTA and FAST5 files in current directory will be processed;
 - binning sensitivity (see `-s` option): 5 (genus);
 - output directory (`-o` option): directory named `binning_result_<date_and_time_of_run>`
   nested in working directory;
 - minimum mean quality of a read to keep (`-q` option): 10;
 - filtering by length (`-m` option) is disabled;
 - filtering by alignment identity (`-i` option) is disabled;
 - filtering by alignment coverage (`-c` option) is disabled;
 - "FAST5 untwisting" is disaled (see `-u` option);
 - number of CPU threads to use (`-t` option): 1;
 - barapost-binning generated trash file(s) (`-n` flag);""")
# end if

    print("----------------------------------------------------------\n")
    print("""Files that you want `barapost-binning.py` to process should be
    specified as positional arguments (see Examples running detailed (--help) help message).\n""")
    print("OPTIONS:\n")
    print("""-h (--help) --- show help message.
   `-h` -- brief, `--help` -- full;\n""")
    print("-v (--version) --- show version;\n")
    print("""-r (--annot-resdir) --- result directory generated by script `barapost-prober.py`
   This is directory specified to `barapost-prober.py` with `-o` option
   and to `barapost-local.py` with `-r` option.
   Default value is "barapost_result".\n""")
    print("""-d (--indir) --- directory which contains FAST(Q/A/5) files
   meant to be binned. I.e. all FASTQ, FASTA and FAST5 files in this direcory will be processed;\n""")
    print("-o (--outdir) --- output directory;\n")
    print("""-s (--binning-sensitivity) --- binning sensitivity,
   i.e. the lowest taxonomy rank that barapost-binning regards;
   Available values:
     0 for domain, 1 for phylum, 2 for class,
     3 for order, 4 for family, 5 for genus,
     6 for species.
   Default is 5 (genus);\n""")
    print("""-u (--untwist-fast5) --- flag option. If specified, FAST5 files will be
   binned considering that corresponding FASTQ files may contain reads from other FAST5 files
   and reads from a particular FAST5 file may be ditributed among multiple FASTQ files.
   Feature is disabled by default;\n""")
    print("""-t (--threads) --- number of CPU threads to use.
   Affects only FASTA and FASTQ binning.
   barapost-binning processes FAST5 files in 1 thread anyway (exception is "FAST5 untwisting").\n""")
    print("  Filter options:\n")
    print(" Quality and length filters:\n")
    print("""-q (--min-qual) --- threshold for quality filter;
   Reads of lower quality will be written to separate "trash" file;
   Default value: 10;\n""")
    print("""-m (--min-seq-len) ---threshold for query length filter.
   Shorter sequences will be written to separate "trash" file.
   This filter is disabled by default;\n""")
    print(" Alignment significance filters:\n")
    print("""-i (--min-pident) --- threshold (in percents) for alignment identity filter.
   Sequences, which align to best hit with lower identity will be
     written to separate "align_trash" file.
   This filter is disabled by default;\n""")
    print("""-c (--min-coverage) --- threshold (in percents) for alignment coverage filter.
   Sequences, which align to best hit with lower coverage will be
     written to separate "align_trash" file.
   This filter is disabled by default;\n""")
    print("""-n (--no-trash) --- flag option. If specified:
   1) trash files will not be outputed;
   2) sequences, which does not pass filters, won't be written anywhere;\n""")

    if "--help" in sys.argv[1:]:
        print("----------------------------------------------------------\n")
        print("EXAMPLES:\n")
        print("""  1. Process all FASTA and FASTQ files in working directory with default settings:\n
  barapost-binning.py\n""")
        print("""  2. Process all files starting with "some_fasta" in the working directory with default settings.
  Move reads with mean quality < Q15 to "trash" file.
  Move sequences with shorter than 3000 b.p. to "trash" file.
  Move sequences, which align to best hit with identity or coverage lower than 90% to "trash" file.\n
  barapost-binning.py some_my_fastq* -q 15 -m 3000 -i 90 -c 90\n""")
        print("""  3. Process one FASTQ file with default settings.
  File 'reads.fastq' has been already classified and
   results of classification are in directory 'prober_outdir':\n
  barapost-binning.py reads.fastq.gz -r prober_outdir/\n""")
        print("""  4. Process a FASTQ file and a FASTA file, place results in 'outdir' directory.
  Files 'reads.fastq.gz' and 'another_sequences.fasta' have been already classified and
   results of classification are in directory 'prober_outdir':\n
  barapost-binning.py reads_1.fastq.gz some_sequences_2.fasta -o outdir -r prober_outdir/\n""")
        print("""  5. Process all FASTQ, FASTA and FAST5 files in directory named 'dir_with_seqs'.
  Binning by species ('-s 6'). All these files have been already classified and
   results of classification are in directory 'prober_outdir'. Perform "FAST5 untwisting":\n
  barapost-binning.py -d dir_with_seqs -o outdir -r prober_outdir/ -s 6 -u""")
        # end if
    platf_depend_exit(0)
# end if

if "-v" in sys.argv[1:] or "--version" in sys.argv[1:]:
    print(__version__)
    platf_depend_exit(0)
# end if


import os
import re
import getopt
from glob import glob

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hvr:d:o:s:q:m:i:c:ut:n",
        ["help", "version", "taxannot-resdir=", "indir=", "outdir=", "binning-sensitivity=",
         "min-qual=", "min-seq-len=", "min-pident=", "min-coverage=",
         "untwist-fast5", "threads=", "no-trash"])
except getopt.GetoptError as gerr:
    print( str(gerr) )
    platf_depend_exit(2)
# end try

from src.filesystem import is_fasta, is_fastq, is_fast5
is_fastqa = lambda f: is_fasta(f) or is_fastq(f)

from datetime import datetime
now = datetime.now().strftime("%Y-%m-%d %H.%M.%S")

# |== Default parameters: ==|
fq_fa_list = list() # list with input FASTQ and FASTA files paths
fast5_list = list() # list with input FAST5 files paths
tax_annot_res_dir = "barapost_result" # path to directory with classification results
indir_path = None # path to input directory
outdir_path = "binning_result_{}".format(now.replace(' ', '_')) # path to output directory
sens = ("genus", 5) # binning sensitivity
min_qual = 10 # minimum mean read quality to keep
min_qlen = None # minimum seqeunce length to keep
min_pident = None # minimum alignment identity in percent
min_coverage = None # minimum alignment coverage in percent
untwist_fast5 = False # flag indicating whether to run 'FAST5-untwisting' or not
n_thr = 1 # number of threads to launch
no_trash = False

# Add positional arguments to ` and fast5_list
for arg in args:
    if not is_fastqa(arg) and not is_fast5(arg):
        print("Error: invalid positional argument: `{}`".format(arg))
        print("Only FAST(A/Q/5) files can be specified without a key in command line.")
        platf_depend_exit(1)
    # end if

    if not os.path.exists(arg):
        print("Error: file does not exist:\n `{}`".format(os.path.abspath(arg)))
        platf_depend_exit(1)
    # end if

    if is_fastqa(arg):
        fq_fa_list.append( os.path.abspath(arg) )
    else:
        fast5_list.append( os.path.abspath(arg) )
    # end if
# end for

for opt, arg in opts:

    if opt in ("-o", "--outdir"):
        outdir_path = os.path.abspath(arg)

    elif opt in ("-r", "--annot-resdir"):
        tax_annot_res_dir = arg # we'll check it's existance after this loop

    elif opt in ("-s", "--binning-sensitivity"):
        if arg not in ("0", "1", "2", "3", "4", "5", "6"):
            print("Error: invalid value specified with '{}' option!".format(opt))
            print("""Available values:
 0 for domain
 1 for phylum
 2 for class
 3 for order
 4 for family
 5 for genus
 6 for species""")
            print("Your value: '{}'".format(arg))
            platf_depend_exit(1)
        # end if
        ranks = ("superkingdom", "phylum", "class", "order", "family", "genus", "species")
        sens = (ranks[int(arg)], int(arg))
        del ranks # let it go

    elif opt in ("-q", "--min-qual"):
        try:
            min_qual = float(arg)
            # Comparing numbers with floating point for equality is not a grateful thing,
            #   therefore we'll just in case add 1e-9.
            if min_qual < 1e-9:
                raise ValueError
            # end if
        except ValueError:
            print("Error: minimum read quality must be positive number!")
            print("Your value: `{}`".format(arg))
            platf_depend_exit(1)
        # end try

    elif opt in ("-m", "--min-seq-len"):
        try:
            min_qlen = int(arg)
            if min_qlen < 1:
                raise ValueError
            # end if
        except ValueError:
            print("Error: minimum length of the sequence must be integer number > 1!")
            print("Your value: `{}`".format(arg))
            platf_depend_exit(1)
        # end try

    elif opt in ("-i", "--min-pident"):
        try:
            min_pident = float(arg) / 100
            # Comparing numbers with floating point for equality is not a grateful thing,
            #   therefore we'll just in case add 1e-9.
            if not 1e-9 < min_pident <= 100 + 1e-9:
                raise ValueError
            # end if
        except ValueError:
            print("Error: minimum alignment identity must be positive number (0; 100]")
            print("Your value: `{}`".format(arg))
            platf_depend_exit(1)
        # end try

    elif opt in ("-c", "--min-coverage"):
        try:
            min_coverage = float(arg) / 100
            # Comparing numbers with floating point for equality is not a grateful thing,
            #   therefore we'll just in case add 1e-9.
            # Coverage can be greater than 100% because of gaps.
            if min_coverage <= 1e-9:
                raise ValueError
            # end if
        except ValueError:
            print("Error: minimum alignment coverage must be positive number!")
            print("Your value: `{}`".format(arg))
            platf_depend_exit(1)
        # end try

    elif opt in ("-u", "--untwist-fast5"):
        untwist_fast5 = True

    elif opt in ("-t", "--threasds"):
        try:
            n_thr = int(arg)
            if n_thr < 1:
                raise ValueError
            # end if
        except ValueError:
            print("Error: number of threads must be positive integer number!")
            print("Your value: `{}`".format(arg))
            platf_depend_exit(1)
        # end try
        # Check if number of available threads is >= specified value
        if n_thr > len(os.sched_getaffinity(0)):
            print("""\nWarning! You have specified {} threads to use
  although {} are available.""".format(n_thr, len(os.sched_getaffinity(0))))
            err = True
            while err:
                reply = input("""\nPress ENTER to switch to {} threads,
  or enter 'c' to continue with {} threads anyway,
  or enter 'q' to quit:>>""".format(len(os.sched_getaffinity(0)), n_thr))
                if reply in ("", 'c', 'q'):
                    err = False
                    if reply == "":
                        n_thr = len(os.sched_getaffinity(0))
                        print("\nNumber of threads switched to {}\n".format(n_thr))
                    elif reply == 'c':
                        pass
                    elif reply == 'q':
                        sys.exit(0)
                    # end if
                else:
                    print("Invalid reply: `{}`\a\n".format(reply))
                # end if
            # end while
        # end if
        import multiprocessing as mp

    elif opt in ("-d", "--indir"):

        if not os.path.isdir(arg):
            print("Error: directory `{}` does not exist!".format(arg))
            platf_depend_exit(1)
        # end if
        indir_path = os.path.abspath(arg)

        fq_fa_list.extend(list( filter(is_fastqa, glob("{}{}*".format(indir_path, os.sep))) ))
        fast5_list.extend(list( filter(is_fast5, glob("{}{}*".format(indir_path, os.sep))) ))

    elif opt in ("-n", "--no_trash"):
        no_trash = True
    # end if
# end for

# Check if "prober result" directory is specified
if not os.path.isdir(tax_annot_res_dir):
    print("Error: directory `{}` does not exist!".format(tax_annot_res_dir))
    if tax_annot_res_dir == "barapost_result":
        print("""Maybe, output directory generated by `barapost-prober.py` hasn't been named `barapost_result`
    and you have forgotten to specify `-r` option.""")
    platf_depend_exit(1)
    # end if
# end if

num_files = len(fq_fa_list) + len(fast5_list)

# If no FAST(A/Q/5) file have been specified
if num_files == 0:
    # If input directory was specified -- exit
    if not indir_path is None:
        print("""Error: no input FASTQ or FASTA files specified
  or there is no FASTQ and FASTA files in the input directory.\n""")
        platf_depend_exit(1)

    # If input directory was not specified -- look for FASTQ files in working directory
    else:
        fq_fa_list.extend(list( filter(is_fastqa, glob("{}{}*".format(os.getcwd(), os.sep))) ))
        fast5_list.extend(list( filter(is_fast5, glob("{}{}*".format(os.getcwd(), os.sep))) ))

        # If there are nothing to process -- just show help message
        if num_files == 0:
            print("\nbarapost-binning.py (Version {})\n".format(__version__))
            print("Usage:")
            print("  barapost-binning.py one.fastq.gz another.fasta -r tax_annotation_dir [...] [OPTIONS]")
            print("For more detailed description, run:")
            print(" barapost-binning.py -h\n")
            platf_depend_exit(0)
        else:
            # Ask if a user wants to proceed or he/she ran it occasionally and wants just help message
            print("\n {} fasta and/or fastq files are found in working directory.\n".format(len(fq_fa_list)))
            err = True
            while err:
                reply = input("""Press ENTER to process them
  or enter 'h' to just see help message:>> """)
                if reply == "":
                    err = False
                elif reply == 'h':
                    err = False
                    print('\n' + '-'*15)
                    print("  barapost-binning.py (Version {})\n".format(__version__))
                    print("Usage:")
                    print("  barapost-binning.py one.fastq.gz another.fasta -r tax_annotation_dir [...] [OPTIONS]")
                    print("For more detailed description, run:")
                    print("  barapost-binning.py -h\n")
                    platf_depend_exit(0)
                else:
                    print("Invalid reply: {}\n".format(reply))
                # end if
            # end while
        # end if
    # end if
# end if


# Check if there are duplicated basenames in input files:
for lst in (fq_fa_list, fast5_list):
    for path in lst:
        bname = os.path.basename(path)
        same_bnames = tuple(filter(lambda f: os.path.basename(f) == bname, lst))
        if len(same_bnames) != 1:
            print("Error: input files must have different names")
            print("List of files having same name:")
            for p in same_bnames:
                print("`{}`".format(p))
            # end for
            platf_depend_exit(1)
        # end if
    # end for
# end for
del bname, same_bnames, lst


# Check it here once and not further in imported modules
if len(fast5_list) != 0:
    sys.stdout.write("Importing h5py...")
    try:
        import h5py
    except ImportError as imperr:
        print("\nPackage `h5py` is not installed: " + str(imperr))
        print("\n `h5py` package is necessary for FAST5 files binning.")
        print(" Please, install it (e.g. `pip3 install h5py`).")
        print(" Tip for Linux users: you may need to install `libhdf5-dev` with your packet manager first and then go to pip.")
        platf_depend_exit(1)
    # end try
    print("\rImporting h5py... ok")
# end if

# Sort input files in order to process them in alphabetical order
fq_fa_list.sort()
fast5_list.sort()

# Create output directory
if not os.path.isdir(outdir_path):
    try:
        os.makedirs(outdir_path)
    except OSError as oserr:
        print("Error: unable to create result directory")
        print("barapost-binning just tried to create directory `{}` and crushed.".format(outdir_path))
        print("Reason: {}".format( str(oserr) ))
        platf_depend_exit(1)
    # end try
# end if


def get_checkstr(fast5_fpath):
    # Function returns string that will help barapost-binning to find
    #     TSV file generated by prober and barapost while processing FASTQ file
    #     that in turn is basecalled 'fast5_fpath'-file.
    #
    # Function first searches for ID given to file by programs like of MinKNOW.
    # That is:
    #     1) sequence of 40 (I've seen 40, maybe there can be other number)
    #     latin letters in lower case interlaced with numbers;
    #     2) underscore;
    #     3) number of file within sequenator run;
    # For example: file named "FAK94973_e6f2851ddd414655574208c18f2f51e590bf4b27_0.fast5"
    #     has checkstring "e6f2851ddd414655574208c18f2f51e590bf4b27_0".
    # "FAK94973" is not regarding because it can be pruned by basecaller. For example, Guppy acts in this way.
    #
    # If no such distinctive string is found in FAST5 file name
    #     (file can be renamed by the user after sequensing)
    #     whole file name (except of the '.fast5' extention) is returned as checksting.
    #
    # :param fast5_fpath: path to FAST5 file meant to be processed;
    # :type fast5_fpath: str;
    #
    # Returns checkstring described above.

    try:
        # I'll lower the 40-character barrier down to 30 just in case.
        filename_payload = re.search(r"([a-zA-Z0-9]{30,}_[0-9]+)", fast5_fpath).group(1)
    except AttributeError:
        return os.path.basename(fast5_fpath).replace(".fast5", "")
    else:
        return filename_payload
    # end try
# end def get_checkstr

from src.platform import get_logfile_path

from src.printlog import get_full_time, printlog_info, printlog_error
from src.printlog import printlog_error_time, log_info, printn, printlog_info_time
import logging
logfile_path = get_logfile_path("barapost-binning", outdir_path)
logging.basicConfig(filename=logfile_path,
    format='%(levelname)s: %(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO, filemode='w')
log_info(sys.platform)
log_info(sys.implementation)
log_info(sys.version)

print("|=== barapost-binning.py (version {}) ===|\n".format(__version__))
log_info("barapost-binning.py (version {})".format(__version__))
print(get_full_time() + " - Start working\n")
log_info("Start working.")

# Some possible warnings:
if len(fq_fa_list) == 0 and n_thr != 1 and not "-u" in sys.argv[1:] and not "--untwist-fast5" in sys.argv[1:]:
    print("\nWarning! Binning FAST5 files in parallel doesn't give any profit.")
    print("Number of threads is switched to 1.")
    n_thr = 1
# end if
if len(fast5_list) == 0 and untwist_fast5:
    print("\nWarning! No FAST5 file has been given to barapost-binning's input.")
    print("Therefore, `-u` (`--untwist-fast5`) flag does not make any sense.")
    print("Ignoring it.\n")
    untwist_fast5 = False
# end if


# Make sure that each file meant to be processed has it's directory with TSV result file
#    generated by prober and barapost.

printn("Primary validation...")
if not untwist_fast5:
    for fpath in fast5_list:
        # Get number of directories in 'tax_annot_res_dir' where results of current FAST5
        #    baraposting are located.
        possible_fast5_resdirs_num = len( glob("{}{}*{}*".format(tax_annot_res_dir, os.sep, get_checkstr(fpath))) )

        if possible_fast5_resdirs_num == 1:
            continue # OK
        elif possible_fast5_resdirs_num == 0: # there is no such a directory
            print()
            printlog_error_time("Error: classification for following FAST5 file is missing:")
            printlog_error("  `{}`".format(fpath))
            printlog_error("Try running barapost-binning with `-u` (`--untwist-fast5`) flag.")
            print()
            platf_depend_exit(5)
        else: # there are multiple directories where prober-barapost results can be located
            printlog_error_time("Error: multiple result directories match FAST5 file meant to be binned")
            printlog_error("File: `{}`".format(os.path.basename(fpath)))
            printlog_error("Directories:")
            for d in glob("{}{}*{}*".format(tax_annot_res_dir, os.sep, get_checkstr(fpath))):
                printlog_error(d)
            # end for
            printlog_error("  Please, contact the developer -- it is his mistake.\n")
            platf_depend_exit(6)
        # end if
    # end for
# end if

from src.filesystem import get_curr_res_dpath, remove_tmp_files

for fpath in fq_fa_list:
    # Validate new_dpath existance for FASTA and FASTQ files:
    if not os.path.isdir( get_curr_res_dpath(fpath, tax_annot_res_dir) ):
        printlog_error_time("Error: Directory that should have contained results of taxonomic annotation \
for following file does not exist: `{}`.".format(os.path.basename(fpath)))
        printlog_error("Please, make sure that this file have been already processed \
by `barapost-prober.py` and `barapost-local.py`.")
        platf_depend_exit(1)
    # end if
# end for

sys.stdout.write('\r')
printlog_info("Primary validation...ok")
print()

is_fastQA5 = lambda f: not re.search(r".*\.(m)?f(ast)?(a|q|5)(\.gz)?$", f) is None

# Check if there are some results in output directory
if len( list( filter(is_fastQA5, os.listdir(outdir_path)) ) ) != 0:
    printlog_info("Attention! Output directory `{}` is not empty!".format(outdir_path))
    printlog_info("List of sequence-containing files in it:")
    for i, file in enumerate(filter(is_fastQA5, os.listdir(outdir_path))):
        printlog_info("  {}. `{}`".format(i+1, file))
    # end for
    print()

    invalid_reply = True
    while invalid_reply:
        reply = input("""Press ENTER to overwrite all old sequence-containing files
   or enter `r` to rename old directory and to write current results to a new one
   or enter `a` to append new sequences to existing data:>>""")

        if reply == "":
            invalid_reply = False

            printlog_info("You have chosen to remove old files.")
            remove_tmp_files(*filter(is_fastQA5, glob(os.path.join(outdir_path, '*'))))
        elif reply == 'r':
            invalid_reply = False

            printlog_info("You have chosen to rename old directory.")

            from src.filesystem import rename_file_verbosely
            new_name_for_old_dir = rename_file_verbosely(outdir_path)

            # Create new dir
            try:
                os.makedirs(outdir_path)
                # Restore log file from 'new_name_for_old_dir'
                os.rename(os.path.join(new_name_for_old_dir, os.path.basename(logfile_path)),
                    logfile_path)
            except OSError as err:
                printlog_error_time("Filesystem error: {}".format(err))
                platf_depend_exit(1)
            # end try

        elif reply == 'a':
            invalid_reply = False
        else:
            print("Invalid reply: `{}`".format(reply))
        # end if
    # end while
# end if

del is_fastQA5

# Decide whether to create index:
if untwist_fast5:

    # Names of index files
    index_name = "fast5_to_tsvtaxann_idx"

    # Create index directory
    index_dirpath = os.path.join(tax_annot_res_dir, index_name) # name of directory that will contain indicies
    if not os.path.isdir(index_dirpath):
        try:
            os.makedirs(index_dirpath)
        except OSError as oserr:
            printlog_error_time("cannot create index directory")
            printlog_error("Directory that cannot be created: `{}`".format(index_dirpath))
            printlog_error("Reason: `{}`".format( str(oserr) ))
            platf_depend_exit(1)
        # end try
    # end if

    def whether_to_build_index(index_dirpath):
        # Function checks if there are any files in index directory.
        # If there are any, it asks a user whether to create a new index or to use old one.

        # :param index_dirpath: path to index directory;
        # :type index_dirpath: str;

        use_old_index = False

        if len(os.listdir(index_dirpath)) != 0:
            printlog_info("Index file created by `-u` option already exists (left from previous run).")

            error = True

            while error:
                reply = input("""  Press ENTER to make new index file
  or enter 'u' to use old index file:>>""")
                if reply == "":
                    try:
                        for path in glob( os.path.join(index_dirpath, '*') ):
                            os.unlink(path)
                        # end for
                    except OSError as oserr:
                        printlog_error_time("Error: cannot remove old index files!")
                        printlog_error( str(oserr) )
                        platf_depend_exit(1)
                    # end try
                    error = False
                elif reply == 'u':
                    use_old_index = True
                    error = False
                else:
                    print("Invalid reply!\n")
                # end if
            # end while
            printlog_info("You have chosen to {} index file.".format("use old" if use_old_index else "make new"))
            print()
        # end if
        return use_old_index
    # end def whether_to_build_index
# end if


# |===== Create output directory =====|
if not os.path.exists(outdir_path):
    try:
        os.makedirs(outdir_path)
    except OSError as err:
        printlog_error_time("Error: unable to create output directory!")
        printlog_error( str(err) )
        platf_depend_exit(1)
    # end try
# end if


# |=== Module assembling ===|

# Here we are going to import different functions for different use cases:
#   parallel and single-thread procesing requires different functions that
#   performs writing to and binning plain (FASTA, FASTQ) files.
# It is better to check number of threads once and define functions that will
#   be as strait-forward as possible rather than check conditions each time in a spaghetti-function.

# Module, which defines function for binning FAST5 files (with untwisting or not):
FAST5_srt_module = None
# Module, which defines function for binning FASTA and FASTQ files (parallel or not):
QA_srt_module = None
# Module, which defines function for "FAST5-untwisting" (parallel or not):
utw_module = None

try:

    if len(fq_fa_list) != 0:
        if n_thr == 1: # import single-thread FASTA-FASTQ binning function
            import src.binning_modules.single_thread_QA as QA_srt_module
        else: # import parallel FASTA-FASTQ binning function
            import src.binning_modules.parallel_QA as QA_srt_module
        # end if
    # end if

    if len(fast5_list) != 0:

        # Will be None if unwtisting is disabled and True/False otherwise
        use_old_index = None

        if untwist_fast5:
            use_old_index = whether_to_build_index(index_dirpath)
            # We do not need untwisting function if we do not make new index
            if not use_old_index:
                if n_thr == 1: # import single-thread untwisting
                    import src.binning_modules.single_thread_FAST5_utwfunc as utw_module
                else: # import parallel untwisting
                    import src.binning_modules.parallel_FAST5_utwfunc as utw_module
                # end if
            # end if
        # end if

        if use_old_index is None:
            # If untwisting is disabled, import simple FAST5-binning function:
            import src.binning_modules.single_thread_FAST5_binfunc as FAST5_srt_module
        else:
            # If untwisting is enabled, import FAST5-binning function that "knows" about untwisting:
            import src.binning_modules.single_thread_FAST5_binfunc_utw as FAST5_srt_module
        # end if
    # end if
except ImportError as imperr:
    printlog_error_time("Error: module integrity is corrupted!")
    printlog_error(str(imperr))
    platf_depend_exit(1)
# end try


# |===== Proceed =====|

printlog_info('-' * 30)
printlog_info(" - Output directory: `{}`;".format(outdir_path))
printlog_info(" - Logging to `{}`;".format(logging.getLoggerClass().root.handlers[0].baseFilename))
printlog_info(" - Binning according to classification in directory `{}`;".format(tax_annot_res_dir))

printlog_info(" - Binning sensitivity: {};".format(sens[0]))
printlog_info(" - Threads: {};".format(n_thr))
if untwist_fast5:
    printlog_info(' - "FAST5 untwisting" is enabled;')
# end if
print()
printlog_info("   Following filters will be applied:")
printlog_info(" - Quality filter. Threshold: Q{};".format(min_qual))
if not min_qlen is None:
    printlog_info(" - Length filter. Threshold: {} b.p.".format(min_qlen))
# end if
if not min_pident is None:
    printlog_info(" - Alignment identity filter. Threshold: {}%".format(round(min_pident * 100, 2)))
# end if
if not min_coverage is None:
    printlog_info(" - Alignment coverage filter. Threshold: {}%".format(round(min_coverage * 100, 2)))
# end if

s_letter = '' if num_files == 1 else 's'
print()
printlog_info(" {} file{} will be processed.".format( num_files, s_letter))
log_info("Here they are:")
i = 1
for path in fq_fa_list:
    log_info("  {}. `{}`.".format(i, path))
    i += 1
# end for
for path in fast5_list:
    log_info("  {}. `{}`.".format(i, path))
    i += 1
# end for


import src.legacy_taxonomy_handling as legacy_taxonomy_handling

# Form path to taxonomy file:
taxonomy_dir = os.path.join(tax_annot_res_dir, "taxonomy")
if not os.path.isdir(taxonomy_dir):
    os.makedirs(taxonomy_dir)
# end if
taxonomy_path = os.path.join(taxonomy_dir, "taxonomy.tsv")

# Check if there is legacy taxonomy file and, if so, reformat it to new (TSV) format
legacy_taxonomy_handling.check_deprecated_taxonomy(tax_annot_res_dir)


if n_thr != 1:
    from src.spread_files_equally import spread_files_equally
# end if

# |=== Proceed "FAST5-untwisting" if it is enabled ===|

printlog_info('-' * 30)
print()

if untwist_fast5 and not use_old_index:

    printlog_info_time("Untwisting started.")
    printn(" Working...")

    from src.binning_modules.binning_spec import get_tsv_taxann_lst
    tsv_taxann_lst = get_tsv_taxann_lst(tax_annot_res_dir)

    if n_thr == 1:
        for f5_path in fast5_list:
            utw_module.map_f5reads_2_taxann(f5_path, tsv_taxann_lst, tax_annot_res_dir)
            sys.stdout.write('\r')
            printlog_info_time("File `{}` is processed.".format(os.path.basename(f5_path)))
            printn(" Working...")
        # end for
    else:
        pool = mp.Pool(n_thr, initializer=utw_module.init_paral_utw,
            initargs=(mp.Lock(), mp.Lock(),))
        pool.starmap(utw_module.map_f5reads_2_taxann,
            [(sublist, tsv_taxann_lst, tax_annot_res_dir,) for sublist in spread_files_equally(fast5_list, n_thr)])
        pool.close()
        pool.join()
    # end if

    sys.stdout.write('\r')
    printlog_info_time("Untwisting is completed.")
    printlog_info("Index file that maps reads stored in input FAST5 files to \
TSV files containing taxonomic classification is created.")
    printlog_info('-'*20)
    print()
# end if

# Import launching module
if n_thr == 1 or len(fast5_list) != 0:
    from src.binning_modules.launch import launch_single_thread_binning
# end if

if n_thr != 1:
    from src.binning_modules.launch import launch_parallel_binning
# end if


# |=== Proceed binning ===|

printlog_info_time("Binning started.")
printn(" Working...")

res_stats = list()

# Bin FAST5 files:
if len(fast5_list) != 0:
    res_stats.extend(launch_single_thread_binning(fast5_list,
        FAST5_srt_module.bin_fast5_file, tax_annot_res_dir, sens,
            min_qual, min_qlen, min_pident, min_coverage, no_trash))

    # Assign version attribute in FAST5 files to '2.0' -- multiFAST5
    from src.binning_modules.fast5 import assign_version_2
    if len(fast5_list) != 0:
        assign_version_2(fast5_list)
    # end if
# end if

# Bin FASTA and FASTQ files:
if len(fq_fa_list) != 0:
    if n_thr != 1: # in parallel
        res_stats.extend(launch_parallel_binning(fq_fa_list,
            QA_srt_module.bin_fastqa_file, tax_annot_res_dir, sens, n_thr,
            min_qual, min_qlen, min_pident, min_coverage, no_trash))
    else: # in single thread
        res_stats.extend(launch_single_thread_binning(fq_fa_list,
            QA_srt_module.bin_fastqa_file, tax_annot_res_dir, sens,
            min_qual, min_qlen, min_pident, min_coverage, no_trash))
    # end if
# end if

sys.stdout.write('\r')
printlog_info_time("Binning is completed.")
printlog_info('-'*30)
print()

# Summarize statistics
seqs_pass = sum(map(lambda x: x[0], res_stats))
QL_seqs_fail = sum(map(lambda x: x[1], res_stats))
align_seqs_fail = sum(map(lambda x: x[2], res_stats))


# Print som statistics
space_sep_num = "{:,}".format(seqs_pass + QL_seqs_fail + align_seqs_fail).replace(',', ' ')
printlog_info("{} sequences have been processed.".format(space_sep_num))
if QL_seqs_fail > 0:
    len_str = "" if min_qlen is None else " or are shorter than {} b.p".format(min_qlen)
    space_sep_num = "{:,}".format(QL_seqs_fail).replace(',', ' ')
    printlog_info("{} of them have quality < Q{}{}.".format(space_sep_num,
        round(min_qual, 2), len_str))
# end if
if align_seqs_fail > 0:
    space_sep_num = "{:,}".format(align_seqs_fail).replace(',', ' ')
    if not min_pident is None and not min_coverage is None:
        printlog_info("""{} of them had aligned to their best hit with identity < {}%
  or with coverage < {}%""".format(space_sep_num,
            round(min_pident * 100, 2), round(min_coverage * 100, 2)))
    elif not min_pident is None and min_coverage is None:
        printlog_info("{} of them had aligned to their best hit with identity < {}%".format(space_sep_num,
                round(min_pident * 100, 2)))
    elif min_pident is None and not min_coverage is None:
        printlog_info("{} of them had aligned to their best hit with coverage < {}%".format(space_sep_num,
                round(min_coverage * 100, 2)))
    # end if
# end if

space_sep_num = "{:,}".format(seqs_pass).replace(',', ' ')
printlog_info("{} sequences have passed filters.".format(space_sep_num))

print('\n'+ get_full_time() + " - Task is completed!\n")
log_info("Task is completed!")
platf_depend_exit(0)
