from langchain_community.document_loaders import UnstructuredPDFLoader
from pdfminer.pdfdocument import PDFNoValidXRef
from pdfminer.psparser import PSEOF

def load_pdf(pdf_path, mode='elements'):
    try:
        loader = UnstructuredPDFLoader(pdf_path, mode=mode)
        pages = loader.load()
        return pages
    except(PDFNoValidXRef, PSEOF) as e:
        return None