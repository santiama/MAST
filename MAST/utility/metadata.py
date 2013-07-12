from MAST.utility import MASTObj
from MAST.utility import MASTError

ALLOWED_KEYS = {
                'metafile' : (str, 'metadata.txt', 'Metadata file name')
               }


class Metadata(MASTObj):
    """Class to handle the metadata file
        Fields are composed of a keyword and a value, separated by a '='.
    """
    def __init__(self, **kwargs):
        MASTObj.__init__(self, ALLOWED_KEYS, **kwargs)

    def write_data(self, keyword, data):
        """Writes a keyword and it's associated data to the metafile"""
        with open(self.keywords['metafile'], 'a') as metafile:
            metafile.write('%s = %s\n' % (keyword, data))

    def search_data(self, keyword):
        """Searches the file for a keyword, and if found returns the line number
            and data for that keyword.
        """
        line_number = None
        data = None

        with open(self.keywords['metafile'], 'r') as metafile:
            for n, line in enumerate(metafile):
                if keyword in line:
                    line_number = n
                    data = line.split('=')[1].strip()
                    break

        return line_number, data

    def read_data(self, keyword):
        """Searches the metadata file for a specific keyword and returns the
            data.
        """
        line_number, data = self.search_data(keyword)
        return data
 
    def clear_data(self, keyword):
        """Removes the specified data and keyword from the file.
            This is inefficient, as what we do is basically reading in the file
            then iterating through the file, do if..else check, clear the file,
            then re-write it.

            But it works!
        """
        line_number, data = self.search_data(keyword)

        data = list()
        with open(self.keywords['metafile'], 'r') as metafile:
            for n, line in enumerate(metafile):
                if n == line_number:
                    pass
                else:
                    data.append(line)

        self.clear_file()
        for line in data:
            keyword, data = line.split('=')
            self.write_data(keyword, data)

    def clear_file(self):
        """Empties the metafile"""
        open(self.keywords['metafile'], 'w').close()

