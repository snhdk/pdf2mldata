import sys
import json
import re
import os
from collections.abc import Iterable
from pdfminer.layout import LAParams, LTContainer, LTAnno, LTChar, LTTextBox, LTComponent, LTTextContainer, LTTextLine, LTPage, LTLayoutContainer
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator, PDFLayoutAnalyzer
from pdfminer.pdfpage import PDFPage


def iterable(obj):
    return isinstance(obj, Iterable)


def visit_txt_boxes(page_no, node):
    if isinstance(node, LTTextContainer):
        txt = node.get_text()
        txt = txt.strip()        
        txt = re.sub('\s+', ' ', txt)
        if len(txt) > 0:
            return {
                "text": txt,
                "bbox": node.bbox
            }
        else:
           return None
    elif iterable(node):
        res = []
        for elem in (visit_txt_boxes(page_no, child) for child in node):
            if elem is None:
                continue
            elif isinstance(elem, list): # Flatten lists
                for subelem in elem:
                    res.append(subelem)
            else:
                res.append(elem)

        return res if len(res) > 0 else None
    else:
        return None


def pages(pdf_file, visit=visit_txt_boxes, password='', page_numbers=None, maxpages=0, caching=True, laparams=None):
    if laparams is None:
        laparams = LAParams(boxes_flow=None)
    
    with open(pdf_file, "rb") as fp:
        resource_manager = PDFResourceManager()
        device = MyPDFPageAggregator(resource_manager, laparams=laparams)
        interpreter = PDFPageInterpreter(resource_manager, device)
        pages = PDFPage.get_pages(fp, pagenos=page_numbers, maxpages=maxpages, password=password, caching=caching)
        for page_no, page in enumerate(pages):           
            interpreter.process_page(page)
            page_layout = device.get_result()
            page_child_obj = visit(page_no, page_layout)
            page_obj = {
                "page_no": page_no,
                "mediabox": page.mediabox,
                "items": page_child_obj,
            }
            yield page_obj


class MyPDFPageAggregator(PDFLayoutAnalyzer):
    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFLayoutAnalyzer.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)
        self.result = None
        return

    def receive_layout(self, ltpage):
        self.result = ltpage
        return

    def get_result(self):
        return self.result
    
    def begin_page(self, page, ctm):
        PDFLayoutAnalyzer.begin_page(self, page, ctm)
        self.cur_item = MyLTPage(self.cur_item.pageid, self.cur_item.bbox)


class MyLTPage(LTPage):
    def __init__(self, pageid, bbox, rotate=0):
        LTPage.__init__(self, pageid, bbox)
        return

    def group_objects(self, laparams, objs):
        for line in LTLayoutContainer.group_objects(self, laparams, objs):
            txt = line.get_text()
            if not txt.isspace():
                yield line
    

if __name__ == "__main__":   
    filename = sys.argv[1]
    obj = [p for p in pages(filename)]
    txt = json.dumps(obj, indent=2)
    print(txt)
