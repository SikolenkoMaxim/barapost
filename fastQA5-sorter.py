#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "4.2.b"
# Year, month, day
__last_update_date__ = "2020-01-29"

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
    print("\n  fastQA5-sorter.py\n  Version {}; {} edition;\n".format(__version__, __last_update_date__))
    print("DESCRIPTION:\n")
    print("""fastQA5-sorter.py -- this script is designed for sorting (dividing into separate files)
    FASTQ and FASTA files processed by "barapost.py".""")
    print("""Moreover, it can sort FAST5 files according to taxonomical annotation of basecallsed
  FASTQ files. For details, see README.md on github page
  ('FAST5 sorting' section): https://github.com/masikol/barapost\n
"fastQA5-sorter.py" is meant to be used just after "barapost.py".""")
    if "--help" in sys.argv[1:]:
        print("----------------------------------------------------------\n")
        print("""Default parameters:\n
 - if no input files are specified, all FASTQ, FASTA and FAST5 files in current directory will be processed;
 - sorting sensitivity (see '-s' option): 'genus';
 - output directory ('-o' option): directory named '"sorter_result_<date_and_time_of_run>"''
   nested in working directory;
 - minimum mean quality of a read to keep ('-q' option): 10;
 - filtering by length ('-m' option) is disabled;
 - "FAST5 untwisting" is disaled;""")
    # end if

    print("----------------------------------------------------------\n")
    print("""Files that you want 'fastQA5-sorter.py' to process should be
    specified as positional arguments (see EXAMPLE #2 running detailed (--help) help message).\n""")
    print("OPTIONS:\n")
    print("""-h (--help) --- show help message.
   '-h' -- brief, '--help' -- full;\n""")
    print("-v (--version) --- show version;\n")
    print("""-r (--taxannot-resdir) --- result directory containging taxonomic annotation.
   This is directory specified to 'prober.py' with '-o' option (and to 'barapost.py' with '-r' option).
   Default value is "barapost_result";\n""")
    print("""-d (--indir) --- directory which contains FAST(Q/A/5) files
   meant to be sorted. I.e. all FASTQ, FASTA and FAST5 files in this direcory will be processed;\n""")
    print("-o (--outdir) --- output directory;\n")
    print("""-s (--sorting-sensitivity) --- sorting sensitivity,
   i.e. the lowest taxonomy rank that sorter regards;
   Available values: 0 for species, 1 for genus. Default is 1 (genus);\n""")
    print("""-q (--min-qual) --- minimum mean Q quality of a read to keep;
   Reads of lower quality will be written to separate "trash" file;
   Default value: 10;\n""")
    print("""-m (--min-seq-len) --- minimum length of a sequence to keep.
   Shorter sequences will be written to separate "trash" file (see Example #2).
   Filtering by length is disabled by default;\n""")
    print("""-u (--untwist-fast5) --- flag option. If specified, FAST5 files will be
   sorted considering that corresponding FASTQ files may contain reads from other FAST5 files
   and reads from a particular FAST5 file may be ditributed among multiple FASTQ files.
   Feature is disabled by default;\n""")
    print("""-z (--gzip) --- Compress output files with gzip.
   Compression affects only FASTA and FASTQ files;
   Values: 1 for compress, 0 for not to compress (see Example #2).
   1 is default value.""")
    print("""-t (--threads) --- number of threads to launch.
   Affects only FASTA and FASTQ sorting.
   Sorter processes FAST5 files in 1 thread anyway (exception is "FAST5 untwisting").""")

    if "--help" in sys.argv[1:]:
        print("----------------------------------------------------------\n")
        print("EXAMPLES:\n")
        print("""  1. Process all FASTA and FASTQ files in working directory with default settings:\n
  fastQA5-sorter.py\n""")
        print("""  2. Process all files, which start with "some_my_fastq" in the working directory.
  Move reads with mean quality < Q15 to "trash" file.
  Move sequences with shorter than 3000 b.p. to "trash" file.
  Do not compress output files:\n
  fastQA5-sorter.py some_my_fastq* -q 15 -z 0 -m 3000\n""")
        print("""  3. Process one FASTQ file with default settings.
  File 'reads.fastq' has been already classified and
   results of classification are in directory 'prober_outdir':\n
  fastQA5-sorter.py reads.fastq.gz -r prober_outdir/\n""")
        print("""  4. Process a FASTQ file and a FASTA file, place results in 'outdir' directory.
  Files 'reads.fastq.gz' and 'another_sequences.fasta' have been already classified and
   results of classification are in directory 'prober_outdir':\n
  fastQA5-sorter.py reads_1.fastq.gz some_sequences_2.fasta -o outdir -r prober_outdir/\n""")
        print("""  5. Process all FASTQ and FASTA files in directory named 'dir_with_seqs'. Sort by species.
  All these files have been already classified and
   results of classification are in directory 'prober_outdir'. Perform "FAST5 untwisting":\n
  fastQA5-sorter.py -d dir_with_seqs -o outdir -r prober_outdir/ -s 0 -u""")
        # end if
    platf_depend_exit(0)
# end if

if "-v" in sys.argv[1:] or "--version" in sys.argv[1:]:
    print(__version__)
    platf_depend_exit(0)
# end if


import os
import getopt
from glob import glob
from re import search as re_search
from src.printlog import err_fmt, printl, printn, getwt, get_full_time

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hvr:d:o:s:q:m:ut:z:",
        ["help", "version", "taxannot-resdir=", "indir=", "outdir=",
         "sorting-sensitivity=", "min-qual=", "min-seq-len=",
         "untwist-fast5", "threads=", "gzip="])
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
outdir_path = "sorter_result_{}".format(now.replace(' ', '_')) # path to output directory
sens = "genus" # sorting sensitivity
min_qual = 10 # minimum mean read quality to keep
min_qlen = None # minimum seqeunce length to keep
untwist_fast5 = False # flag indicating whether to run 'FAST5-untwisting' or not
n_thr = 1 # number of threads to launch
compress = True # flag indicating whether to compress output files or not

# Add positional arguments to ` and fast5_list
for arg in args:
    if not is_fastqa(arg) and not is_fast5(arg):
        print(err_fmt("invalid positional argument: '{}'".format(arg)))
        print("Only FAST(A/Q/5) files can be specified without a key in command line.")
        platf_depend_exit(1)
    # end if

    if not os.path.exists(arg):
        print(err_fmt("file does not exist:\n '{}'".format(os.path.abspath(arg))))
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

    elif opt in ("-r", "--taxannot-resdir"):
        tax_annot_res_dir = arg # we'll check it's existance after this loop

    elif opt in ("-s", "--sorting-sensitivity"):
        if arg not in ("0", "1"):
            print(err_fmt("invalid value specified with '{}' option!".format(opt)))
            print("Available values: 0 for species, 1 for genus. 1 is default.")
            print("Your value: '{}'".format(arg))
            platf_depend_exit(1)
        # end if
        sens = ("species", "genus")[int(arg)]

    elif opt in ("-q", "--min-qual"):
        try:
            min_qual = float(arg)
            if min_qual < 0:
                raise ValueError
            # end if
        except ValueError:
            print(err_fmt("minimum read quality must be positive number!"))
            print("Your value: '{}'".format(arg))
            platf_depend_exit(1)
        # end try

    elif opt in ("-m", "--min-seq-len"):
        try:
            min_qlen = int(arg)
            if min_qlen < 1:
                raise ValueError
            # end if
        except ValueError:
            print(err_fmt("minimum length of the sequence must be integer number > 1!"))
            print("Your value: '{}'".format(arg))
            platf_depend_exit(1)
        # end try

    elif opt in ("-u", "--untwist-fast5"):
        untwist_fast5 = True

    elif opt in ("-z", "--gzip"):
        if arg in ("0", "1"):
            compress = False if arg == "0" else True
        else:
            print(err_fmt("invalid value passed with '{}' option".format(opt)))
            print("Available values: 1 for compress 0 for not to compress.")
            print("Your value: '{}'".format(arg))
            platf_depend_exit(1)
        # end if

    elif opt in ("-t", "--threasds"):
        try:
            n_thr = int(arg)
            if n_thr < 1:
                raise ValueError
            # end if
        except ValueError:
            print(err_fmt("number of threads must be positive integer number!"))
            print("Your value: '{}'".format(arg))
            platf_depend_exit(1)
        # end try
        # Check if number of available threads is >= specified value
        if n_thr > len(os.sched_getaffinity(0)):
            print("""\nWarning! You have specified {} threads to use
  although {} are available.""".format(n_thr, len(os.sched_getaffinity(0))))
            error = True
            while error:
                reply = input("""\nPress ENTER to switch to {} threads,
  or enter 'c' to continue with {} threads anyway,
  or enter 'q' to quit:>>""".format(len(os.sched_getaffinity(0)), n_thr))
                if reply in ("", 'c', 'q'):
                    error = False
                    if reply == "":
                        n_thr = len(os.sched_getaffinity(0))
                        print("\nNumber of threads switched to {}\n".format(n_thr))
                    elif reply == 'c':
                        pass
                    elif reply == 'q':
                        sys.exit(0)
                    # end if
                else:
                    print("Invalid reply: '{}'\a\n".format(reply))
                # end if
            # end while
        # end if
        import multiprocessing as mp

    elif opt in ("-d", "--indir"):

        if not os.path.isdir(arg):
            print(err_fmt("directory '{}' does not exist!".format(arg)))
            platf_depend_exit(1)
        # end if
        indir_path = os.path.abspath(arg)

        fq_fa_list.extend(list( filter(is_fastqa, glob("{}{}*".format(indir_path, os.sep))) ))
        fast5_list.extend(list( filter(is_fast5, glob("{}{}*".format(indir_path, os.sep))) ))
    # end if
# end for

# Check if "prober result" directory is specified
if not os.path.isdir(tax_annot_res_dir):
    print(err_fmt("directory '{}' does not exist!".format(tax_annot_res_dir)))
    if tax_annot_res_dir == "barapost_result":
        print("""Maybe, output directory generated by 'prober.py' hasn't been named 'barapost_result'
    and you have forgotten to specify '-r' option.""")
    platf_depend_exit(1)
    # end if
# end if

num_files = len(fq_fa_list) + len(fast5_list)

# If no FAST(A/Q/5) file have been specified
if num_files == 0:
    # If input directory was specified -- exit
    if not indir_path is None:
        print(err_fmt("""no input FASTQ or FASTA files specified
  or there is no FASTQ and FASTA files in the input directory.\n"""))
        platf_depend_exit(1)
    
    # If input directory was not specified -- look for FASTQ files in working directory
    else:
        fq_fa_list.extend(list( filter(is_fastqa, glob("{}{}*".format(os.getcwd(), os.sep))) ))
        fast5_list.extend(list( filter(is_fast5, glob("{}{}*".format(os.getcwd(), os.sep))) ))

        # If there are nothing to process -- just show help message
        if num_files == 0:
            print("\nfastQA5-sorter.py (Version {})\n".format(__version__))
            print("Usage:")
            print("  fastQA5-sorter.py one.fastq.gz another.fasta -r tax_annotation_dir [...] [OPTIONS]")
            print("For more detailed description, run:")
            print(" fastQA5-sorter.py -h\n")
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
                    print("  fastQA5-sorter.py (Version {})\n".format(__version__))
                    print("Usage:")
                    print("  fastQA5-sorter.py one.fastq.gz another.fasta -r tax_annotation_dir [...] [OPTIONS]")
                    print("For more detailed description, run:")
                    print("  fastQA5-sorter.py -h\n")
                    platf_depend_exit(0)
                else:
                    print("Invalid reply: {}\n".format(reply))
                # end if
            # end while
        # end if
    # end if
# end if

# Check it here once and not further inimported  modules
if len(fast5_list) != 0:
    try:
        import h5py
    except ImportError as imperr:
        print("\nPackage 'h5py' is not installed: " + str(imperr))
        print("\n 'h5py' package is necessary for FAST5 files sorting.")
        print(" Please, install it (e.g. 'pip3 install h5py').")
        print(" Tip for Linux users: you may need to install 'libhdf5-dev' with your packet manager first and then go to pip.")
        platf_depend_exit(1)
    # end try
# end if

# Sort input files in order to process them in alphabetical order
fq_fa_list.sort()
fast5_list.sort()

# Some warnings:

if len(fq_fa_list) == 0 and n_thr != 1 and not "-u" in sys.argv[1:] and not "--untwist-fast5" in sys.argv[1:]:
    print("\nWarning! Sorting FAST5 files in parallel doesn't give any profit.")
    print("Number of threads is switched to 1.")
    n_thr = 1
# end if

if len(fast5_list) == 0 and untwist_fast5:
    print("\nWarning! No FAST5 file has been given to sorter's input.")
    print("Therefore, '-u' ('--untwist-fast5') flag does not make any sense.")
    print("Ignoring it.")
    untwist_fast5 = False
# end if


# Create output directory
if not os.path.isdir(outdir_path):
    try:
        os.makedirs(outdir_path)
    except OSError as oserr:
        print(err_fmt("unable to create result directory"))
        print("fastQA5-sorter just tried to create directory '{}' and crushed.".format(outdir_path))
        print("Reason: {}".format( str(oserr) ))
        platf_depend_exit(1)
    # end try
# end if


def get_checkstr(fast5_fpath):
    """
    Function returns string that will help fasQA5-sorter to find
        TSV file generated by prober and barapost while processing FASTQ file
        that in turn is basecalled 'fast5_fpath'-file.
    
    Function first searches for ID given to file by programs like of MinKNOW.
    That is:
        1) sequence of 40 (I've seen 40, maybe there can be other number)
        latin letters in lower case interlaced with numbers;
        2) underscore;
        3) number of file within sequenator run;
    For example: file named "FAK94973_e6f2851ddd414655574208c18f2f51e590bf4b27_0.fast5"
        has checkstring "e6f2851ddd414655574208c18f2f51e590bf4b27_0".
    "FAK94973" is not regarding because it can be pruned by basecaller. For example, Guppy acts in this way.

    If no such distinctive string is found in FAST5 file name
        (file can be renamed by the user after sequensing)
        whole file name (except of the '.fast5' extention) is returned as checksting.

    :param fast5_fpath: path to FAST5 file meant to be processed;
    :type fast5_fpath: str;

    Returns checkstring described above.
    """

    try:
        # I'll lower the 40-character barrier down to 30 just in case.
        filename_payload = re_search(r"([a-zA-Z0-9]{30,}_[0-9]+)", fast5_fpath).group(1)
    except AttributeError:
        return os.path.basename(fast5_fpath).replace(".fast5", "")
    else:
        return filename_payload
    # end try
# end def get_checkstr

from src.platform import get_logfile_path
logfile_path = get_logfile_path("fastQA5-sorter", outdir_path)

printl(logfile_path, "\n |=== fastQA5-sorter.py (version {}) ===|\n".format(__version__))
printl(logfile_path, get_full_time() + "- Start working\n")

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
            print(err_fmt("""directory that may be considered as valid for sorting of file
  '{}'\n    is not found in the directory '{}'""".format(fpath, tax_annot_res_dir)))
            print("Try running sorter with '-u' ('--untwist-fast5') flag.\n")
            platf_depend_exit(1)
        else: # there are multiple directories where prober-barapost results can be located
            print(err_fmt("multiple result directories match FAST5 file meant to be sorted"))
            print("  Please, contact the developer -- it is his mistake.\n")
            platf_depend_exit(1)
        # end if
    # end for
# end if

from src.filesystem import get_curr_res_dpath

for fpath in fq_fa_list:
    # Validate new_dpath existance for FASTA and FASTQ files:
    if not os.path.isdir( get_curr_res_dpath(fpath, tax_annot_res_dir) ):
        print(err_fmt("prober result directory not found"))
        print("""Directory that should have contained results of taxonomic annotation of the following file:
  '{}' does not exist.""".format(os.path.basename(fpath)))
        print("Please, make sure that this file have been already processed by 'prober.py' and 'barapost.py'.")
        platf_depend_exit(1)
    # end if
# end for

print("\rPrimary validation... ok\n")

is_fastQA5 = lambda f: True if not re_search(r".*\.(m)?f(ast)?(a|q|5)(\.gz)?$", f) is None else False

# Check if there are some results in output directory
if len( list( filter(is_fastQA5, os.listdir(outdir_path)) ) ) != 0:
    printl(logfile_path, "Attention! Output directory '{}' is not empty!".format(outdir_path))
    printl(logfile_path, "List of sequence-containing files in it:")
    for i, file in enumerate(filter(is_fastQA5, os.listdir(outdir_path))):
        printl(logfile_path, "  {}. '{}'".format(i+1, file))
    # end for
    print()
    
    invalid_reply = True
    while invalid_reply:
        reply = input("""Press ENTER to overwrite all old sequence-containing files
    or enter 'r' to rename old directory and to write current results to a new one
    or enter 'a' to append new data to the existing one:>>""")

        if reply == "":
            invalid_reply = False

            printl(logfile_path, "You have chosen to remove old files.")
            for file in filter(is_fastQA5, os.listdir(outdir_path)):
                printl(logfile_path, "Removing '{}'".format( os.path.join(outdir_path, file) ))
                os.unlink( os.path.join(outdir_path, file) )
            # end for
        elif reply == 'r':
            invalid_reply = False

            printl(logfile_path, "You have chosen to rename old directory.")
            from src.filesystem import rename_file_verbosely
            rename_file_verbosely(outdir_path, logfile_path)
        elif reply == 'a':
            invalid_reply = False
        else:
            print("Invalid reply: '{}'".format(reply))
        # end if
        printl(logfile_path)
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
            printl(logfile_path, err_fmt("cannot create index directory"))
            printl(logfile_path, "Directory that cannot be created: '{}'".format(index_dirpath))
            printl(logfile_path, "Reason: '{}'".format( str(oserr) ))
            platf_depend_exit(1)
        # end try
    # end if

    def whether_to_build_index(index_dirpath):
        """
        Function checks if there are any files in index directory.
        If there are any, it asks a user whether to create a new index or to use old one.

        :param index_dirpath: path to index directory;
        :type index_dirpath: str;
        """

        use_old_index = False

        if len(os.listdir(index_dirpath)) != 0:
            printl(logfile_path, "Attention! Index file created by '-u' (--untwist_fast5) option exists (left from previous run).")

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
                        printl(logfile_path, err_fmt("Cannot remove old index files!"))
                        printl(logfile_path,  str(oserr) )
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
            printl(logfile_path, "You have chosen to {} index file.\n".format("use old" if use_old_index else "make new"))
        # end if
        return use_old_index
    # end def whether_to_build_index
# end if


# |===== Create output directory =====|
if not os.path.exists(outdir_path):
    try:
        os.makedirs(outdir_path)
    except Exception as err:
        printl(logfile_path, err_fmt("unable to create output directory!"))
        printl(logfile_path,  str(err) )
        platf_depend_exit(1)
    # end try
# end if


# |=== Module assembling ===|

# Here we are going to import different functions for different use cases:
#   parallel and single-thread procesing requires different functions that
#   performs writing to and sorting plain (FASTA, FASTQ) files.
# It is better to check number of threads once and define functions that will
#   be as strait-forward as possible rather than check conditions each time in a spaghetti-function.

# Module, which defines function for sorting FAST5 files (with untwisting or not):
FAST5_srt_module = None
# Module, which defines function for sorting FASTA and FASTQ files (parallel or not):
QA_srt_module = None
# Module, which defines function for "FAST5-untwisting" (parallel or not):
utw_module = None

try:

    if len(fq_fa_list) != 0:
        if n_thr == 1: # import single-thread FASTA-FASTQ sorting function
            import src.sorter_modules.single_thread_QA as QA_srt_module
        else: # import parallel FASTA-FASTQ sorting function
            import src.sorter_modules.parallel_QA as QA_srt_module
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
                    import src.sorter_modules.single_thread_FAST5_utwfunc as utw_module
                else: # import parallel untwisting
                    import src.sorter_modules.parallel_FAST5_utwfunc as utw_module
                # end if
            # end if
        # end if

        if use_old_index is None:
            # If untwisting is disabled, import simple FAST5-sorting function:
            import src.sorter_modules.single_thread_FAST5_srtfunc as FAST5_srt_module
        else:
            # If untwisting is enabled, import FAST5-sorting function that "knows" about untwisting:
            import src.sorter_modules.single_thread_FAST5_srtfunc_utw as FAST5_srt_module
        # end if
    # end if
except ImportError as imperr:
    printl(logfile_path, err_fmt("module integrity is corrupted!"))
    printl(logfile_path, str(imperr))
    platf_depend_exit(1)
# end try


# |===== Proceed =====|

printl(logfile_path, '-' * 30)
printl(logfile_path, " - Output directory: '{}';".format(outdir_path))
printl(logfile_path, " - Logging to '{}';".format(logfile_path))
printl(logfile_path, " - Sorting according to classification in directory '{}';".format(outdir_path))
printl(logfile_path, " - Sorting sensitivity: '{}';".format(sens))
printl(logfile_path, " - Minimum mean quality of a read to keep: {};".format(min_qual))
if not min_qlen is None:
    printl(logfile_path, " - Minimum length of a read to keep: {};".format(min_qlen))
# end if
printl(logfile_path, " - Threads: {};".format(n_thr))
if untwist_fast5:
    printl(logfile_path, " - \"FAST5 untwisting\" is enabled;")
# end if

s_letter = '' if num_files == 1 else 's'
printl(logfile_path, "\n {} file{} will be processed.".format( num_files, s_letter))
with open (logfile_path, 'a') as logfile:
    logfile.write("Here they are:\n")
    i = 1
    for path in fq_fa_list:
        logfile.write("    {}. '{}'\n".format(i, path))
        i += 1
    # end for
    for path in fast5_list:
        logfile.write("    {}. '{}'\n".format(i, path))
        i += 1
    # end for
# end with

if n_thr != 1:
    from src.spread_files_equally import spread_files_equally
# end if

# |=== Proceed "FAST5-untwisting" if it is enabled ===|

printl(logfile_path, '-' * 30 + '\n')

if untwist_fast5 and not use_old_index:

    printl(logfile_path, "{} - Untwisting started.".format(getwt()))
    printn(" Working...")

    from src.sorter_modules.sorter_spec import get_tsv_taxann_lst
    tsv_taxann_lst = get_tsv_taxann_lst(tax_annot_res_dir)

    if n_thr == 1:
        for f5_path in fast5_list:
            utw_module.map_f5reads_2_taxann(f5_path, tsv_taxann_lst, tax_annot_res_dir, logfile_path)
            printl(logfile_path, "\r{} - File '{}' is processed.".format(getwt(), os.path.basename(f5_path)))
            printn(" Working...")
        # end for
    else:
        pool = mp.Pool(n_thr, initializer=utw_module.init_paral_utw,
            initargs=(mp.Lock(), mp.Lock(),))
        pool.starmap(utw_module.map_f5reads_2_taxann,
            [(sublist, tsv_taxann_lst, tax_annot_res_dir, logfile_path,) for sublist in spread_files_equally(fast5_list, n_thr)])
        pool.close()
        pool.join()
    # end if

    printl(logfile_path, "\r{} - Untwisting is completed.".format(getwt()))
    printl(logfile_path, """Index file that maps reads stored in input FAST5 files to
  TSV files containing taxonomic classification is created.""")
    printl(logfile_path, '-'*20+'\n')
# end if

# Import launching module
if n_thr == 1 or len(fast5_list) != 0:
    from src.sorter_modules.launch import launch_single_thread_sorting
# end if

if n_thr != 1:
    from src.sorter_modules.launch import launch_parallel_sorting
# end if


# |=== Proceed sorting ===|

printl(logfile_path, "{} - Sorting started.".format(getwt()))
printn(" Working...")

res_stats = list()

# Sort FAST5 files:
if len(fast5_list) != 0:
    res_stats.extend(launch_single_thread_sorting(fast5_list,
        FAST5_srt_module.sort_fast5_file, tax_annot_res_dir, sens,
            min_qual, min_qlen, logfile_path))
# end if

# Sort FASTA and FASTQ files:
if len(fq_fa_list) != 0:
    if n_thr != 1: # in single thread
        res_stats.extend(launch_parallel_sorting(fq_fa_list,
            QA_srt_module.sort_fastqa_file, tax_annot_res_dir, sens, n_thr,
            min_qual, min_qlen, logfile_path))
    else: # in parallel
        res_stats.extend(launch_single_thread_sorting(fq_fa_list,
            QA_srt_module.sort_fastqa_file, tax_annot_res_dir, sens,
            min_qual, min_qlen, logfile_path))
# end if

printl(logfile_path, "\r{} - Sorting is completed.\n".format(getwt()))

# Assign version attribute in FAST5 files to '2.0' -- multiFAST5
from src.sorter_modules.fast5 import assign_version_2
if len(fast5_list) != 0:
    assign_version_2(fast5_list)
# end if

# Summarize statistics
seqs_pass = sum(map(lambda x: x[0], res_stats))
seqs_fail = sum(map(lambda x: x[1], res_stats))


# For printing pretty large numbers
from src.get_undr_sep_number import get_undr_sep_number

printl(logfile_path, "{} sequences have been processed.".format(get_undr_sep_number(seqs_pass + seqs_fail)))
if seqs_fail > 0:
    len_fmt_str = " and length ({} bp)".format(min_qlen) if not min_qlen is None else ""
    printl(logfile_path, "{} of them have passed quality (Q{}){} controle.".format(get_undr_sep_number(seqs_pass),
        int(min_qual), len_fmt_str))
# end if

fastqa_res_files = tuple(filter(is_fastqa, glob(os.path.join(outdir_path, '*'))))

# Exit now if there is nothing to compress
if len(fastqa_res_files) == 0 or not compress:
    printl(logfile_path, '\n'+ get_full_time() + "- Task is completed!\n")
    platf_depend_exit(0)
# end if

# Otherwise -- proceed gzipping

printl(logfile_path, "{} - Gzipping output files started".format(getwt()))

# GNU gzip utility is faster, but there can be presence of absence of it :)
gzip_util = "gzip"
util_found = False
for directory in os.environ["PATH"].split(os.pathsep):
    if os.path.isdir(directory) and gzip_util in os.listdir(directory):
        util_found = True
        break
    # end if
# end for

# Define function that will gzip files

if util_found:

    def gzip_func(fpaths):
        """Function that compresses output FASTA and FASTQ files with gzip utility.
        
        :param fpaths: list of paths to file to compress;
        :type fpaths: list<str>;
        """

        for fpath in fpaths:
            try:
                if not os.system("{} {}".format(gzip_util, fpath)) == 0:
                    raise OSError("Gzip error")
                # end if
            except OSError as oserr:
                printl(logfile_path, err_fmt("cannot gzip file '{}'".format(os.path.basename(fpath))))
                printl(logfile_path, "Reason: {}".format( str(oserr) ))
                # Try to gzip others -- continue loop
            else:
                printl(logfile_path, "{} - Gzipping '{}' completed".format(getwt(), os.path.basename(fpath)))
            # end try
        # end for
    # end def gzip_func
else:

    from shutil import copyfileobj as shutil_copyfileobj
    from gzip import open as open_as_gzip

    def gzip_func(fpaths):
        """Function that compresses output FASTA and FASTQ files with Python gzip and shutil modules.
        
        :param fpaths: list of paths to file to compress;
        :type fpaths: list<str>;
        """
        for fpath in fpaths:
            try:
                # form .fasta.gz file 'by hand'
                with open(fpath, 'rb') as fastqa_file, open_as_gzip(fpath+".gz", "wb") as faqgz_file:
                    shutil_copyfileobj(fastqa_file, faqgz_file)
                # end with
                os.unlink(fpath) # remove plain FASTA file
            except OSError as oserr:
                printl(logfile_path, err_fmt("cannot gzip file '{}'".format(os.path.basename(fpath))))
                printl(logfile_path, "Reason: {}".format( str(oserr) ))
                # Try to gzip others -- continue loop
            else:
                printl(logfile_path, "{} - Gzipping '{}' completed".format(getwt(), os.path.basename(fpath)))
            # end try
        # end for
    # end def gzip_func
# end if

if n_thr == 1: # single-thread compressing

    gzip_func(fastqa_res_files)

else: # compress in parallel

    pool = mp.Pool(n_thr)
    pool.starmap(gzip_func, [(sublist,) for sublist in spread_files_equally(fastqa_res_files, n_thr)])
    pool.close()
    pool.join()
# end if

printl(logfile_path, "{} - Gzipping output files is completed".format(getwt()))

printl(logfile_path, '\n'+ get_full_time() + "- Task is completed!\n")
platf_depend_exit(0)
