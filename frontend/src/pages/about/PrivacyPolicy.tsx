import React from 'react';
import { Typography } from '@mui/material';

import {
  ContentHeader,
  ContentBoxLegalDocument,
  LegalPaper,
} from 'src/components';
import { useTranslation } from 'react-i18next';

const PrivacyPolicyPage = () => {
  const { t } = useTranslation();
  return (
    <>
      <ContentHeader
        title={`${t('menu.about')} > ${t('privacyPolicy.privacyPolicy')}`}
      />
      <ContentBoxLegalDocument mainTitle={t('privacyPolicy.privacyPolicy')}>
        <LegalPaper>
          <Typography
            id="what-personal-data-tournesol-collects-and-why"
            variant="h4"
            gutterBottom
            sx={{
              fontStyle: 'italic',
            }}
          >
            {t('privacyPolicy.whatPersonalDataTournesolCollectAndWhy')}
          </Typography>
          <Typography id="ratings" variant="h5" gutterBottom>
            {t('privacyPolicy.ratings')}
          </Typography>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t('privacyPolicy.whyTournesolCollectsRatings')}
          </Typography>
          <Typography id="search" variant="h5" gutterBottom>
            {t('privacyPolicy.search')}
          </Typography>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t('privacyPolicy.whyTournesolCollectsSearchQueries')}
          </Typography>
          <Typography
            id="why-tournesol-collects-contributor-profile"
            variant="h5"
            gutterBottom
          >
            {t('privacyPolicy.contributorProfile')}
          </Typography>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t('privacyPolicy.whyTournesolCollectsContributorProfile')}
          </Typography>
          <Typography id="contact-form" variant="h5" gutterBottom>
            {t('privacyPolicy.contactForm')}
          </Typography>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t('privacyPolicy.thereIsNoContactForm')}
          </Typography>
          <Typography id="login-information" variant="h5" gutterBottom>
            {t('privacyPolicy.loginInformation')}
          </Typography>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t('privacyPolicy.loginInformationDetails')}
          </Typography>
          <Typography
            id="embedded-content-from-other-websites"
            variant="h5"
            gutterBottom
          >
            {t('privacyPolicy.embeddedContentFromOtherWebsites')}
          </Typography>
          <Typography
            sx={{
              mb: 0,
            }}
          >
            {t('privacyPolicy.whatDataCollectEmbeddedWebsites')}
          </Typography>
        </LegalPaper>
        <LegalPaper>
          <Typography
            id="who-tournesol-shares-users-n-contributors-data-with"
            variant="h4"
            gutterBottom
            sx={{ fontStyle: 'italic' }}
          >
            {t('privacyPolicy.whoTournesolSharesUsersNContributorsDataWith')}
          </Typography>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t(
              'privacyPolicy.whoTournesolSharesUsersNContributorsDataWithParagraph'
            )}
          </Typography>
          <Typography id="public-data" variant="h5">
            {t('privacyPolicy.publicData')}
          </Typography>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t('privacyPolicy.whereGoPublicData')}
          </Typography>
          <Typography id="aggregate-data" variant="h5">
            {t('privacyPolicy.aggregateData')}
          </Typography>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t('privacyPolicy.whereGoAggregateData')}
          </Typography>
          <Typography id="research-purposes" variant="h5">
            {t('privacyPolicy.researchPurposes')}
          </Typography>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t('privacyPolicy.researchPurposesParagraph')}
          </Typography>
        </LegalPaper>
        <LegalPaper>
          <Typography
            id="how-long-tournesol-retains-contributors-data"
            variant="h4"
            gutterBottom
            sx={{ fontStyle: 'italic' }}
          >
            {t('privacyPolicy.howLongTournesolRetainsContributorsData')}
          </Typography>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t(
              'privacyPolicy.howLongTournesolRetainsContributorsDataParagraph'
            )}
          </Typography>
        </LegalPaper>
        <LegalPaper>
          <Typography
            id="what-rights-contributors-have-over-their-data"
            variant="h4"
            gutterBottom
            sx={{ fontStyle: 'italic' }}
          >
            {t('privacyPolicy.whatRightsContributorsHaveOverTheirData')}
          </Typography>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t(
              'privacyPolicy.whatRightsContributorsHaveOverTheirDataParagraph'
            )}
          </Typography>
        </LegalPaper>
      </ContentBoxLegalDocument>
    </>
  );
};

export default PrivacyPolicyPage;
