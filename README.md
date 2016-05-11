# filter-pipeline
A Python pipeline that can be used to convert data from a database such as HOGENOM7 into a matrix file that can be used by phylogeny softwares such as biphy, IQTRee and RAxML.

tri_taxonomique.py allows to filter species according to a selected taxonomic level, thanks to a taxonomic file provided by the user.

tri_matrix.py uses the output from tri_taxonomique.py and the original gene families file to create a matrix file in NEXUS ou PHYLIP format.

tri.py allows to automatically use the two functions detailed above one after the other.

Taxonomie_propre_sorted.txt is the complete file used for the analysis I performed. It was generated thanks to NCBI Refseq informations and homogenized and filtered manually.

echantillon_500000.txt is a sample (500.000 first lines) from the complete file used in the analysis. It was generated directly from the HOGENOM7 database.

