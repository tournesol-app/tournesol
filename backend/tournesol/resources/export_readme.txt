========================
Tournesol Public Dataset
========================

This archive contains the public dataset of the Tournesol project.

License
=======

All files are available under the terms of the Open Data Commons Attribution
License (ODC-By) v1.0.

See: https://opendatacommons.org/licenses/by/odc_by_1.0_public_text.txt

List of files
=============

comparisons.csv
---------------

Type: algorithm input.

This file contains all the public comparisons made by users. A comparison is
represented by a rating given by a user for a specific criteria and a pair of
videos.

users.csv
---------

Type: algorithm input.

This file contains the list of users who appear in the comparisons.csv file.

    trust score:

    The trust score represents how confident the algorithm is that the user is
    a human with an authentic behavior, using a single account on the platform.

    This score is calculated from the user's email address (trusted domain or
    not) and from the others users who vouched for them.

    Users with a trust score of 0 (i.e. users without a trusted email and who
    haven't been vouched for by trusted users) can influence together at most
    10% of the total collaborative evaluation of a video.

individual_criteria_scores.csv
------------------------------

Type: algorithm output.

This file contains the individual scores computed by the algorithm for each
criterion, rated by a user for a given video.

    score:

    TO DESCRIBE. How is it built? What does it influence?

    voting right:

    TO DESCRIBE. How is it built? What does it influence?
