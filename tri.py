"""
Usage:
    tri.py -i <input> -t <tax_file> --level <tax_level> --filetype <outputfile_type> -o <output_directory>

Options:
    -i, --input     filepath to raw input file with species to be filtered
    -o, --output    filepath to output directory, <output_directory>/taxo_filtered.txt is detined
to be used as filter in tri_matrix.py
    -t, --taxo      tax file of the species in the matrix file, that will be used to select the species to keep
    --level         integer, taxonomic level at which to filter the matrix
    --filetype      file type for the output matrix file : NEXUS or PHYLIP
    -h, --help      prints this help message
"""

from tri_taxonomique import tri_taxonomique
from tri_matrix import tri_matrix
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
    print arguments

# pour lancer tri_taxonomique, les arguments sont les memes donc il n'y a pas de probleme !
tri_taxonomique(arguments)

# par contre, tri_matrice n'utilise pas les memes arguments...
# il faut les ajouter dans le dico arguments{}
arguments['--filter'] = True
arguments["<filter_file>"] = arguments["<output_directory>"] + "/taxo_filtered.txt"
print arguments

tri_matrix(arguments)
