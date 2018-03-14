"""

Example that extracts Tables from TETML files and saves them via Pickle

"""

import os
import argparse

from bs4 import BeautifulSoup

from corvid.table_extraction.table_extractor import TetmlTableExtractor
try:
    import cPickle as pickle
except:
    import pickle

from config import TETML_DIR, PICKLE_DIR

DIVIDER = '\n\n-----------------------------------------------\n\n'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_dir', type=str,
                        help='enter path to local directory containing TETML files')
    parser.add_argument('-o', '--output_dir', type=str,
                        help='enter path to local directory to save pickled Tables')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    args = parser.parse_args()

    # define input files
    tetml_dir = args.input_dir if args.input_dir else TETML_DIR

    # define output files
    pickle_dir = args.output_dir if args.output_dir else PICKLE_DIR

    papers = {}
    for tetml_path in os.listdir(tetml_dir):
        paper_id = tetml_path.replace('.tetml', '')
        tetml_path = os.path.join(tetml_dir, tetml_path)
        pickle_path = os.path.join(pickle_dir, paper_id + '.pickle')

        if os.path.exists(pickle_path) and not args.overwrite:
            print('{} already exists. Skipping...'.format(pickle_path))
            continue

        try:
            with open(tetml_path, 'r') as f_tetml:
                print('Extracting tables from {}...'.format(paper_id))
                tables = TetmlTableExtractor.extract_tables(
                    tetml=BeautifulSoup(f_tetml),
                    caption_search_window=3)

                print(DIVIDER.join([str(table) for table in tables]))

                print('Pickling extracted tables for {}...'.format(paper_id))
                with open(pickle_path, 'wb') as f_pickle:
                    pickle.dump(tables, f_pickle)

                papers.update({paper_id: tables})
        except FileNotFoundError as e:
            print(e)
            print('{} missing TETML file. Skipping...'.format(paper_id))

        print(DIVIDER)