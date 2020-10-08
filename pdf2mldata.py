from pdfannots import pdfannots
import extract_text
import sys
import json
import pathlib
import collections


BBoxWrap = collections.namedtuple('BBoxWrap', 'x0 y0 x1 y1')


def anno_to_dict(a):
    return {
        "pageno": a.page.pageno,
        "tagname": a.tagname,
        "bbox": a.rect,
        #"boxes":  a.boxes,
        "author": a.author,
        "text": a.text
    }


def res_to_dict(txt, tag, pageno, bbox):
    return {
        'text': txt,
        'tag': tag,
        'page_no': pageno,
        'bbox': bbox
    }


def load_data(filename):
    with open(filename, 'rb') as fp:
        tmp = pdfannots.process_file(fp, False)
        data_anno = [anno_to_dict(a) for a in tmp[0]]
    
    data_txt = [p for p in extract_text.pages(filename)]
    return (data_anno, data_txt)


def merge_data(data_anno, data_txt):
    res = []
    overlap_threshold = 0.5
    for page in data_txt:
        page_anno = [a for a in data_anno if a['pageno'] == page['page_no']]
        for anno in page_anno: 
            res.append(res_to_dict(anno['text'], anno['tagname'], page['page_no'], anno['bbox']))

        for item in page['items']:
            txt_bbox = BBoxWrap(*item['bbox'])
            anno_overlaps = [pdfannots.boxhit(txt_bbox, anno['bbox']) > overlap_threshold for anno in page_anno]
            if not any(anno_overlaps):
                res.append(res_to_dict(item['text'], 'None', page['page_no'], txt_bbox))
    
    res.sort(key=lambda item: item['bbox'][1], reverse=True)
    res.sort(key=lambda item: item['page_no'])
    return res


def pdf_to_samples(in_fn):
    data_anno, data_txt = load_data(in_fn)
    res = merge_data(data_anno, data_txt)
    return res


def process_pdf_file(in_f, out_f):
    res = pdf_to_samples(in_f)
    with open(out_f, 'w') as fp:
        json.dump(res, fp, indent=2)


def process_dir(input_dir_txt, output_dir_txt):
    input_dir = pathlib.Path(input_dir_txt)
    assert(input_dir.is_dir())
    output_dir = pathlib.Path(output_dir_txt)
    assert(output_dir.is_dir())

    for input_file in input_dir.glob('**/*.pdf'):
        rel = input_file.relative_to(input_dir)
        print('{:<90}'.format(str(rel)), end='')

        out_file = output_dir.joinpath(rel).with_suffix('.pdf.json')
        if not out_file.parent.is_dir():
            out_file.parent.mkdir(parents=True)
            
        if out_file.is_file():
            print('Skipping')
        else:
            print('Processing')
            process_pdf_file(str(input_file), str(out_file))


if __name__ == "__main__": 
    process_dir(sys.argv[1], sys.argv[2])
