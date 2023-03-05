========================
Tournesol Public Dataset
========================

This archive contains the public dataset of the Tournesol project.

License
=======

All files are available under the terms of the Open Data Commons Attribution
License (ODC-By) v1.0.

Human-readable summary
----------------------

You are free:

- To share: To copy, distribute and use the database.
- To create: To produce works from the database.
- To adapt: To modify, transform and build upon the database.

As long as you:

- Attribute: You must attribute any public use of the database, or works
  produced from the database, in the manner specified in the license. For any
  use or redistribution of the database, or works produced from it, you must
  make clear to others the license of the database and keep intact any notices
  on the original database.

Full license text
-----------------

See the `LICENSE.txt` file distributed in this archive.

See the online version at https://opendatacommons.org/licenses/by/odc_by_1.0_public_text.txt

List of files
=============

comparisons.csv
---------------

This file contains all the public comparisons made by users. A comparison is
represented by a rating given by a user for a specific criterion and a pair of
videos.

List of columns:


- public_username:

  The username of the user who submitted the comparison.

- video_a:

  One of the two video being compared. If the score is negative, it indicates
  that the user prefers video_a against video_b.

- video_b:

  The second video being compared. If the score is positive, it indicates that
  the user prefers video_b against video_a.

- criteria:

  The name of the criterion for the comparison. The main criterion is
  "largely_recommended". Other criteria (for example "reliability", "pedagogy",
  or "importance") are optional. Users can choose to compare two video on any
  of the criteria.

- score:

  The score is an integer between -10 and +10. Negative values indicate that
  the user considers the video_a better, and positive values indicate that
  they prefer the video_b. A score of 0 or close to 0 means that they find the
  two videos similar.

- week_date:

  The date of the Monday of the week during which the comparison was first
  submitted. Note that it is possible that the comparison is updated at a later
  time, but it is rather rare.

users.csv
---------

This file contains the list of users who appear in the comparisons.csv file and
the trust scores evaluated by Tournesol based on the two mechanisms:
  1. trusted domain for email addresses
  2. vouching system

List of columns:


- public_username:

  The public username of the user.

- trust_score:

  This field is computed by Tournesol's algorithms. The trust score represents
  how confident the algorithm is that the user is a human with an authentic
  behavior and using a single account. Currently this score is calculated based
  on a list of trusted email domains. Email domains are trusted if there are
  reasons to believe that this domain only provides a single email address per
  person. Secondly the trust scores also take into account vouches that any
  user can choose to give to another account if they trust that the user
  controlling the account is authentic and controls a single account. Trust
  scores influence the computation of voting rights (see file
  individual_criteria_scores.csv).

individual_criteria_scores.csv
------------------------------

This file contains the individual scores computed by the algorithm for each
criterion, rated by a user for a given video.

List of columns:


- public_username:

  The username of the user who has included the video in their comparisons

- video:

  The ID of the video on YouTube.

- criteria:

  The name of the criterion on which the score applies.

- score:

  This field is computed by Tournesol's algorithms. The score is a number
  between -100.0 and +100.0. Individual scores are computed based on all the
  comparisons submitted by a user. Additionally individual scores of all users
  are globally scaled such that they are meaningfully comparable and can be
  aggregated.

- uncertainty:

  This field is computed by Tournesol's algorithms. It should represent the 
  uncertainty on the score value. For more detail, check out the algorithms
  implementation or the paper which describe them
  https://arxiv.org/abs/2211.01179

- voting_right:

  This field is computed by Tournesol's algorithms. The voting right is a
  number between 0.0 and 1.0 used to compute collective scores. It is assigned
  to each user depending on their trust scores (see file users.csv) and on how
  many users have rated the same video. This is done in such a manner that if a
  large number of users with low trust scores compare the same video, then they
  will all receive a very small voting right, but if the number of users with
  low trust score is not more than 10% of all the users that rated the same
  video then they will receive a full voting right.

collective_criteria_scores.csv
------------------------------

This file contains the collective scores computed by the algorithm for each
criterion.

List of columns:


- video:

  The ID of the video on YouTube.

- criteria:

  The name of the criterion on which the score applies.

- score:

  This field is computed by Tournesol's algorithms. This score is obtained by
  considering all the individual scores on the same video and criterion. With a
  lot of contributors these scores should be close to the median of their
  individual scores. With a small number of contributors, this score would be
  reduced towards 0 such that it is not possible for a small number of users to
  give a very high collective score on a video.

- uncertainty:

  This field is computed by Tournesol's algorithms. It should represent the 
  uncertainty on the score value. For more detail, check out the algorithms
  implementation or the paper which describe them
  https://arxiv.org/abs/2211.01179