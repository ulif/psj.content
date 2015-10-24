# normalize terms
#
import dinsort
import gzip
import unittest


INFILE_PATH = "identifier.txt.gz"
OUTFILE_PATH = "terms.txt"

# how are numbers and terms separated in files?
SEPARATOR = "&&"


def normalize_list(inpath, outpath, separator):
    """Turn a list of terms into normalized form.

    For instance::

        (123)&&Term1
        (124)&&Term Number 2

    will become::

        term1(123)&&Term1
        term number 2(124)&&Term Number 2

    etc. Here the `separator` string is "&&" in both,
    input and output file.
    """
    print("Opening %s for reading..." % inpath)
    with gzip.open(inpath, "r") as infile:
        with open(outpath, "w") as outfile:
            for cnt, line in enumerate(infile.readlines()):
                if cnt % 100000 == 0:
                    # ping back every 10**6th entry
                    print("Done: %s entries" % cnt)
                id_num, term = line.strip().split(separator, 1)
                term = term.decode("utf-8")
                normalized = dinsort.normalize("%s(%s)" % (term, id_num))
                out_term = "%s%s%s\n" % (normalized, separator, term)
                outfile.write(out_term.encode("utf-8"))
    print("Done. Written results to %s" % outpath)


class TestNormalize(unittest.TestCase):
    # run tests with:: `python -m unittest normalize`

    def test_foo(self):
        assert True is False


if __name__ == "__main__":
	normalize_list(INFILE_PATH, OUTFILE_PATH, SEPARATOR)
