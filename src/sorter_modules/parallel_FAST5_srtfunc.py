# -*- coding: utf-8 -*-


from src.sorter_modules.common import *


try:
    import h5py
except ImportError as imperr:
    print(err_fmt("package 'h5py' is not installed"))
    print( "Exact error description given by the interpreter: {}".format(str(imperr)) )
    print("\n  'h5py' package is necessary for FAST5 files sorting.")
    print("  Please, install it (e.g. 'pip3 install h5py').")
    print("  Tip for Linux users: you may need to install 'libhdf5-dev' with your packet manager first and then go to pip.")
    platf_depend_exit(1)
# end try


def copy_read_f5_2_f5(from_f5, read_name, to_f5_path):
    """
    Function copies a read with ID 'read_name'
        from 'from_f5' multiFAST5 file to to_f5 multiFAST5 one.

    :param from_f5: FAST5 file object to copy a read from;
    :type from_f5: h5py.File;
    :param read_name: ID of a read to copy;
    :type read_name: str;
    :param to_f5: destination FAST5 file;
    :type to_f5: h5py.File;
    """
    try:
        with h5py.File(to_f5_path, 'a') as to_f5:
            from_f5.copy(read_name, to_f5)
        # end with
    except ValueError as verr:
        printl("\n\n ! - Error: {}".format( str(verr) ))
        printl("Reason is probably the following:")
        printl("  read that is copying to the result file is already in it.")
        printl("ID of the read: '{}'".format(read_name))
        printl("File: '{}'".format(to_f5.filename))
        platf_depend_exit(1)
    # end try
# end def copy_read_f5_2_f5


def copy_single_f5(from_f5, read_name, to_f5_path):
    """
    Function copies a read with ID 'read_name'
        from 'from_f5' singleFAST5 file to to_f5 multiFAST5 one.

    :param from_f5: FAST5 file object to copy a read from;
    :type from_f5: h5py.File;
    :param read_name: ID of a read to copy;
    :type read_name: str;
    :param to_f5: destination FAST5 file;
    :type to_f5: h5py.File;
    """
    try:
        with h5py.File(to_f5_path, 'a') as to_f5:
            read_group = read_name
            to_f5.create_group(read_group)

            for ugk_subgr in from_f5["UniqueGlobalKey"]:
                from_f5.copy("UniqueGlobalKey/"+ugk_subgr, to_f5[read_group])
            # end for

            read_number_group = "Raw/Reads/"+next(iter(from_f5["Raw"]["Reads"]))
            read_number = re_search(r"(Read_[0-9]+)", read_number_group).group(1)
            from_f5.copy(from_f5[read_number_group], to_f5[read_group])
            to_f5.move("{}/{}".format(read_group, read_number), "{}/Raw".format(read_group))

            for group in from_f5:
                if group != "Raw" and group != "UniqueGlobalKey":
                    from_f5.copy(group, to_f5["/{}".format(read_group)])
                # end if
            # end for
        # end with
    except ValueError as verr:
        printl("\n\n ! - Error: {}".format( str(verr) ))
        printl("Reason is probably the following:")
        printl("  read that is copying to the result file is already in it.")
        printl("ID of the read: '{}'".format(read_name))
        printl("File: '{}'".format(to_f5.filename))
        platf_depend_exit(1)
    # end try
# end def copy_single_f5


def fast5_readids(fast5_file):

    if "Raw" in fast5_file.keys():
        yield "read_" + fmt_read_id(fast5_file.filename)
        return
    else:
        for readid in fast5_file:
            if readid.startswith("read_"):
                yield readid
            # end if
        # end for
    # end if
    return
# end def fast5_readids


def sort_fast5_file(f5_path):
    """
    Function sorts FAST5 file without untwisting.

    :param f5_path: path to FAST5 file meant to be processed;
    :type f5_path: str;
    """

    seqs_pass = 0
    seqs_fail = 0

    trash_fpath = os.path.join(outdir_path, "qual_less_Q{}{}.fast5".format(int(min_ph33_qual),
            minlen_fmt_str))

    new_dpath = glob("{}{}*{}*".format(tax_annot_res_dir, os.sep, get_checkstr(f5_path)))[0]
    tsv_res_fpath = get_res_tsv_fpath(new_dpath)
    resfile_lines = configure_resfile_lines(tsv_res_fpath, sens)

    from_f5 = h5py.File(f5_path, 'r')

    # singleFAST5 and multiFAST5 files should be processed in different ways
    # "Raw" group always in singleFAST5 root and never in multiFAST5 root
    if "Raw" in from_f5.keys():
        f5_cpy_func = copy_single_f5
    else:
        f5_cpy_func = copy_read_f5_2_f5
    # end if

    # Create an iterator that will yield records
    seq_records_iterator = fast5_readids(from_f5)
    # Dict for storing batches of sequences meant to be written to output files:
    to_write = dict()
    stop = False # for outer while-loop

    while not stop:

        # Extract batch of records of 'n_thr' size and find their destination paths:
        for _ in range(n_thr):

            try:
                read_name = next(seq_records_iterator)
            except StopIteration:
                stop = True # for outer while-loop
                break
            # end try

            try:
                hit_name, ph33_qual, q_len = resfile_lines[sys.intern(fmt_read_id(read_name))] # omit 'read_' in the beginning of FAST5 group's name
            except KeyError:
                printl(err_fmt("""read '{}' not found in TSV file containing taxonomic annotation.
      This TSV file: '{}'""".format(fmt_read_id(read_name), tsv_res_fpath)))
                printl("Try running sorter with '-u' (--untwist-fast5') flag.\n")
                platf_depend_exit(1)
            # end try

            # If read is found in TSV file:
            q_len = SeqLength(q_len)
            if ph33_qual != '-' and ph33_qual < min_ph33_qual:
                # Place this sequence to trash file
                to_write[read_name] = trash_fpath
                seqs_fail += 1
            else:
                # Get name of result FASTQ file to write this read in
                sorted_file_path = os.path.join(outdir_path, "{}.fast5".format(hit_name))
                # Place this sequence to sorted file
                to_write[read_name] = sorted_file_path
                seqs_pass += 1
            # end if
        # end for

        # Write batch of records to output files:
        with write_lock:
            for read_id, outfpath in to_write.items():
                f5_cpy_func(from_f5, read_id, outfpath)
            # end for
        # end with
        to_write.clear()
    # end while

    # Write the rest of 'uneven' data to output files:
    if len(to_write) != 0:
        with write_lock:
            for read_id, outfpath in to_write.items():
                f5_cpy_func(from_f5, read_id, outfpath)
            # end for
        # end with
    # end if

    from_f5.close()
    return (seqs_pass, seqs_fail)
# end def sort_fast5_file


def init_paral_sorting(write_lock_buff, inc_val_buff, inc_val_lock_buff):

    global write_lock
    write_lock = write_lock_buff

    global inc_val
    inc_val = inc_val_buff

    global inc_val_lock
    inc_val_lock = inc_val_lock_buff
# end def init_paral_sorting


def assign_version_2(fast5_list):
    # Assign version attribute to '2.0' -- multiFAST5
    for f5path in fast5_list:
        with h5py.File(f5path, 'a') as f5file:
            f5file.attrs["file_version"] = b"2.0"
        # end with
    # end for
# end def assign_version_2
