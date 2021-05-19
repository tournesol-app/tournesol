import React from 'react';

import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    minWidth: '420px',
  },
}));

export default () => {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <h1>Privacy Policy</h1>

      <h3>Who we are</h3>
      <p>
        Our website address is <a href="https://tournesol.app">https://tournesol.app</a>
      </p>

      <h3>What personal data Tournesol collects and why</h3>
      <h4>Ratings</h4>
      <p>
        Our mission is to identify top videos of public utility by eliciting contributors'
        judgements on content quality.
        To do so, Tournesol collects the data provided
        by the contributors in the <a href="https://tournesol.app/rate">rate page</a>.
        To estimate how much thoughts have been put in
        contributors’ judgments, and thus how much their data should be trusted, Tournesol also
        measures the contributors’ response time and Tournesol records the slider movements.
        In their contributor page, contributors can remove this recording of the slider movements.
        We believe that such data have a huge scientific and ethical value and will motivate
        research on more robustly beneficial recommendations for humanity.
      </p>

      <h4>Search</h4>
      <p>
        Even if the contributor is not logged in, Tournesol collects the parameters of their
        search queries in order to better understand most users’ needs. We believe that such
        data can also have a scientific and ethical value to help make recommendation systems
        more robustly beneficial to humanity.
      </p>

      <h4>User profile</h4>
      <p>
        In order to distinguish different contributors’ expertise, Tournesol asks contributors
        to certify their emails, to report their fields of expertise and to link to their public
        profiles. We believe that such data have an important scientific and ethical value and
        will help make recommendation systems more robustly beneficial to humanity.
      </p>

      <h4>Comments</h4>
      <p>
        When contributors leave comments on the site, Tournesol records the data in the comment
        forms, and the metadata like publication time to help spam detection. The data is also
        labeled with the contributors’ Tournesol profile. We believe that such data have an
        important scientific value and will help make recommendation systems more robustly
        beneficial to humanity.
      </p>

      <h4>Contact form</h4>
      <p>
        There is no contact form. If you need to contact us, please email
        <a href="mailto:tournesol.application@gmail.com">tournesol.application@gmail.com</a>.
      </p>

      <h4>Cookies</h4>
      <p>
        If a contributor has an account and logs in to this site, Tournesol will set a
        temporary cookie to determine if their browser accepts cookies. This cookie contains
        no personal data and is discarded when the contributor closes their browser.
      </p>
      <p>
        When the contributor logs in, Tournesol will also set up several cookies to save their
        login information and their screen display choices. Login cookies last for two days,
        and screen options cookies last for a year. If the contributor selects “Remember Me”,
        their login will persist for two weeks. If they log out of their account, the login
        cookies will be removed.
      </p>
      <p>
        Tournesol does not use cookies for tracking purposes.
      </p>

      <h4>Embedded content from other websites</h4>
      <p>
        Tournesol embeds video content from YouTube. Embedded content from other websites
        behaves in the exact same way as if the visitor had visited the other website.
        These websites may collect data about the users, use cookies, embed additional
        third-party tracking. They may monitor the users’ interaction with that embedded
        content, including tracking their interaction with the embedded content if they
        have an account and are logged in to that website.
      </p>

      <h3>Who Tournesol shares users’ and contributors’ data with</h3>
      <p>
        Tournesol highly values the protection of users’ and contributors’ data. In particular,
        Tournesol knows that some of the contributors’ judgments may conflict with the agendas
        of some political leaders or of their employer. We want contributors to express
        judgments without the fear of any consequence for their personal life. This is why
        Tournesol has the option of providing judgments and comments privately or anonymously.
        Privately provided raw judgments and comments will not be shared with any third party.
      </p>

      <h4>Public data</h4>
      <p>
        Contributors are encouraged, when possible, to rate and comment videos publicly.
        This will allow us to collect a public database, which, hopefully, will stimulate
        research on more beneficial recommendation algorithms.
      </p>
      <p>
        Note that contributors can however publish comments anonymously. In this case, the
        comment is public, and we can certify whether it comes from a verified account, but
        the identity of the author of the comment will never be made public, nor be shared
        with third parties.
      </p>
      <p>
        Private ratings, i.e. ratings for which at least one video is rated privately by the
        contributor, will never be made public, nor shared with third parties.
      </p>

      <h4>Aggregate data</h4>
      <p>
        Our algorithms combine your data to other experts’ data to provide aggregate statistics,
        which are made public. This is typically the case of the Tournesol scores given to
        different videos. We also plan to release statistics about subsets of experts, e.g. to
        determine how pedagogical a physics video is according to biologists.
      </p>
      <p>
        In any such case, we apply the principles of differential privacy, by adding randomness
        to the actual aggregation, in order to increase the privacy of your data.
      </p>

      <h4>Research purposes</h4>
      <p>
        We believe that contributors’ data have an important scientific and ethical value to
        help make recommendation systems more robustly beneficial to humanity. This is why the
        data publicly provided by contributors will be easily downloadable by any user. We hope
        that this can stimulate academic and private research on more robustly beneficial
        recommendation algorithms.
      </p>

      <h3>How long we retain your data</h3>
      <p>
        If a user makes a search, rate videos or leave a comment, their data will be retained
        indefinitely, along with metadata. Tournesol does so to fulfill its mission to identify
        the top quality content that contributors want to see promoted at scale.
      </p>

      <p>
        All contributors can see, edit, or delete the personal information provided in their
        contributor page at any time (except they cannot change their username). Website
        administrators can also see and edit that information.
      </p>

      <h3>What rights you have over your data</h3>
      <p>
        By going to their contributor page, contributors can download the data they submitted to
        the platform. They can also request that Tournesol erases any personal data Tournesol
        recorded about them. This does not include the data that Tournesol is obliged to keep
        for administrative, legal, or security purposes.
      </p>

      <h3>Where we send your data</h3>
      <p>
        Visitor comments may be checked through an automated spam detection service.
      </p>

      <h3>Your contact information</h3>
      <p>
        Please see the legal mentions.
      </p>
    </div>
  );
};
