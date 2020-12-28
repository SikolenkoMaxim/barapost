# -*- coding: utf-8 -*-

import h5py

import os
import sys

from src.binning_modules.binning_spec import configure_resfile_lines
from src.binning_modules.fast5 import update_file_dict
from src.binning_modules.fast5 import fast5_readids, copy_read_f5_2_f5, copy_single_f5

from src.binning_modules.filters import get_QL_filter, get_QL_trash_fpath
from src.binning_modules.filters import get_align_filter, get_align_trash_fpath

from src.platform import platf_depend_exit
from src.printlog import printl, printn, getwt, err_fmt
from src.fmt_readID import fmt_read_id

from shelve import open as open_shelve

index_name = "fast5_to_tsvtaxann_idx"


def bin_fast5_file(f5_path, tax_annot_res_dir, sens,
        min_qual, min_qlen, min_pident, min_coverage, no_trash, logfile_path):
    """
    Function bins FAST5 file with untwisting.

    :param f5_path: path to FAST5 file meant to be processed;
    :type f5_path: str;
    :param tax_annot_res_dir: path to directory containing taxonomic annotation;
    :type tax_annot_res_dir: str;
    :param sens: binning sensitivity;
    :type sens: str;
    :param min_qual: threshold for quality filter;
    :type min_qual: float;
    :param min_qlen: threshold for length filter;
    :type min_qlen: int (or None, if this filter is disabled);
    :param min_pident: threshold for alignment identity filter;
    :type min_pident: float (or None, if this filter is disabled);
    :param min_coverage: threshold for alignment coverage filter;
    :type min_coverage: float (or None, if this filter is disabled);
    :param no_trash: loical value. True if user does NOT want to output trash files;
    :type no_trash: bool;
    :param logfile_path: path to log file;
    :type logfile_path: str;
    """

    outdir_path = os.path.dirname(logfile_path)

    seqs_pass = 0 # counter for sequences, which pass filters
    QL_seqs_fail = 0 # counter for too short or too low-quality sequences
    align_seqs_fail = 0 # counter for sequences, which align to their best hit with too low identity or coverage

    srt_file_dict = dict()

    index_dirpath = os.path.join(tax_annot_res_dir, index_name) # name of directory that will contain indicies

    # Make filter for quality and length
    QL_filter = get_QL_filter(f5_path, min_qual, min_qlen)
    # Configure path to trash file
    if not no_trash:
        QL_trash_fpath = get_QL_trash_fpath(f5_path, outdir_path, min_qual, min_qlen,)
    else:
        QL_trash_fpath = None
    # end if

    # Make filter for identity and coverage
    align_filter = get_align_filter(min_pident, min_coverage)
    # Configure path to this trash file
    if not no_trash:
        align_trash_fpath = get_align_trash_fpath(f5_path, outdir_path, min_pident, min_coverage)
    else:
        align_trash_fpath = None
    # end if

    # File validation:
    #   RuntimeError will be raised if FAST5 file is broken.
    try:
        # File existance checking is performed while parsing CL arguments.
        # Therefore, this if-statement will trigger only if f5_path's file is not a valid HDF5 file.
        if not h5py.is_hdf5(f5_path):
            raise RuntimeError("file is not of HDF5 (i.e. not FAST5) format")
        # end if

        from_f5 = h5py.File(f5_path, 'r')

        for _ in from_f5:
            break
        # end for
    except RuntimeError as runterr:
        printl(logfile_path, err_fmt("FAST5 file is broken"))
        printl(logfile_path, "Reading the file '{}' crashed.".format(os.path.basename(f5_path)))
        printl(logfile_path, "Reason: {}".format( str(runterr) ))
        printl(logfile_path, "Omitting this file...\n")
        # Return zeroes -- inc_val won't be incremented and this file will be omitted
        return (0, 0, 0)
    # end try

    # singleFAST5 and multiFAST5 files should be processed in different ways
    # "Raw" group always in singleFAST5 root and never in multiFAST5 root
    if "Raw" in from_f5.keys():
        f5_cpy_func = copy_single_f5
    else:
        f5_cpy_func = copy_read_f5_2_f5
    # end if

    readids_to_seek = list(from_f5.keys()) # list of not-binned-yet read IDs

    # Fill the list 'readids_to_seek'
    for read_name in fast5_readids(from_f5):
        # Get rid of "read_"
        readids_to_seek.append(sys.intern(read_name))
    # end for

    # Walk through the index
    index_f5_2_tsv = open_shelve( os.path.join(index_dirpath, index_name), 'r' )

    if not f5_path in index_f5_2_tsv.keys():
        printl(logfile_path, err_fmt("Source FAST5 file not found in index"))
        printl(logfile_path, "Try to rebuild index")
        platf_depend_exit(1)
    # end if

    for tsv_path in index_f5_2_tsv[f5_path].keys():

        read_names = index_f5_2_tsv[f5_path][tsv_path]
        resfile_lines = configure_resfile_lines(tsv_path, sens,
            os.path.join(tax_annot_res_dir, "taxonomy", "taxonomy"), logfile_path)

        for read_name in read_names:
            try:
                hit_names, *vals_to_filter = resfile_lines[sys.intern(fmt_read_id(read_name)[1:])]
            except KeyError:
                printl(logfile_path,
                    err_fmt("missing taxonomic annotation info for read '{}'".format(fmt_read_id(read_name)[1:])))
                printl(logfile_path, "It is stored in '{}' FAST5 file".format(f5_path))
                printl(logfile_path, "Try to make new index file (press ENTER on corresponding prompt).")
                printl(logfile_path, """Or, if does not work for you, make sure that taxonomic annotation info
for this read is present in one of TSV files generated by 'barapost-prober.py' and 'barapost-local.py'.""")
                index_f5_2_tsv.close()
                platf_depend_exit(1)
            # end try

            if not QL_filter(vals_to_filter):
                # Get name of result FASTQ file to write this read in
                if QL_trash_fpath not in srt_file_dict.keys():
                    srt_file_dict = update_file_dict(srt_file_dict, QL_trash_fpath, logfile_path)
                # end if
                f5_cpy_func(from_f5, read_name, srt_file_dict[QL_trash_fpath], logfile_path)
                QL_seqs_fail += 1
            elif not align_filter(vals_to_filter):
                # Get name of result FASTQ file to write this read in
                if align_trash_fpath not in srt_file_dict.keys():
                    srt_file_dict = update_file_dict(srt_file_dict, align_trash_fpath, logfile_path)
                # end if
                f5_cpy_func(from_f5, read_name, srt_file_dict[align_trash_fpath], logfile_path)
                align_seqs_fail += 1
            else:
                for hit_name in hit_names.split("&&"): # there can be multiple hits for single query sequence
                    # Get name of result FASTQ file to write this read in
                    binned_file_path = os.path.join(outdir_path, "{}.fast5".format(hit_name))
                    if binned_file_path not in srt_file_dict.keys():
                        srt_file_dict = update_file_dict(srt_file_dict, binned_file_path, logfile_path)
                    # end if
                    f5_cpy_func(from_f5, read_name, srt_file_dict[binned_file_path], logfile_path)
                # end for
                seqs_pass += 1
            # end if
        # end for

    from_f5.close()
    index_f5_2_tsv.close()

    # Close all binned files
    for file_obj in filter(lambda x: not x is None, srt_file_dict.values()):
        file_obj.close()
    # end for

    printl(logfile_path, "\r{} - File '{}' is binned.".format(getwt(), os.path.basename(f5_path)))
    printn(" Working...")

    return (seqs_pass, QL_seqs_fail, align_seqs_fail)
# end def bin_fast5_file
