import os

def get_template(ppt_tempalte):
    pptx_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template', ppt_tempalte)
    
    return pptx_template