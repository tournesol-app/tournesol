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
      <ContentBoxLegalDocument
        mainTitle={t('privacyPolicy.privacyPolicy')}
        sx={{
          h4: {
            color: 'secondary.main',
            fontStyle: 'italic',
            mb: 2,
          },
          h5: {
            mb: 1,
          },
          '& p': {
            mb: 3,
          },
        }}
      >
        <LegalPaper>
          <Typography
            id="what-personal-data-tournesol-collects-and-why"
            variant="h4"
          >
            1. {t('privacyPolicy.whatPersonalDataTournesolCollectAndWhy')}
          </Typography>
          <Typography id="ratings" variant="h5">
            1.1. {t('privacyPolicy.ratings')}
          </Typography>
          <Typography>
            {t('privacyPolicy.whyTournesolCollectsRatings')}
          </Typography>
          <Typography id="search" variant="h5">
            1.2. {t('privacyPolicy.search')}
          </Typography>
          <Typography>
            {t('privacyPolicy.whyTournesolCollectsSearchQueries')}
          </Typography>
          <Typography
            id="why-tournesol-collects-contributor-profile"
            variant="h5"
          >
            1.3. {t('privacyPolicy.contributorProfile')}
          </Typography>
          <Typography>
            {t('privacyPolicy.whyTournesolCollectsContributorProfile')}
          </Typography>
          <Typography id="contact-form" variant="h5">
            1.4. {t('privacyPolicy.contactForm')}
          </Typography>
          <Typography>{t('privacyPolicy.thereIsNoContactForm')}</Typography>
          <Typography id="login-information" variant="h5">
            1.5. {t('privacyPolicy.loginInformation')}
          </Typography>
          <Typography>{t('privacyPolicy.loginInformationDetails')}</Typography>
          <Typography id="embedded-content-from-other-websites" variant="h5">
            1.6. {t('privacyPolicy.embeddedContentFromOtherWebsites')}
          </Typography>
          <Typography>
            {t('privacyPolicy.whatDataCollectEmbeddedWebsites')}
          </Typography>
          <Typography id="browser-extension" variant="h5">
            1.7. {t('privacyPolicy.browserExtension')}
          </Typography>
          <Typography>
            {t('privacyPolicy.browserExtensionDataCollection')}
          </Typography>
        </LegalPaper>
        <LegalPaper>
          <Typography
            id="who-tournesol-shares-users-n-contributors-data-with"
            variant="h4"
          >
            2. {t('privacyPolicy.whoTournesolSharesUsersNContributorsDataWith')}
          </Typography>
          <Typography>
            {t(
              'privacyPolicy.whoTournesolSharesUsersNContributorsDataWithParagraph'
            )}
          </Typography>
          <Typography id="public-data" variant="h5">
            2.1. {t('privacyPolicy.publicData')}
          </Typography>
          <Typography>{t('privacyPolicy.whereGoPublicData')}</Typography>
          <Typography id="aggregate-data" variant="h5">
            2.2. {t('privacyPolicy.aggregateData')}
          </Typography>
          <Typography>{t('privacyPolicy.whereGoAggregateData')}</Typography>
          <Typography id="research-purposes" variant="h5">
            2.3. {t('privacyPolicy.researchPurposes')}
          </Typography>
          <Typography>
            {t('privacyPolicy.researchPurposesParagraph')}
          </Typography>
        </LegalPaper>
        <LegalPaper>
          <Typography
            id="how-long-tournesol-retains-contributors-data"
            variant="h4"
          >
            3. {t('privacyPolicy.howLongTournesolRetainsContributorsData')}
          </Typography>
          <Typography>
            {t(
              'privacyPolicy.howLongTournesolRetainsContributorsDataParagraph'
            )}
          </Typography>
        </LegalPaper>
        <LegalPaper>
          <Typography
            id="what-rights-contributors-have-over-their-data"
            variant="h4"
          >
            4. {t('privacyPolicy.whatRightsContributorsHaveOverTheirData')}
          </Typography>
          <Typography>
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
