# -*- coding: utf-8  -*-

from src.printlog import getwt, printl, printn
from src.filesystem import get_curr_res_dpath, create_result_directory, remove_tmp_files, is_fastq
from src.write_classification import write_classification

from src.fasta import fasta_packets
from src.fastq import fastq_packets

from src.barapost_modules.barapost_spec import look_around, launch_blastn, parse_align_results_xml

import os
from re import search as re_search


def process(fq_fa_list, packet_size, tax_annot_res_dir, blast_algorithm, use_index, logfile_path):
    """
    Function performs 'many_files'-parallel mode of single-thread mode.
    They differ only in ptinting to the console.

    :param fq_fa_list: list of paths to FASTA and FASTQ files meant to be processed;
    :type fq_fa_list: list<str>;
    :param parallel: flag indicating if parallel mode if enabled.
        Influences only on printing to the console;
    :type parallel: bool;
    """

    taxonomy_path = os.path.join(tax_annot_res_dir, "taxonomy","taxonomy")
    queries_tmp_dir = os.path.join(tax_annot_res_dir, "queries-tmp")
    local_fasta = os.path.join(tax_annot_res_dir, "local_database", "local_seq_set.fasta")

    # Iterate over source FASTQ and FASTA files
    for i, fq_fa_path in enumerate(fq_fa_list):

        # Create the result directory with the name of FASTQ of FASTA file being processed:
        new_dpath = create_result_directory(fq_fa_path, tax_annot_res_dir)

        # "hname" means human readable name (i.e. without file path and extention)
        infile_hname = os.path.basename(fq_fa_path)
        infile_hname = re_search(r"(.+)\.(m)?f(ast)?(a|q)(\.gz)?$", infile_hname).group(1)

        # Look around and ckeck if there are results of previous runs of this script
        # If 'look_around' is None -- there is no data from previous run
        previous_data = look_around(new_dpath, fq_fa_path, blast_algorithm, logfile_path)

        if previous_data is None: # If there is no data from previous run
            num_done_reads = 0 # number of successfully processed sequences
            tsv_res_path = "{}.tsv".format(os.path.join(new_dpath,
                "classification")) # form result tsv file path
        else: # if there is data from previous run
            num_done_reads = previous_data["n_done_reads"] # get number of successfully processed sequences
            tsv_res_path = previous_data["tsv_respath"] # result tsv file sholud be the same as during previous run
        # end if

        packet_generator = fastq_packets if is_fastq(fq_fa_path) else fasta_packets

        for packet in packet_generator(fq_fa_path, packet_size, num_done_reads):

            if packet["fasta"] == "":
                printl(logfile_path, "\nFile '{}' has been already completely processed.".format(fq_fa_path))
                printl(logfile_path, "Omitting it.")
                continue
            # end if

            # Align the packet
            align_xml_text = launch_blastn(packet["fasta"], blast_algorithm,
                use_index, queries_tmp_dir, local_fasta)

            # Get result tsv lines
            result_tsv_lines = parse_align_results_xml(align_xml_text,
                packet["qual"], taxonomy_path)

            # Write the result to tsv
            write_classification(result_tsv_lines, tsv_res_path)
        # end for

        printl(logfile_path, "\r{} - File '{}' is processed.".format(getwt(), os.path.basename(fq_fa_path)))
        printn("Working...")

    # end for
    remove_tmp_files( os.path.join(queries_tmp_dir, "query{}_tmp.fasta".format(os.getpid())) )
# end def process
