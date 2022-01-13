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
            {t('privacyPolicy.whoTournesolSharesUsersNContributorsDataWith')}
          </Typography>
          <Typography paragraph>
            {t(
              'privacyPolicy.whoTournesolSharesUsersNContributorsDataWithParagraph'
            )}
          </Typography>
          <Typography variant="h5">{t('privacyPolicy.publicData')}</Typography>
          <Typography paragraph>
            {t('privacyPolicy.whereGoPublicData')}
          </Typography>
          <Typography variant="h5">
            {t('privacyPolicy.aggregateData')}
          </Typography>
          <Typography paragraph>
            {t('privacyPolicy.whereGoAggregateData')}
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
