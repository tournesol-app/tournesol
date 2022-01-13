import React from 'react';
import { Typography } from '@mui/material';

import { ContentHeader } from 'src/components';
import { useTranslation } from 'react-i18next';

const PrivacyPolicyPage = () => {
  const { t } = useTranslation();
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
            {t('privacyPolicy.privacyPolicy')}
          </Typography>
          <Typography variant="h4" gutterBottom style={{ fontStyle: 'italic' }}>
            {t('privacyPolicy.whatPersonalDataTournesolCollectAndWhy')}
          </Typography>
          <Typography variant="h5">{t('privacyPolicy.ratings')}</Typography>
          <Typography paragraph>
            {t('privacyPolicy.whyTournesolCollectsRatings')}
          </Typography>
          <Typography variant="h5">{t('privacyPolicy.search')}</Typography>
          <Typography paragraph>
            {t('privacyPolicy.whyTournesolCollectsSearchQueries')}
          </Typography>
          <Typography variant="h5">
            {t('privacyPolicy.contributorProfile')}
          </Typography>
          <Typography paragraph>
            {t('privacyPolicy.whyTournesolCollectsContributorProfile')}
          </Typography>
          <Typography variant="h5">{t('privacyPolicy.contactForm')}</Typography>
          <Typography paragraph>
            {t('privacyPolicy.thereIsNoContactForm')}
          </Typography>
          <Typography variant="h5">{t('privacyPolicy.cookies')}</Typography>
          <Typography paragraph>
            {t('privacyPolicy.whyTournesolCollectscookies')}
          </Typography>
          <Typography variant="h5">
            {t('privacyPolicy.embeddedContentFromOtherWebsites')}
          </Typography>
          <Typography paragraph>
            {t('privacyPolicy.whatDataCollectEmbeddedWebsites')}
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
