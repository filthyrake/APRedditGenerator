# APRedditGenerator
Scans FITS metadata and generates template for easy copy/pasting of acquisition info to Reddit and a CSV for Astrobin

Yes I know I should add a requirements file for you all, but this one is pretty simple.  It scans the LIGHTS directory from wherever you run this from and it scrapes the headers from your FITS files for relevant data to create a really handy text file you can just copy/paste from (or at least that's what I do) when I share my astro images to reddit.  Currently it is configured for the gear I have, but it is pretty easily modifiable for anyone's.

Unfortunately you cannot upload images to Astrobin using their API (boy I wish) or really via any other automated method.  That said, what you CAN do is use a CSV file to upload your acquisition information at least.  So this script also attempts to generate a CSV file that will work for that (this part is NOT TESTED).
