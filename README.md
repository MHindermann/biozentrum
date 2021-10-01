# Data collection and preprocessing for Biozentrum jubilee publication

Bibliometric data collection and preprocessing for "50 years of research at the Biozentrum" on p. 40 of the 50 years Biozentrum Life Sciences jubilee publication available at https://www.biozentrum.unibas.ch/de/about/biozentrum-auf-einen-blick/50-year-jubilee.

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

## Word cloud based on keywords / 20210128
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

## Word cloud based on title + abstract / 20210209
1. We build histograms based on title and, if available, abstract based on the slices by decade saved in 
   `/refined/20210128`. In order to take into account
   distributed 
   terms, we try out monograms, bigrams and trigrams. For example like so for a bigram over all five decades:
   ```
   _Data.save_text2ngram(DIR + "/refined/20210128/deduplicated_1971-1981.json",
                         DIR + "/refined/20210128/deduplicated_1981-1991.json",
                         DIR + "/refined/20210128/deduplicated_1991-2001.json",
                         DIR + "/refined/20210128/deduplicated_2001-2011.json",
                         DIR + "/refined/20210128/deduplicated_2011-2021.json",
                         n=2,
                         save_path=DIR + "/refined/20210209/2gram_1971-2021.json")
   ```
   The n-grams are saved under `/refined/20210209`.
2. The n-grams are more or less clean (no stopwords, some administrative terms have been excluded, see `_Data.
   text2ngram` 
   for details).
3. A summary of all n-grams over all decades can be found here: `/refined/20210209/n-grams_summary.xlsx`   

## Add "Biocenter" papers / 20210223
1. Papers with a non-"Biozentrum" affiliation were skipped in the first metadata harvesting run. It seems that this approach misses out on too many papers, so we amend the query at PubMed:  
`(Biozentrum[ad] OR Center for molecular life sciences[ad] OR Biocenter[ad]) AND (Basel[ad] OR Bâle[ad] OR Basle[ad])`  
   This search yields 3763 results and is exported as `/refined/20210223/pubmed-biocenter-set_1974-2021.txt`.
   
2. We import these results into `/refined/deduplicated.enlx` with Endnote but discard duplicates to the effect of adding 870 new papers. We then performed a semi-manual deduplication, removing 250+ duplicates. The result is saved as `/refined/20210223/deduplicated.enlx` and contains 10843 items (as compared to the 10115 previous items)

3. Unfortunately, the Endnote XML-export does not work (again); `_Utility.xml2json` bugs out and I cannot fix it. So we imported the Endnote data into Citavi and exported from there as `/refined/20210223/deduplicated_citavi.xml`; this is then converted to `/refined/20210223/deduplicated_citavi.json`.

## Redo n-grams for more complete metadata / 20210301
1. Slice `/refined/20210223/deduplicated_citavi.json` into 5 files sorted by decade with `_Data.extract_by_decade` and save in `/refined/20210301/metadata`.
2. Create histograms of all combinations of: n-gram (0 < n < 4), files in decades, title versus title + abstract with `_Data.super_ngram`. The 3 * 5 * 2 = 30 files are saved in `/refined/20210301/ngrams`. The n-grams are no longer case-sensitive.
3. A summary of the results can be found at `/refined/20210301/summary.xlsx`

## Add normalized histograms of n-grams / 20210315
1. Let a histogram of n-grams be normalized iff there is at most 1 occurrence per n-gram per sample (i.e., text, based on title or abstract and title), implemented with `_Data.super_norm_ngram`. Normalization should take care of the bias that some n-grams might be mentioned multiple times in a single abstract (same for title albeit this probably rarely ever happens).
2. The output is saved in `/refined/20210315/norm_ngrams`; a summary is available at `/refined/20210315/summary_normalized.xlsx`.
