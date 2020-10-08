# pdf2mldata
This tool can extract text with and with and without highlights from PDF documents. Thus simple and easy to do annotations in PDF documents can be used to create binary labeled data.


## Example
Extracting data from [data.pdf](doc/data.pdf) gives the following output. Notice the ```tag``` property with values ```Highlight``` and ```None``` which can be used as labels.


```json
[
  {
    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum consequat mi quis pretium semper. Proin luctus orci ac neque venenatis, quis commodo dolor posuere. Curabitur dignissim sapien quis cursus egestas. ",
    "tag": "Highlight",
    "page_no": 0,
    "bbox": [
      52.6869,
      692.383,
      555.694,
      736.353
    ]
  },
  {
    "text": "Donec blandit auctor arcu, nec pellentesque eros molestie eget. In consectetur aliquam hendrerit. Sed cursus mauris vitae ligula pellentesque, non pellentesque urna aliquet. Fusce placerat mauris enim, nec rutrum purus semper vel. Praesent tincidunt neque eu pellentesque pharetra. Fusce pellentesque est orci.",
    "tag": "None",
    "page_no": 0,
    "bbox": [
      56.8,
      624.908,
      552.8199999999998,
      678.308
    ]
  },
  ...
```

This can be loaded into a Pandas DataFrame as follows:

```python
import pandas as pd
df = pd.read_json('data.pdf.json')
```

## Setup
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

## Usage
```bash
$ python3 pdf2mldata.py <pdf_dir> <out_dir>
```


## Dependencies
* [pdfannots](https://github.com/0xabu/pdfannots), commit ```abf1664```
  * It is not PyPI package, hence included in subfolder.

## Other
* [pdf-annotate](https://github.com/plangrid/pdf-annotate) is useful for adding rectangle annotations to the PDF document using the extracted bounding box during inference.