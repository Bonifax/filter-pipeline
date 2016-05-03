"""
Usage:
    tri_taxonomique.py -i <input> -t <tax_file> --level <tax_level> -o <output_directory>

Options:
    -i, --input     filepath to raw input file with species to be filtered
    -o, --output    filepath to output directory, <output_directory>/taxo_filtered.txt is detined
to be used as filter in tri_matrix.py
    -t, --taxo      tax file of the species in the matrix file, that will be used to select the species to keep
    --level         integer, taxonomic level at which to filter the matrix
    -h, --help      prints this help message
"""
import os
from docopt import docopt


def tri_taxonomique(arguments):
    #################################################################################
    # Pour verifier que le dossier d'output existe bien, le cree sinon :

    if not os.path.exists(arguments['<output_directory>']):
        os.makedirs(arguments['<output_directory>'])

    ##############################################################################
    tax_level = int(arguments["<tax_level>"])

    entree = open(arguments["<input>"])
    taxo = open(arguments["<tax_file>"])
    sortie_taxo = open(arguments["<output_directory>"] + "/taxo_filtered.txt", "w")
    sortie_liste = open(arguments["<output_directory>"] + "/grouped_species_filtered.txt", "w")
    fichier_dico_count = open(arguments["<output_directory>"] + "/dico_count.txt", "w")
    fichier_dico_taxo = open(arguments["<output_directory>"] + "/dico_taxo_code.txt", "w")
    fichier_parametres = open(arguments["<output_directory>"] + "/tri_taxonomique_parametres.txt", "w")

    ##############################################################################
    # Enregistrement des parametres :
    fichier_parametres.write("tri_taxonomique.py -i <input> -t <tax_file> --level <tax_level> -o <output_directory>\n")
    fichier_parametres.write(str(arguments))

    ##############################################################################

    dico_taxo = {}  # organise tq : dico_taxo = {'eukaryote' : [[123, 'ABCD', 'Lorem ipsum', 'eukaryote', 'metazoa', ...], [ ...]] , [[],[]]}
    dico_taxo_codealpha = {}  # organise tq : dico_taxo_codealpha = {'ABCD' : [123, 'ABCD', 'Lorem ipsum', 'eukaryote', 'metazoa', ...], 'EFGH4 : [...]}

    # On fait un dictionnaire avec en clef la valeur du niveau taxo choisi et en valeurs toute la ligne (sous forme de liste)
    for line_taxo in taxo:
        handle_taxo = line_taxo.strip().split("\t")
        if len(handle_taxo) > (tax_level + 1):
            level_taxo = handle_taxo[tax_level]
        elif " " in handle_taxo[-2]:
            level_taxo = handle_taxo[-3]
        else:
            level_taxo = handle_taxo[-2]

        if level_taxo not in dico_taxo:
            dico_taxo[level_taxo] = []
        dico_taxo[level_taxo].append(handle_taxo)
        dico_taxo_codealpha[handle_taxo[0]] = handle_taxo

    for k, v in dico_taxo_codealpha.iteritems():
        new_line = k + "\t" + "\t".join(v) + "\n"
        fichier_dico_taxo.write(new_line)

    for k, v in dico_taxo.iteritems():
        new_line = k + "\t" + "\n\t\t\t".join(map("\t".join, v)) + "\n"
        sortie_liste.write(str(new_line))

    print "Le rangement des especes est fait"
    print "Maintenant filtrons :"

    # Dictionnaire pour stocker tous les genes presents par espece
    dico_spec_genes = {}
    previous_gene_fam = ""
    previous_species = ""
    compte_lignes = 0

    for line in entree:
        handle = line.strip().split('\t')
        gene_fam = handle[0]
        species = handle[1].split('_')[0]

        if gene_fam != previous_gene_fam:
            test = 0

        elif gene_fam == previous_gene_fam and species != previous_species and test < 1:
            if previous_species not in dico_spec_genes:
                dico_spec_genes[previous_species] = set()
            if species not in dico_spec_genes:
                dico_spec_genes[species] = set()
            dico_spec_genes[previous_species].add(previous_gene_fam)
            dico_spec_genes[species].add(gene_fam)
            test += 1

        elif gene_fam == previous_gene_fam and species != previous_species and test >= 1:
            if species not in dico_spec_genes:
                dico_spec_genes[species] = set()
            dico_spec_genes[species].add(gene_fam)
            test += 1

        previous_gene_fam = gene_fam
        previous_species = species

        compte_lignes += 1
        if compte_lignes % 500000 == 0:
            print "Nous en sommes a la ", compte_lignes, "ligne du fichier"

    # En realite seule la taille du genome nous interesse ici, donc on peut simplifier :
    dico_count = {}
    for k, v in dico_spec_genes.iteritems():
        dico_count[k] = len(v)

    # creation d'un fichier pour stocker dico_count :
    for k, v in dico_count.iteritems():
        my_new_line = k + "\t" + str(v) + "\n"
        fichier_dico_count.write(my_new_line)

    dico_pour_tri = {}
    for k, v in dico_taxo.iteritems():
        dico_pour_tri[k] = {}
        for liste_taxo in v:
            dico_pour_tri[k][liste_taxo[0]] = dico_count[liste_taxo[0]]

    filtered_dico = {}
    for k, v in dico_pour_tri.iteritems():
        max_code = max(v.iterkeys(), key=(lambda key: v[key]))
        if dico_count[max_code] > 400:
            filtered_dico[max_code] = dico_taxo_codealpha[max_code]

    for k, v in filtered_dico.iteritems():
        my_new_line = "\t".join(v) + "\n"
        sortie_taxo.write(my_new_line)

    """

    # preparation du dictionnaire permettant de selectionner uniquement les especes retenues
    dico_filtre = {}

    """

    entree.close()
    taxo.close()
    sortie_liste.close()
    sortie_taxo.close()
    fichier_dico_count.close()
    fichier_dico_taxo.close()
    fichier_parametres.close()


if __name__ == '__main__':
    arguments = docopt(__doc__)
    print arguments
    tri_taxonomique(arguments)
