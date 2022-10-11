import React from 'react';
import { Typography } from '@mui/material';

import { ContentHeader } from 'src/components';
import { useTranslation, Trans } from 'react-i18next';

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
            <Trans t={t} i18nKey="privacyPolicy.whyTournesolCollectsRatings" />
          </Typography>
          <Typography variant="h5">{t('privacyPolicy.search')}</Typography>
          <Typography paragraph>
            <Trans
              t={t}
              i18nKey="privacyPolicy.whyTournesolCollectsSearchQueries"
            />
          </Typography>
          <Typography variant="h5">
            {t('privacyPolicy.contributorProfile')}
          </Typography>
          <Typography paragraph>
            <Trans
              t={t}
              i18nKey="privacyPolicy.whyTournesolCollectsContributorProfile"
            />
          </Typography>
          <Typography variant="h5">{t('privacyPolicy.contactForm')}</Typography>
          <Typography paragraph>
            <Trans t={t} i18nKey="privacyPolicy.thereIsNoContactForm" />
          </Typography>
          <Typography variant="h5">
            {t('privacyPolicy.loginInformation')}
          </Typography>
          <Typography paragraph>
            <Trans t={t} i18nKey="privacyPolicy.loginInformationDetails" />
          </Typography>
          <Typography variant="h5">
            {t('privacyPolicy.embeddedContentFromOtherWebsites')}
          </Typography>
          <Typography paragraph>
            <Trans
              t={t}
              i18nKey="privacyPolicy.whatDataCollectEmbeddedWebsites"
            />
          </Typography>
          <Typography variant="h4" gutterBottom sx={{ fontStyle: 'italic' }}>
            {t('privacyPolicy.whoTournesolSharesUsersNContributorsDataWith')}
          </Typography>
          <Typography paragraph>
            <Trans
              t={t}
              i18nKey="privacyPolicy.whoTournesolSharesUsersNContributorsDataWithParagraph"
            />
          </Typography>
          <Typography variant="h5">{t('privacyPolicy.publicData')}</Typography>
          <Typography paragraph>
            <Trans t={t} i18nKey="privacyPolicy.whereGoPublicData" />
          </Typography>
          <Typography variant="h5">
            {t('privacyPolicy.aggregateData')}
          </Typography>
          <Typography paragraph>
            <Trans t={t} i18nKey="privacyPolicy.whereGoAggregateData" />
          </Typography>
          <Typography variant="h5">
            {t('privacyPolicy.researchPurposes')}
          </Typography>
          <Typography paragraph>
            <Trans t={t} i18nKey="privacyPolicy.researchPurposesParagraph" />
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
