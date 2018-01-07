# Convet XML invoices Trifid to Pohoda

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

## Validation

```
./validate_pohoda.sh invoices_pohoda.xml
```
