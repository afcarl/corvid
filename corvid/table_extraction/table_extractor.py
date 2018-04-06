"""

Classes that extract as many Tables as possible from a local PDF.

"""

import os

from typing import List

try:
    import cPickle as pickle
except ImportError:
    import pickle

from corvid.types.table import Table

from corvid.table_extraction.pdf_to_xml_parser import PDFToXMLParser, \
    TetmlPDFToXMLParser, OmnipagePDFToXMLParser
from corvid.table_extraction.xml_to_tables_parser import XMLToTablesParser, \
    TetmlXMLToTablesParser, OmnipageXMLToTablesParser


class TableExtractor(object):
    def extract(self, paper_id: str, source_pdf_path: str,
                *args, **kwargs) -> List[Table]:
        raise NotImplementedError


class XMLTableExtractor(TableExtractor):
    def __init__(self,
                 pdf_to_xml_parser: PDFToXMLParser,
                 xml_to_tables_parser: XMLToTablesParser):
        self.pdf_to_xml_parser = pdf_to_xml_parser
        self.xml_to_tables_parser = xml_to_tables_parser

    def extract(self, paper_id: str, source_pdf_path: str,
                is_use_xml_cache: bool = True, is_use_pkl_cache: bool = True,
                *args, **kwargs) -> List[Table]:
        """Returns Tables extracted from a PDF while caching intermediate
        steps like using an external tool to process PDF -> XML.
        """
        source_xml_path = self.pdf_to_xml_parser.get_target_path(paper_id)
        if is_use_xml_cache and os.path.exists(source_xml_path):
            pass
        else:
            self.pdf_to_xml_parser.parse(paper_id, source_pdf_path)

        tables_pkl_path = self.xml_to_tables_parser.get_target_path(paper_id)
        if is_use_pkl_cache and os.path.exists(tables_pkl_path):
            with open(tables_pkl_path, 'rb') as f_pkl:
                tables = pickle.load(f_pkl)
        else:
            tables = self.xml_to_tables_parser.parse(paper_id, source_xml_path,
                                                     *args, **kwargs)

        return tables


class TetmlTableExtractor(XMLTableExtractor):
    def __init__(self,
                 tet_bin_path: str,
                 xml_cache_dir: str,
                 pkl_cache_dir: str):
        pdf_to_xml_parser = TetmlPDFToXMLParser(tet_bin_path,
                                                xml_cache_dir)
        xml_to_tables_parser = TetmlXMLToTablesParser(pkl_cache_dir)
        super(TetmlTableExtractor, self).__init__(pdf_to_xml_parser,
                                                  xml_to_tables_parser)


class OmnipageTableExtractor(XMLTableExtractor):
    def __init__(self,
                 omnipage_bin_path: str,
                 xml_cache_dir: str,
                 pkl_cache_dir: str):
        pdf_to_xml_parser = OmnipagePDFToXMLParser(omnipage_bin_path,
                                                   xml_cache_dir)
        xml_to_tables_parser = OmnipageXMLToTablesParser(pkl_cache_dir)
        super(OmnipageTableExtractor, self).__init__(pdf_to_xml_parser,
                                                     xml_to_tables_parser)
