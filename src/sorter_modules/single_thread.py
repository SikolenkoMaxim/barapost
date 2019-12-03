# -*- coding: utf-8 -*-


def printl(text=""):
    """
    Function for printing text to console and to log file.
    """
    print(text)
    logfile.write(str(text).strip('\r') + '\n')
    logfile.flush()
# end def printl


from src.sorter_modules.common import *


def write_fastq_record(sorted_file, fastq_record):
    """
    :param sorted_file: file, which data from fastq_record is written in
    :type sorted_file: _io.TextIOWrapper
    :param fastq_record: dict of 4 elements. Elements are four corresponding lines of FASTQ
    :type fastq_record: dict<str: str>
    """
    try:
        sorted_file.write(fastq_record["seq_id"])
        sorted_file.write(fastq_record["seq"])
        sorted_file.write(fastq_record["opt_id"])
        sorted_file.write(fastq_record["qual_line"])
    except OSError as err:
        printl(err_fmt( str(err) ))
        printl("File: '{}'".format(sorted_path))
        platf_depend_exit(0)
    # end try
# end def write_fastq_record


def write_fasta_record(sorted_file, fasta_record):
    """
    :param sorted_file: file, which data from fasta_record is written in
    :type sorted_file: _io.TextIOWrapper
    :param fasta_record: dict of 2 elements. Elements are four corresponding lines of FASTA
    :type fasta_record: dict<str: str>
    """
    try:
        sorted_file.write(fasta_record["seq_id"])
        sorted_file.write(fasta_record["seq"])
    except OSError as err:
        printl(err_fmt( str(err) ))
        printl("File: '{}'".format(sorted_path))
        platf_depend_exit(0)
    # end try
# end def write_fasta_record


def sort_fastqa_file(fq_fa_path):
    """
    Function for single-thread sorting FASTQ and FASTA files.

    :param fq_fa_path: path to FASTQ (of FASTA) file meant to be processed;
    :type fq_fa_path: str;
    """

    seqs_pass = 0
    seqs_fail = 0
    srt_file_dict = dict()

    new_dpath = get_curr_res_dpath(fq_fa_path, tax_annot_res_dir)
    tsv_res_fpath = get_res_tsv_fpath(new_dpath)
    resfile_lines = configure_resfile_lines(tsv_res_fpath, sens)

    # Configure path to trash file
    if is_fastq(fq_fa_path):
        seq_records_generator = fastq_records
        write_fun =  write_fastq_record
        trash_fpath = os.path.join(outdir_path, "qual_less_Q{}{}.fastq".format(int(min_ph33_qual),
            minlen_fmt_str))
    else:
        seq_records_generator = fasta_records
        write_fun = write_fasta_record
        trash_fpath = os.path.join(outdir_path, "len_less_{}.fasta".format(min_qlen))
    # end if

    for fastq_rec in seq_records_generator(fq_fa_path):

        read_name = sys.intern(fmt_read_id(fastq_rec["seq_id"])) # get ID of the sequence

        try:
            hit_name, ph33_qual, q_len = resfile_lines[read_name] # find hit corresponding to this sequence
        except KeyError:
            printl(err_fmt("""read '{}' not found in TSV file containing taxonomic annotation.
This TSV file: '{}'""".format(read_name, tsv_res_fpath)))
            printl("Make sure that this read has been already processed by 'prober.py' and 'barapost.py'.")
            platf_depend_exit(1)
        # end try

        # If read is found in TSV file:
        q_len = SeqLength(q_len)
        if q_len < min_qlen or (ph33_qual != '-' and ph33_qual < min_ph33_qual):
            # Place this sequence to trash file
            if trash_fpath not in srt_file_dict.keys():
                srt_file_dict = update_file_dict(srt_file_dict, trash_fpath)
            # end if
            write_fun(srt_file_dict[trash_fpath], fastq_rec) # write current read to sorted file
            seqs_fail += 1
        else:
            # Get name of result FASTQ file to write this read in
            sorted_file_path = os.path.join(outdir_path, "{}.fast{}".format(hit_name,
                'q' if is_fastq(fq_fa_path) else 'a'))
            if sorted_file_path not in srt_file_dict.keys():
                srt_file_dict = update_file_dict(srt_file_dict, sorted_file_path)
            # end if
            write_fun(srt_file_dict[sorted_file_path], fastq_rec) # write current read to sorted file
            seqs_pass += 1
        # end if
    # end for

    # Close all sorted files
    for file_obj in srt_file_dict.values():
        file_obj.close()
    # end for
    return (seqs_pass, seqs_fail)
# end def sort_fastqa_file


def update_file_dict(srt_file_dict, new_fpath):
    try:
        if new_fpath.endswith(".fast5"):
            srt_file_dict[sys.intern(new_fpath)] = h5py.File(new_fpath, 'a')
        else:
            srt_file_dict[sys.intern(new_fpath)] = open(new_fpath, 'a')
        # end if
    except OSError as oserr:
        printl(err_fmt("error while opening one of result files"))
        printl("Errorneous file: '{}'".format(new_fpath))
        printl( str(oserr) )
        platf_depend_exit(1)
    # end try
    return srt_file_dict
# end def update_file_dict