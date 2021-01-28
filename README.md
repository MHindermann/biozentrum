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
5. Manual deduplication removes an additional 1720 records; the remaining 10115 records are saved as `refined/deduplicated.enlx` resp. `refined/deduplicated.xml`.
6. The Endnote XML export format is unwieldy; more importantly, it is not correctly parsed by OpenRefine. We can amend this by running `_Utility.xml2json(DIR + "/refined/deduplicated.xml", DIR + "/refined/deduplicated.json")`; the output is saved as `refined/deduplicated.json`.
7. Declutter `deduplicated.json` in OpenRefine (remove empty columns, adapt column names, etc.); export data in decade-slices as `.csv` to `refined/20210128` and convert to `.json`.

## Word cloud based on keywords
1. Due to the deduplication process different kinds of keywords can no longer be distinguished. 
2. We can get an approximation of a word cloud by means of a histogram. Since the given keywords are messy (different ways of spelling one term, capitalization, etc.) we need to clean them first. To create a histogram for arbitrary slices of records (here the slices by decade saved in `refined/20210128`) do this:
   ```
   _Keywords.slices2histogram(DIR + "/refined/20210128/deduplicated_1971-1981.json",
                           DIR + "/refined/20210128/deduplicated_1981-1991.json",
                           DIR + "/refined/20210128/deduplicated_1991-2001.json",
                           DIR + "/refined/20210128/deduplicated_2001-2011.json",
                           DIR + "/refined/20210128/deduplicated_2011-2021.json",
                           save_path=DIR + "/refined/20210128/histogram_1971-2021.json")
   ```
Preleminary results can be found here: `refined/20210128/histogram_summary.xlsx`. Not yet implemented:  

3. So far artifacts such as "article", "priority journal", etc. have not been removed from the keywords.  
4. We might also want to unify the singular and plural of one and the same keyword.  
5. We might also want to map each keyword to a keyword from a controlled vocabulary in order to prevent semantic duplications. However, this is more involved due to the prevalence of compound keywords such as "Mechanistic Target of Rapamycin Complex 2/genetics/*metabolism" which require some more care. So this step is skipped for now.
