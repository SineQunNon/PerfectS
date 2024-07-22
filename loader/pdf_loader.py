from langchain_community.document_loaders import UnstructuredPDFLoader

def load_pdf(pdf_path, mode='elements'):
    loader = UnstructuredPDFLoader(pdf_path, mode=mode)
    pages = loader.load()
    return pages