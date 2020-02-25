# -*- coding: utf-8 -*-
# Module defines finctions that are "miscallaneous" for sorter.

import os
import sys
import shelve
from glob import glob
from re import search as re_search

from src.platform import platf_depend_exit
from src.printlog import printl, err_fmt


def get_res_tsv_fpath(new_dpath):
    """
    Function returns current TSV file. Sorting will be performad according to this file.

    :param new_dpath: current result directory;
    :type new_dpath: str;
    """

    brpst_resfile_patt = r".*classification\.tsv$"

    is_similar_to_tsv_res = lambda f: True if f == "classification.tsv" else False

    if not os.path.exists(new_dpath):
        printl(logfile_path, err_fmt("directory '{}' does not exist!".format(new_dpath)))
        printl(logfile_path, """ Please make sure you have performed taxonomic annotation of the following file
    '{}...'
    with 'prober.py' 'barapost.py'""".format(os.path.basename(new_dpath)))
        printl(logfile_path, """Also this error might occur if you forget to specify result directory
    generated by 'prober.py' with '-r' option.""")
        platf_depend_exit(0)
    # end if

    # Recent file will be the first in sorted list
    tsv_res_fpath = list( filter(is_similar_to_tsv_res, sorted(os.listdir(new_dpath))) )[0]

    return os.path.join(new_dpath, tsv_res_fpath)
# end def get_res_tsv_fpath


def get_tsv_taxann_lst(tax_annot_res_dir):
    """
    Function returns list of path to TSV files that contain taxonomic annotation.

    :param tax_annot_res_dir: path to '-r' directory;
    :type tax_annot_res_dir: str;
    """

    # Get all directories nested in 'tax_annot_res_dir':
    dir_lst = filter(lambda f: True if os.path.isdir(f) else False,
        glob( os.path.join(tax_annot_res_dir, "*") ))
    # Get all directories that contain "classification.tsv" file:
    taxann_dir_lst = filter(lambda d: os.path.exists(os.path.join(d, "classification.tsv")),
        dir_lst)
    # Get path to TSV files containing taxonomy annotation info
    tsv_taxann_lst = map(lambda d: os.path.join(d, "classification.tsv"),
        taxann_dir_lst)

    return tuple(tsv_taxann_lst)
# end def get_tsv_taxann_lst


# There is an accession number in the beginning of local FASTA file
local_name_hit_patt = r"OWN_SEQ_[0-9]+_"
# Pattern that will match ID of seqeunce in FASTA file generated by SPAdes
spades_patt = r"(NODE)_([0-9]+)"
# Pattern that will match ID of seqeunce in FASTA file generated by a5
a5_patt = r"(scaffold)_([0-9]+)"
# Pattern that will match file path in sequence ID
path_patt = r"\(_(.+)_\)"


ranks = ("superkingdom", "phylum", "class", "order", "family", "genus", "species")


def find_rank_for_filename(sens, taxonomy):
    """
    Function forms name of sorted file according to annotation and sorting sensitivity.

    :param sens: sorting sensitivity;
    :type sens: tuple<str, int>;
    :param taxonomy: taxonomy from taxopnomy file;
    :type taxonomy: tuple<tuple<str>>;
    """
    rank_name = sens[0]
    rank_num = sens[1]

    if taxonomy[rank_num][1] != "":
        # If we've got rank that we need -- return it
        return taxonomy[rank_num][1]
    else:
        # Otherwise -- recursively go up to the root of taxonomy tree
        new_sens = (ranks[rank_num-1], rank_num-1)
        return find_rank_for_filename( new_sens, taxonomy ) + ";no_{}".format(rank_name)
    # end if
# end def find_rank_for_filename


def format_taxonomy_name(hit_acc, hit_def, sens, taxonomy_path):
    """
    Function formats taxonomy name according to chosen sensibiliry of sorting.
    :param hit_acc: accession(s) of best hit(s);
    :type hit_acc: str;
    :param hit_def: annotation of best hit;
    :type hit_def: str;
    :param sens: sensibility returned by 'get_classif_sensibility()' function.
        It's value can be one of the following strings: "genus", "species";
    :type sens: str;
    :param taxonomy_path: path to taxonomy file;
    :type taxonomy_path: str;

    Returns formatted hit name of 'str' type;
    """

    # If there is no hit -- we are sure what to do!
    if hit_def == "No significant similarity found":
        return "unknown"
    # end if

    best_hit_annots = list() # list of strings that will be names of sorted files

    for acc, annotation in zip(hit_acc.split('&&'), hit_def.split('&&')):

        # Get taxonomy
        try:
            with shelve.open(taxonomy_path, 'r') as tax_file:
                taxonomy = tax_file[acc]
            # end with
        except KeyError:
            printl("taxonomy file error 994")
            printl("Cant find taxonomy for reference sequnce '{}'".format(acc))
            printl("It's annotation: '{}'".format(annotation))
            printl("Probably you should run \"barapost.py\" once again and rebuild the database --")
            printl("  \"barapost.py\" will make taxonomy file consistent.")
            platf_depend_exit(1)
        # end try

        # If it is beautiful tuple-formatted taxonomy -- find rank name for filename
        if isinstance(taxonomy, tuple):

            best_hit_annots.append(find_rank_for_filename(sens, taxonomy))
            if sens[0] == "species":
                genus_sens = ("genus", sens[1]-1)
                genus_name = find_rank_for_filename(genus_sens, taxonomy)
                species_name = best_hit_annots[len(best_hit_annots)-1]
                best_hit_annots[len(best_hit_annots)-1] = "{}_{}".format(genus_name, species_name)
            # end if

        # Otherwise consider sequence ID
        elif isinstance(taxonomy, str):

            # Check if hit is a sequence from SPAdes or a5 assembly:
            spades_match_obj = re_search(spades_patt, modif_hit_name)
            a5_match_obj = re_search(a5_patt, modif_hit_name)

            if not spades_match_obj is None or not a5_match_obj is None:

                for match_obj in (spades_match_obj, a5_match_obj):

                    # If hit is a sequence from SPAdes or a5 assembly
                    if not match_obj is None:

                        # Find path to file with assembly:
                        try:
                            assm_path = re_search(path_patt, modif_hit_name).group(1)
                        except AttributeError:
                            assm_path = None
                        # end

                        node_or_scaff = match_obj.group(1) # get word "NODE" or "scaffold"
                        node_scaff_num = match_obj.group(2) # get it's number

                        # SPAdes generate "NODEs"
                        if node_or_scaff == "NODE":
                            assmblr_name = "SPAdes"
                        # a5 generates "scaffolds"
                        elif node_or_scaff == "scaffold":
                            assmblr_name = "a5"
                        # There cannot be enything else
                        else:
                            print(err_fmt("signature of sequence ID from assembly not recognized: '{}'".format(hit_name)))
                            platf_depend_exit(1)
                        # end if

                        # Include file path to sorted file name
                        # Replace path separetor with underscore in order not to held a bacchanalia in file system.
                        if assm_path is not None:
                            if sens[0] != "species":
                                # Return only path and "NODE" in case of SPAdes and "scaffold" in case of a5
                                best_hit_annots.append('_'.join( (assmblr_name, "assembly", assm_path.replace(os.sep, '_'), node_or_scaff) ))
                            else:
                                # Return path and "NODE_<N>" in case of SPAdes and "scaffold_<N>" in case of a5
                                best_hit_annots.append('_'.join( (assmblr_name, "assembly", assm_path.replace(os.sep, '_'), node_or_scaff,
                                    node_scaff_num) ))
                            # end if
                        else:
                            if sens[0] != "species":
                                # Return only "NODE" in case of SPAdes and "scaffold" in case of a5
                                best_hit_annots.append(assmblr_name + "_assembly_" + node_or_scaff)
                            else:
                                # Return "NODE_<N>" in case of SPAdes and "scaffold_<N>" in case of a5
                                best_hit_annots.append('_'.join( (assmblr_name + "assembly", node_or_scaff, node_scaff_num )))
                            # end if
                        # end if
                    # end if
                # end for
            else:
                # If it is not assembly -- merely return sequence ID
                best_hit_annots.append(annotation)
            # end if
        else:
            # Execution must not reach here
            print("\nFatal error 8754.")
            print("Please, contact the developer -- it is his fault.")
            platf_depend_exit(1)
        # end if
    # end for

    # Return deduplicated names
    return "&&".join(set(best_hit_annots))
# end def format_taxonomy_name


def configure_resfile_lines(tsv_res_fpath, sens, taxonomy_path):
    """
    Function returns dictionary, where keys are sequence (i.e. sequences meant to be sorted) IDs,
        and values are corresponding hit names.

    :param tsv_res_fpath: path to current TSV file. Sorting will be performed accorfing to this TSV file;
    :type tsv_res_fpath: str;
    :param sens: sorting sensitivity;
    :type sens: str;
    :parm taxonomy_path: path to taxonomy file;
    :type taxonomy_file: str;
    """

    resfile_lines = dict()

    with open(tsv_res_fpath, 'r') as brpst_resfile:

        brpst_resfile.readline() # pass the head of the table
        line = brpst_resfile.readline().strip() # get the first informative line

        while line != "":
            splt = line.split('\t')
            read_name = sys.intern(splt[0])
            hit_name = splt[1]
            hit_acc = splt[2]

            try:
                quality = float(splt[8]) # we will filter by quality
            except ValueError as verr:
                if splt[8] == '-':
                    # Keep minus as quality if there is no quality information.
                    # Error will not be raised.
                    quality = splt[8]
                else:
                    printl(logfile_path, err_fmt("query quality parsing error"))
                    printl(logfile_path,  str(verr) )
                    printl(logfile_path, "Please, contact the developer.")
                    platf_depend_exit(1)
                # end if
            # end try

            try:
                query_len = int(splt[3])  # we will filter by length
            except ValueError as verr:
                printl(logfile_path, err_fmt("query length parsing error"))
                printl(logfile_path,  str(verr) )
                printl(logfile_path, "Please, contact the developer.")
                platf_depend_exit(1)
            # end try

            try:
                pident = float(splt[5]) # we will filter by identity
            except ValueError as verr:
                if splt[5] == '-':
                    # Keep minus as quality if there is no quality information.
                    # Error will not be raised.
                    pident = splt[5]
                else:
                    printl(logfile_path, err_fmt("alignment identity parsing error"))
                    printl(logfile_path,  str(verr) )
                    printl(logfile_path, "Please, contact the developer.")
                    platf_depend_exit(1)
                # end if
            # end try

            try:
                coverage = float(splt[4]) # we will filter by coverage
            except ValueError as verr:
                if splt[4] == '-':
                    # Keep minus as quality if there is no quality information.
                    # Error will not be raised.
                    coverage = splt[4]
                else:
                    printl(logfile_path, err_fmt("alignment coverage parsing error"))
                    printl(logfile_path,  str(verr) )
                    printl(logfile_path, "Please, contact the developer.")
                    platf_depend_exit(1)
                # end if
            # end try

            resfile_lines[read_name] = [format_taxonomy_name(hit_acc, hit_name, sens, taxonomy_path),
                quality, query_len, pident, coverage]

            line = brpst_resfile.readline().strip() # get next line
        # end while
    # end with

    return resfile_lines
# end def configure_resfile_lines


def get_checkstr(fast5_fpath):
    """
    Function returns string that will help fasQA5-sorter to find
        TSV file generated by prober and barapost while provessing FASTQ file
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


def update_file_dict(srt_file_dict, new_fpath):
    try:
        if new_fpath.endswith(".fast5"):
            srt_file_dict[sys.intern(new_fpath)] = h5py.File(new_fpath, 'a')
        else:
            srt_file_dict[sys.intern(new_fpath)] = open(new_fpath, 'a')
        # end if
    except OSError as oserr:
        printl(logfile_path, err_fmt("error while opening one of result files"))
        printl(logfile_path, "Errorneous file: '{}'".format(new_fpath))
        printl(logfile_path,  str(oserr) )
        platf_depend_exit(1)
    # end try
    return srt_file_dict
# end def update_file_dict
