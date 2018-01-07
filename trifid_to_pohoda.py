"""
Converts a batch of invoices exported from Trifid Pokladna to Stormware Pohoda.

Usage:

```
python trifid_to_pohoda.py invoices_trifid.xml invoices_pohoda.xml
```

Both data formats are based on XML. A very rudimentary conversion is performed,
so data field in generaly may be missing.

The reason is that export from Trifid sometimes doesn't work properly, but at
least export to its native format works. Trifid allows to export a whole batch
of invoices in its own format. Export to Pohoda worked but only one invoice at
time. We want to be able to import the whole batch to Pohoda for accountant.

Tested with Trifid Pokladna 2016.

Trifid XML is in UTF-8 encoding with CRLF, while Pohoda in windows-1250 CRLF.

See also:
- https://gist.github.com/bzamecnik/cf0c0c76d0d5cbd4d5d9d67e7ff15b23
    Joins multiple single-file invoices in the StormWare Pohoda XML format
    to a single XML file.
"""

import argparse
from collections import OrderedDict

import xmltodict

def convert_price(price):
    return price.replace(',', '.')

def trifid_to_pohoda_invoice(trifid_invoice):
    """
    dict -> dict
    """
    # order of elements matters :/
    pohoda_inv = OrderedDict([
        ('@version', '2.0'),
        ('inv:invoiceHeader', OrderedDict([
            ('inv:invoiceType', 'issuedInvoice'),
            ('inv:number', OrderedDict([
                ('typ:ids', None),
                ('typ:numberRequested', '$INVOICE_ID')
            ])),
            ('inv:symVar', '$INVOICE_ID'),
            ('inv:date', '$DATE'),
            ('inv:dateTax', '$DATE_TAX'),
            ('inv:dateDue', '$DATE_DUE'),
            ('inv:accounting', OrderedDict([
                ('typ:ids', '311/604010')
            ])),
            ('inv:classificationVAT', OrderedDict([
                ('typ:classificationVATType', 'inland')
            ])),
            ('inv:text', 'Faktury vydané'),
            ('inv:partnerIdentity', OrderedDict([
                ('typ:address', OrderedDict([
                    ('typ:company', '$CUSTOMER_NAME'),
                    ('typ:division', None),
                    ('typ:city', None),
                    ('typ:street', None),
                    ('typ:zip', None),
                    ('typ:ico', None),
                    ('typ:dic', None)
                ]))
            ])),
            ('inv:paymentType', OrderedDict([
                ('typ:paymentType', 'draft')
            ])),
           ('inv:note', 'Načteno z XML')
        ])),
        ('inv:invoiceSummary', OrderedDict([
            ('inv:homeCurrency', OrderedDict([
                ('typ:priceNone', '$PRICE_NO_TAX'),
                ('typ:priceLow', '0'),
                ('typ:priceLowVAT', '0'),
                ('typ:priceHigh', '0'),
                ('typ:priceHighVAT', '0')
            ]))
        ]))
    ])
    data_pack_item = OrderedDict([
        ('dat:dataPackItem', OrderedDict([
            ('@id', '$DOCUMENT_ID'),
            ('@version', '2.0'),
            ('inv:invoice', pohoda_inv)
       ]))
    ])

    header = trifid_invoice['dokladHlavicka']
    invoice_data = header['fakturacniUdaje']
    invoice_id = invoice_data['cisloFaktury']

    data_pack_item['dat:dataPackItem']['@id'] = header['dokladCislo']['@KodRady'] + header['dokladCislo']['@Cislo']

    pohoda_header = pohoda_inv['inv:invoiceHeader']
    pohoda_header['inv:number']['typ:numberRequested'] = invoice_id
    pohoda_header['inv:symVar'] = invoice_id
    pohoda_header['inv:date'] = header['dokladVystaven']
    pohoda_header['inv:dateDue'] = invoice_data['datumSplatnosti']
    pohoda_header['inv:dateTax'] = invoice_data['datumDPH']

    pohoda_header['inv:partnerIdentity']['typ:address']['typ:company'] = \
        header['odberatel']['adresa']['firma']
    pohoda_header['inv:partnerIdentity']['typ:address']['typ:division'] = \
        header['odberatel']['adresa']['adresa1']

    trifid_footer =  trifid_invoice['dokladPata']
    pohoda_summary = pohoda_inv['inv:invoiceSummary']
    pohoda_summary['inv:homeCurrency']['typ:priceNone'] = \
        convert_price(trifid_footer['rozpisDPH']['sazbaNulova']['@Zaklad'])

    return data_pack_item

def convert_invoice_batch(trifid_dict):
    pohoda_invoices = xmltodict.parse("""<?xml version="1.0" encoding="Windows-1250"?>
    <dat:dataPack xmlns:dat="http://www.stormware.cz/schema/version_2/data.xsd"
        xmlns:inv="http://www.stormware.cz/schema/version_2/invoice.xsd"
        xmlns:typ="http://www.stormware.cz/schema/version_2/type.xsd"
        id="00001" application="" ico="" version="2.0" note="Import FA">
    </dat:dataPack>""")
    data_pack_item = pohoda_invoices['dat:dataPack']['dat:dataPackItem'] = []
    for inv in trifid_dict['trifid']['faktura']:
        pohoda_item = trifid_to_pohoda_invoice(inv)
        data_pack_item.append(pohoda_item['dat:dataPackItem'])
    return pohoda_invoices

def load_xml(path):
    with open(path, 'rb') as f:
        return xmltodict.parse(f)

def save_pohoda_xml(doc, path):
    with open(path, 'wb') as f:
        xmltodict.unparse(doc, output=f, pretty=True, encoding='Windows-1250', newl='\r\n')

def convert_invoice_batch_files(trifid_path, pohoda_path):
    trifid_dict = load_xml(trifid_path)
    pohoda_dict = convert_invoice_batch(trifid_dict)
    save_pohoda_xml(pohoda_dict, pohoda_path)

def main():
    parser = argparse.ArgumentParser(description='Converts XML with invoices from Trifid to Pohoda.')
    parser.add_argument('trifid_xml', metavar='TRIFID_XML')
    parser.add_argument('pohoda_xml', metavar='POHODA_XML')

    args = parser.parse_args()

    convert_invoice_batch_files(args.trifid_xml, args.pohoda_xml)

if __name__ == '__main__':
    main()
