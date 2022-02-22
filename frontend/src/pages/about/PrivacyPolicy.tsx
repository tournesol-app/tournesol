import React from 'react';
import { Typography } from '@mui/material';

import { ContentHeader } from 'src/components';
import { useTranslation } from 'react-i18next';

const PrivacyPolicyPage = () => {
  const { t } = useTranslation();
  return (
    <>
      <ContentHeader
        title={`${t('menu.about')} > ${t('privacyPolicy.privacyPolicy')}`}
      />
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
          <Typography variant="h4" gutterBottom sx={{ fontStyle: 'italic' }}>
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
          <Typography variant="h4" gutterBottom sx={{ fontStyle: 'italic' }}>
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
          <Typography variant="h5">
            {t('privacyPolicy.researchPurposes')}
          </Typography>
          <Typography paragraph>
            {t('privacyPolicy.researchPurposesParagraph')}
          </Typography>
          <Typography variant="h4" gutterBottom sx={{ fontStyle: 'italic' }}>
            {t('privacyPolicy.howLongTournesolRetainsContributorsData')}
          </Typography>
          <Typography paragraph>
            {t(
              'privacyPolicy.howLongTournesolRetainsContributorsDataParagraph'
            )}
          </Typography>
          <Typography variant="h4" gutterBottom sx={{ fontStyle: 'italic' }}>
            {t('privacyPolicy.whatRightsContributorsHaveOverTheirData')}
          </Typography>
          <Typography paragraph>
            {t(
              'privacyPolicy.whatRightsContributorsHaveOverTheirDataParagraph'
            )}
          </Typography>
        </div>
      </div>
    </>
  );
};

export default PrivacyPolicyPage;
