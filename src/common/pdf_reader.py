from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

from flask import abort
import common.event_logger as logger

class PDFToText():

    def __init__(self, file_path):
        """
        Setup the pdf parser to be able to read the passed in file.

        Args:
            file_path (string): Path to the pdf that will be worked on.
        """        
        try:
            self.file_path = file_path
            with open(self.file_path, 'rb') as f:
                self.parser = PDFParser(f)
                self.doc = PDFDocument()
                self.parser.set_document(self.doc)
                self.doc.set_parser(self.parser)
                self.doc.initialize('')
                self.rsrcmgr = PDFResourceManager()
                self.laparams = LAParams()
                self.laparams.char_margin = 1.0
                self.laparams.word_margin = 1.0
                self.device = PDFPageAggregator(self.rsrcmgr, laparams=self.laparams)
                self.interpreter = PDFPageInterpreter(self.rsrcmgr, self.device)
        except Exception as e:
            logger.logTraceback('---'+str(e)+'---', e)
            abort(500, description=e)

    def extract_pdf_text(self):
        """
        Extract the parser's file, only returning anything from a text object.

        Returns:
            string: The extracted text from the pdf.
        """        

        extracted_text = ''
        logger.logEvent('Beginning extraction of PDF to Text...')
        try:
            for page in self.doc.get_pages():
                self.interpreter.process_page(page)
                layout = self.device.get_result()
                for lt_obj in layout:
                    if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                        extracted_text += lt_obj.get_text().replace('\n', ' ')
            return extracted_text
        except Exception as e:
            logger.logTraceback('---'+str(e)+'---', e)
            abort(500, description=e)