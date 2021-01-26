# Biozentrum

## Metadata harvesting
### Scopus / 20210125
1. Search `ALL ( basel )  AND  ( LIMIT-TO ( AF-ID ,  "Biozentrum, Universität Basel"   60015184 ) ) `, 5863 hits
2. Export as `raw/scopus_x-y.ris` in slices of ~2000 records with all available information.

### Web of Science / 20210125
1. Search ` ADDRESS: (biozentrum)
Refined by: ORGANIZATIONS-ENHANCED: ( UNIVERSITY OF BASEL ) `, 5625 hits
2. Export as `raw/savedrecs_x-y.ciw` in slices of 500 records with all available information ("Full record and available references").

### PubMed / 20210125
1. Search ` biozentrum `, 5626 hits
2. Save as `pubmed-biozentrum-set_x-y.txt` via PubMed format option. `.csv` export fails.

## Deduplication with Endnote
1. Import Scopus files (reference manager option).
2. Import Web of Science files (via multi-filter option).
3. Import PubMed files (via multi-filter option).
4. Run "find duplicates", remove 5803 records. But a quick manual check reveals that many duplicates have been missed.
5. https://guides.library.illinois.edu/openrefine/duplicates