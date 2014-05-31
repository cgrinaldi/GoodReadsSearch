# Good Reads Search

## Overview
search_library.py uses the GoodReads API to search the Montgomery County library website (http://www.montgomerycountymd.gov/library/) for books that I have placed in my "to_search" shelf. If a book if found, it is placed in the "to_library" shelf, awaiting additional tagging based on the book. If the book is not located, it is placed in the "not_library" shelf.

## Notes
* This code requires a GoodReads API key
* While specific to the Montgomery County library system, it could probably be extended to other libraries, depending on how they output the results of searches, and if it is possible to search via url parameters.
