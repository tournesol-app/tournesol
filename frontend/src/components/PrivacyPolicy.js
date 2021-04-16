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
      Our website address is <a href="https://tournesol.app">https://tournesol.app</a>

      <h3>What personal data we collect and why we collect it</h3>
      <h4>Ratings</h4>
      Our mission to elicit, infer and aggregate experts’ judgments on which content
      recommendations are most beneficial. To do so, we collect the data provided by any user
      acting like a potential expert in the content rating interface. We also measure the
      response time, to further research in distinguishing instinctive responses from
      thoughtful responses. We believe that such data have a huge scientific value to help
      make recommendation systems more robustly beneficial to humanity.

      <h4>Search</h4>
      If you are not logged in, we will collect the parameters of your search queries in order
      to better understand most users’ needs. We believe that such data can have a scientific
      value to help make recommendation systems more robustly beneficial to humanity.

      <h4>User profile</h4>
      In order to distinguish different users’ expertise, we ask users to certify their
      emails, to report their fields of expertise and to link to their public profiles. We
      believe that such data have an important scientific value to help make recommendation
      systems more robustly beneficial to humanity.

      <h4>Comments</h4>
      When users leave comments on the site, we collect the data shown in the comments form,
      and browser user agent string to help spam detection. The data is also labeled with the
      user’s Tournesol profile. We believe that such data have an important scientific value
      to help make recommendation systems more robustly beneficial to humanity.

      <h4>Contact form</h4>
      There is no contact form. If you need to contact us, please email
      <a href="mailto:le-nguyen.hoang@science4all.org">
        le-nguyen.hoang@science4all.org
      </a>

      <h4>Cookies</h4>
      If you have an account and you log in to this site, we will set a temporary cookie to
      determine if your browser accepts cookies. This cookie contains no personal data and is
      discarded when you close your browser.

      When you log in, we will also set up several cookies to save your login information and
      your screen display choices. Login cookies last for two days, and screen options cookies
      last for a year. If you select “Remember Me”, your login will persist for two weeks. If
      you log out of your account, the login cookies will be removed.

      We do not use cookies for tracking purposes.

      <h4>Embedded content from other websites</h4>
      Tournesol embeds video content from YouTube. Embedded content from other websites
      behaves in the exact same way as if the visitor has visited the other website. These
      websites may collect data about you, use cookies, embed additional third-party tracking,
      and monitor your interaction with that embedded content, including tracking your
      interaction with the embedded content if you have an account and are logged in to that
      website.

      <h4>Who we share your data with</h4>
      We highly value the protection of your data, as we know that some opinions you provide
      may conflict with the agendas of some political leaders or of your employer. We want you
      to express judgments without the fear of any consequence for your personal life. This is
      why we will not share your raw data with any third party.

      Some of the data we collect can, by nature, be seen by anybody, as e.g. comments that
      you post on the website. Note that you can customize how much you reveal about who you
      are when you comment.

      <h4>Aggregate data</h4>
      Our algorithms combine your data to other experts’ data to provide aggregate statistics,
      which are made public. This is typically the case of the Tournesol scores given to
      different videos. We also plan to release statistics about subsets of experts, e.g. to
      determine how pedagogical a physics video is according to biologists.

      In any such case, we apply the principles of differential privacy, by adding randomness
      to the actual aggregation, in order to increase the privacy of your data.

      <h4>Research purposes</h4>
      We believe that your data have an important scientific value to help make recommendation
      systems more robustly beneficial to humanity. This is why we plan to randomize our
      users’ data to create and release publicly an anonymized dataset to be analyzed by other
      researchers. Again, we plan to abide by the principles of differential privacy.

      <h4>How long we retain your data</h4>
      If you make a search, rate videos or leave a comment, the data you input will be
      retained indefinitely, along with metadata. This is so that we can fulfill our mission
      to identify quality content that experts want to see promoted at scale.

      For users that register on our website (if any), we also store the personal information
      they provide in their user profile. All users can see, edit, or delete their personal
      information at any time (except they cannot change their username). Website
      administrators can also see and edit that information.

      <h4>What rights you have over your data</h4>
      If you have an account on this site, or have left comments, you can request to receive
      an exported file of the personal data we hold about you, including any data you have
      provided to us. You can also request that we erase any personal data we hold about you.
      This does not include any data we are obliged to keep for administrative, legal, or
      security purposes.

      <h4>Where we send your data</h4>
      Visitor comments may be checked through an automated spam detection service.

      <h4>Your contact information</h4>
      Please see the legal mentions.
    </div>
  );
};
