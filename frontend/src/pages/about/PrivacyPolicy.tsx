import React from 'react';
import { Typography } from '@material-ui/core';

import { ContentHeader } from 'src/components';

const PrivacyPolicyPage = () => {
  return (
    <>
      <ContentHeader title="About > Privacy Policy" />
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            maxWidth: '100%',
            width: 840,
            color: '#4A473E',
            padding: 24,
          }}
        >
          <Typography variant="h3" gutterBottom>
            Privacy Policy
          </Typography>
          <Typography variant="h4" gutterBottom style={{ fontStyle: 'italic' }}>
            What personal data Tournesol collects and why?
          </Typography>
          <Typography variant="h5">Ratings</Typography>
          <Typography paragraph>
            Our mission is to elicit, infer and aggregate contributors’
            judgments on the quality of online videos. To do so, Tournesol
            collects the data provided by the contributors when they compare
            pairs of content.
          </Typography>
          <Typography variant="h5">Search</Typography>
          <Typography paragraph>
            Even if the contributor is not logged in, Tournesol collects the
            parameters of their search queries in order to better understand
            most users’ needs. We believe that such data can also have a
            scientific and ethical value to help make recommendation systems
            more robustly beneficial to humanity.
          </Typography>
          <Typography variant="h5">Contributor profile</Typography>
          <Typography paragraph>
            In order to distinguish different contributors’ expertise, Tournesol
            asks contributors to certify their emails, to report their fields of
            expertise and to link to their public profiles. We believe that such
            data have an important scientific and ethical value and will help
            make recommendation systems more robustly beneficial to humanity.
          </Typography>
          <Typography variant="h5">Contact form</Typography>
          <Typography paragraph>
            There is no contact form. If you need to contact us, please use the
            following email: tournesol.application(at)gmail.com
          </Typography>
          <Typography variant="h5">Cookies</Typography>
          <Typography paragraph>
            If a contributor has an account and logs in Tournesol, Tournesol
            will set a temporary cookie to determine if their browser accepts
            cookies. This cookie contains no personal data and is discarded when
            the contributor closes their browser. When the contributor logs in,
            Tournesol will also set up several cookies to save their login
            information and their screen display choices. Login cookies last for
            two days, and screen options cookies last for a year. If the
            contributor selects “Remember Me”, their login will persist for two
            weeks. If they log out of their account, the login cookies will be
            removed. Tournesol does not use cookies for tracking purposes.
          </Typography>
          <Typography variant="h5">
            Embedded content from other websites
          </Typography>
          <Typography paragraph>
            Tournesol embeds video content from YouTube. Embedded content from
            other websites behaves in the exact same way as if the visitor had
            visited the other website. These websites may collect data about the
            users, use cookies, and embed additional third-party tracking. They
            may monitor the users’ interaction with that embedded content,
            including tracking their interaction with the embedded content if
            they have an account and are logged in to that website
          </Typography>
          <Typography variant="h4" gutterBottom style={{ fontStyle: 'italic' }}>
            Who Tournesol shares users’ and contributors’ data with?
          </Typography>
          <Typography paragraph>
            Tournesol highly values the protection of users’ and contributors’
            data. In particular, Tournesol knows that some of the contributors’
            judgments may conflict with the agendas of some political leaders or
            of their employer. We want contributors to express judgments without
            the fear of any consequence for their personal life. This is why
            Tournesol has the option of providing judgments privately or
            anonymously. Privately provided raw judgments will not be shared
            with any third party.
          </Typography>
          <Typography variant="h5">Public data</Typography>
          <Typography paragraph>
            Contributors are encouraged, when possible, to compare videos
            publicly. This will allow us to collect a public database, which,
            hopefully, will stimulate research on more beneficial recommendation
            algorithms. Private ratings, i.e. ratings for which at least one
            video is rated privately by the contributor, will never be made
            public, nor shared with third parties
          </Typography>
          <Typography variant="h5">Aggregate data</Typography>
          <Typography paragraph>
            Our algorithms combine contributors’ public and private data to
            provide aggregate statistics, which are made public. This is
            typically the case of the Tournesol scores given to different
            videos. Tournesol also plans to release statistics about subsets of
            contributors, e.g. to determine how pedagogical a physics video is
            according to biologists. In any such case, we apply the principles
            of differential privacy, by adding randomness to the actual
            aggregation, in order to increase the privacy of your data.
          </Typography>
          <Typography variant="h5">Research purposes</Typography>
          <Typography paragraph>
            We believe that contributors’ data have an important scientific and
            ethical value to help make recommendation systems more robustly
            beneficial to humanity. This is why the data publicly provided by
            contributors will be easily downloadable by any user. We hope that
            this can stimulate academic and private research on more robustly
            beneficial recommendation algorithms.
          </Typography>
          <Typography variant="h4" gutterBottom style={{ fontStyle: 'italic' }}>
            How long Tournesol retains contributors’ data?
          </Typography>
          <Typography paragraph>
            If a user makes a search or compares videos, their data will be
            retained indefinitely, along with metadata. Tournesol does so to
            fulfill its mission to identify the top quality content that
            contributors want to see promoted at scale. All contributors can
            see, edit, or delete the personal information provided in their
            contributor page at any time (except they cannot change their
            username). Website administrators can also see and edit that
            information.
          </Typography>
          <Typography variant="h4" gutterBottom style={{ fontStyle: 'italic' }}>
            What rights contributors have over their data?
          </Typography>
          <Typography paragraph>
            By going to their contributor page, contributors can download the
            data they submitted to their platform. They can also request that
            Tournesol erases any personal data Tournesol recorded about them.
            This does not include the data that Tournesol is obliged to keep for
            administrative, legal, or security purposes.
          </Typography>
        </div>
      </div>
    </>
  );
};

export default PrivacyPolicyPage;
