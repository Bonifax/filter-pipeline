"""
Usage:
    tri_matrix.py -i <input> -f <filter_file> --filetype <outputfile_type> -o <output_directory>

Options:
    -i, --input     filepath to input file to be filtered (list of genes and species where gene is present).
Not a matrix file
    -o, --output    filepath to output directory
    -f, --filter    file to be used for filtering, first column must be the code used in input file.
Best if generated through tri_taxonomique.py
    --filetype      file type for the output matrix file : NEXUS or PHYLIP
    -h, --help      prints this help message
"""

import os
from docopt import docopt


def tri_matrix(arguments):
    #################################################################################
    # Pour verifier que le dossier d'output existe bien, le cree sinon.

    if not os.path.exists(arguments['<output_directory>']):
        os.makedirs(arguments['<output_directory>'])

    ##############################################################################
    entree = open(arguments["<input>"])
    filtre = open(arguments["<filter_file>"])

    if arguments["<outputfile_type>"] == "NEXUS":
        sortie_matrice = open(arguments["<output_directory>"] + "/matrix_filtered.nex", "w")
    elif arguments["<outputfile_type>"] == "PHYLIP":
        sortie_matrice = open(arguments["<output_directory>"] + "/matrix_filtered.phy", "w")
    else:
        print "ERROR, Filetype must be NEXUS or PHYLIP"

    fichier_dico_genes = open(arguments["<output_directory>"] + "/dico_genes.txt", "w")
    fichier_liste_all_genes = open(arguments["<output_directory>"] + "/all_genes.txt", "w")
    fichier_liste_nosingleton_genes = open(arguments["<output_directory>"] + "/liste_no_singleton_genes.txt", "w")
    fichier_parametres = open(arguments["<output_directory>"] + "/tri_matrix_parametres.txt", "w")

    ##############################################################################
    # Enregistrement des parametres :
    fichier_parametres.write("tri_matrix.py -i <input> -f <filter_file> -o <output_directory>\n")
    fichier_parametres.write(str(arguments))

    ##############################################################################

    # 1_ Dictionnaire matrice

    dico_filtre = {}
    for line in filtre:
        handle = line.strip().split("\t")
        dico_filtre[handle[0]] = handle[1:]

    dico = {}
    previous_gene_fam = ""
    previous_species = ""
    all_genes = set()
    no_singleton_genes = set()
    compte_lignes = 0

    for line in entree:
        handle = line.strip().split('\t')
        gene_fam = handle[0]
        species = handle[1].split('_')[0]
        all_genes.add(gene_fam)

        if species in dico_filtre:

            if gene_fam != previous_gene_fam:
                test = 0

            elif gene_fam == previous_gene_fam and species != previous_species and test < 1:
                if previous_species not in dico:
                    dico[previous_species] = set()
                if species not in dico:
                    dico[species] = set()
                dico[previous_species].add(previous_gene_fam)
                dico[species].add(gene_fam)
                no_singleton_genes.add(previous_gene_fam)
                no_singleton_genes.add(gene_fam)
                test += 1

            elif gene_fam == previous_gene_fam and species != previous_species and test >= 1:
                if species not in dico:
                    dico[species] = set()
                dico[species].add(gene_fam)
                no_singleton_genes.add(gene_fam)
                test += 1

            previous_gene_fam = gene_fam
            previous_species = species

        compte_lignes += 1
        if compte_lignes % 1000000 == 0:
            print "Nous en sommes a la ", compte_lignes, "ligne du fichier."
    print "le fichier contient", compte_lignes, "lignes au total."

    # On cree simplement ce fichier pour stocker le dico ##############################

    dico_texte = str(dico)
    retourligne_dico = dico_texte.replace("), ", "\n")
    tabulation_dico = retourligne_dico.replace(": set(", "\t")

    fichier_dico_genes.write(tabulation_dico)

    # Un fichier pour stocker tous les genes presents dans le fichier #################
    all_genes_texte = str(all_genes)
    retourligne_all_genes = all_genes_texte.replace(", ", "\n")
    all_genes_clean = retourligne_all_genes.replace("set(", "")
    all_genes_clean = all_genes_clean.replace(")", "")

    fichier_liste_all_genes.write(all_genes_clean)

    # Un fichier pour stocker toutes les familles non singletons ######################
    no_singleton_genes_texte = str(no_singleton_genes)
    retourligne_nosingleton_genes = no_singleton_genes_texte.replace(", ", "\n")
    no_singleton_genes_clean = retourligne_nosingleton_genes.replace("set(", "")
    no_singleton_genes_clean = no_singleton_genes_clean.replace(")", "")

    fichier_liste_nosingleton_genes.write(no_singleton_genes_clean)

    print "Il y avait", len(all_genes) - len(no_singleton_genes), \
        "genes presents chez une seule ou aucune espece selectionnee dans le fichier,"
    print "sur un total de", len(all_genes), "genes dans le fichier initial."

    #########################################################
    # 2_ Maitenant il faut creer la matrice a partir du dictionnaire

    # Pour ca on associe chaque gene non singleton a une position (coordonnee)
    liste_all_genes = list(all_genes)

    positions = dict()
    for index, element in enumerate(no_singleton_genes):
        positions[element] = index

    # ensuite on cree une liste de 0 et 1 pour chaque espece, avec
    # 0 aux positions des genes absents et 1 pour les genes presents chez l'espece

    matrice = {}
    nombre_especes = 0

    for espece, list_genes in dico.iteritems():
        new_line = ["0" for x in range(len(no_singleton_genes))]
        for gene_id in list_genes:
            indice = positions[gene_id]
            new_line[indice] = "1"
        matrice[espece] = new_line

        nombre_especes += 1

    print "Il y a", nombre_especes, "especes dans la matrice."

    # La matrice est creee, ici sous forme de dictionnaire,
    # donc il ne reste plus qu'a l'ecrire dans un fichier texte.
    # On va la formatter directement au format NEXUS en ajoutant une head et une tail.

    if arguments["<outputfile_type>"] == "NEXUS":
        sortie_matrice.write("#NEXUS\n")
        sortie_matrice.write("begin data;\n")
        sortie_matrice.write("dimensions ntax=%s nchar=%s;\n" % (nombre_especes, len(no_singleton_genes)))
        sortie_matrice.write("format interleave datatype=standard gap=-;\n")
        sortie_matrice.write("matrix\n")
    elif arguments["<outputfile_type>"] == "PHYLIP":
        sortie_matrice.write(str(nombre_especes) + "\t\t" + str(len(no_singleton_genes)) + "\n")


    for k, v in matrice.iteritems():
        my_new_line = dico_filtre[k][-1][:20].replace(" ", "_").replace("(", "_").replace(")", "_").replace(".",
                                                                                                            "_") + "\t" + "".join(
            v) + "\n"
        sortie_matrice.write(my_new_line)
    print "La matrice est faite"

    if arguments["<outputfile_type>"] == "NEXUS":
        sortie_matrice.write(";\n")
        sortie_matrice.write("\n")
        sortie_matrice.write("begin mrbayes;\n")
        sortie_matrice.write("lset rates=gamma coding=noabsencesites|nosingletonpresence;\n")
        sortie_matrice.write("mcmc;\n")
        sortie_matrice.write("end;\n")

    entree.close()
    filtre.close()
    sortie_matrice.close()
    fichier_liste_nosingleton_genes.close()
    fichier_liste_all_genes.close()
    fichier_dico_genes.close()
    fichier_parametres.close()


if __name__ == '__main__':
    arguments = docopt(__doc__)
    print arguments
    tri_matrix(arguments)
