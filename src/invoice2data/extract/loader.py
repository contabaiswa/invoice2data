"""
This module abstracts templates for invoice providers.

Templates are initially read from .yml files and then kept as class.
"""

import os
import yaml
import pkg_resources
from collections import OrderedDict
import logging
from .invoice_template import InvoiceTemplate
import codecs
import chardet

logging.getLogger("chardet").setLevel(logging.WARNING)

DROPBOX_PATH = os.getenv('dropbox')
templates_filepath = DROPBOX_PATH + "\\shared settings\\templates" 


# borrowed from http://stackoverflow.com/a/21912744
def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """load mappings and ordered mappings

    loader to load mappings and ordered mappings into the Python 2.7+ OrderedDict type,
    instead of the vanilla dict and the list of pairs it currently uses.
    """

    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )

    return yaml.load(stream, OrderedLoader)


def read_templates(filepath=None, filename=None):
    """
    Load yaml templates from template filepath. Return list of dicts.

    Use built-in templates if no filepath is set.

    Parameters
    ----------
    filepath : str
        user defined filepath where they stores their files, if None uses built-in templates
        can either be a directory or a single template.yml filepath

    Returns
    -------
    output : Instance of `InvoiceTemplate`
        template which match based on keywords

    Examples
    --------

    >>> read_template("home/duskybomb/invoice-templates/")
    InvoiceTemplate([('issuer', 'OYO'), ('fields', OrderedDict([('amount', 'GrandTotalRs(\\d+)'),
    ('date', 'Date:(\\d{1,2}\\/\\d{1,2}\\/\\d{1,4})'), ('invoice_number', '([A-Z0-9]+)CashatHotel')])),
    ('keywords', ['OYO', 'Oravel', 'Stays']), ('options', OrderedDict([('currency', 'INR'), ('decimal_separator', '.'),
    ('remove_whitespace', True)])), ('template_name', 'com.oyo.invoice.yml')])

    After reading the template you can use the result as an instance of `InvoiceTemplate` to extract fields from
    `extract_data()`

    >>> my_template = InvoiceTemplate([('issuer', 'OYO'), ('fields', OrderedDict([('amount', 'GrandTotalRs(\\d+)'),
    ('date', 'Date:(\\d{1,2}\\/\\d{1,2}\\/\\d{1,4})'), ('invoice_number', '([A-Z0-9]+)CashatHotel')])),
    ('keywords', ['OYO', 'Oravel', 'Stays']), ('options', OrderedDict([('currency', 'INR'), ('decimal_separator', '.'),
    ('remove_whitespace', True)])), ('template_name', 'com.oyo.invoice.yml')])
    >>> extract_data("invoice2data/test/pdfs/oyo.pdf", my_template, pdftotext)
    {'issuer': 'OYO', 'amount': 1939.0, 'date': datetime.datetime(2017, 12, 31, 0, 0), 'invoice_number': 'IBZY2087',
     'currency': 'INR', 'desc': 'Invoice IBZY2087 from OYO'}

    """

    output = []
    if not filepath:
        filepath = templates_filepath

    if filepath[-4:] == '.yml':
        name = filepath[:-4] 
        filepath = filepath.replace("/", "\\")
        if "\\" not in filepath:
             filepath = f"{templates_filepath}\\" + filepath
        with open(filepath, "rb") as f:
                    encoding = chardet.detect(f.read())["encoding"]
        with codecs.open(
            filepath, encoding=encoding
        ) as template_file:
            tpl = ordered_load(template_file.read())
        tpl["template_name"] = filepath.split("\\")[-1]

        # # Test if all required fields are in template:
        # assert "keywords" in tpl.keys(), "Missing keywords field."

        # Keywords as list, if only one.
        if type(tpl["keywords"]) is not list:
            tpl["keywords"] = [tpl["keywords"]]

        output.append(InvoiceTemplate(tpl))
    else:
        for path, subdirs, files in os.walk(filepath):
            for name in sorted(files):
                if name.endswith(".yml"):
                    with open(os.path.join(path, name), "rb") as f:
                        encoding = chardet.detect(f.read())["encoding"]
                    with codecs.open(
                        os.path.join(path, name), encoding=encoding
                    ) as template_file:
                        tpl = ordered_load(template_file.read())
                    tpl["template_name"] = name

                    # # Test if all required fields are in template:
                    # assert "keywords" in tpl.keys(), "Missing keywords field."

                    # Keywords as list, if only one.
                    if type(tpl["keywords"]) is not list:
                        tpl["keywords"] = [tpl["keywords"]]

                    output.append(InvoiceTemplate(tpl))
    return output
