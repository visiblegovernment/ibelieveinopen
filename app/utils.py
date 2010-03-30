import csv

# utilities used by various scripts.

class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.encoding = encoding

    def next(self):
        row = self.reader.next()
        return [unicode(s, self.encoding) for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.writer = csv.writer(f, dialect=dialect, **kwds)
        self.encoding = encoding

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
