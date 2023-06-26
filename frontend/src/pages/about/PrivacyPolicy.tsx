import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';
import { useTranslation } from 'react-i18next';

const PrivacyPolicyPage = () => {
  const { t } = useTranslation();
  return (
    <>
      <ContentHeader
        title={`${t('menu.about')} > ${t('privacyPolicy.privacyPolicy')}`}
      />
      <ContentBox maxWidth="md">
        <Typography variant="h3" textAlign="center" mt={2} mb={4}>
          {t('privacyPolicy.privacyPolicy')}
        </Typography>
        <Box display="flex" flexDirection="column" gap={4}>
          <Paper sx={{ p: 2 }}>
            <Typography
              id="what-personal-data-tournesol-collects-and-why"
              variant="h4"
              fontStyle="italic"
              gutterBottom
            >
              {t('privacyPolicy.whatPersonalDataTournesolCollectAndWhy')}
            </Typography>
            <Typography id="ratings" variant="h5" gutterBottom>
              {t('privacyPolicy.ratings')}
            </Typography>
            <Typography paragraph>
              {t('privacyPolicy.whyTournesolCollectsRatings')}
            </Typography>
            <Typography id="search" variant="h5" gutterBottom>
              {t('privacyPolicy.search')}
            </Typography>
            <Typography paragraph>
              {t('privacyPolicy.whyTournesolCollectsSearchQueries')}
            </Typography>
            <Typography
              id="why-tournesol-collects-contributor-profile"
              variant="h5"
              gutterBottom
            >
              {t('privacyPolicy.contributorProfile')}
            </Typography>
            <Typography paragraph>
              {t('privacyPolicy.whyTournesolCollectsContributorProfile')}
            </Typography>
            <Typography id="contact-form" variant="h5" gutterBottom>
              {t('privacyPolicy.contactForm')}
            </Typography>
            <Typography paragraph>
              {t('privacyPolicy.thereIsNoContactForm')}
            </Typography>
            <Typography id="login-information" variant="h5" gutterBottom>
              {t('privacyPolicy.loginInformation')}
            </Typography>
            <Typography paragraph>
              {t('privacyPolicy.loginInformationDetails')}
            </Typography>
            <Typography
              id="embedded-content-from-other-websites"
              variant="h5"
              gutterBottom
            >
              {t('privacyPolicy.embeddedContentFromOtherWebsites')}
            </Typography>
            <Typography paragraph mb={0}>
              {t('privacyPolicy.whatDataCollectEmbeddedWebsites')}
            </Typography>
          </Paper>
          <Paper sx={{ p: 2 }}>
            <Typography
              id="who-tournesol-shares-users-n-contributors-data-with"
              variant="h4"
              gutterBottom
              sx={{ fontStyle: 'italic' }}
            >
              {t('privacyPolicy.whoTournesolSharesUsersNContributorsDataWith')}
            </Typography>
            <Typography paragraph>
              {t(
                'privacyPolicy.whoTournesolSharesUsersNContributorsDataWithParagraph'
              )}
            </Typography>
            <Typography id="public-data" variant="h5">
              {t('privacyPolicy.publicData')}
            </Typography>
            <Typography paragraph>
              {t('privacyPolicy.whereGoPublicData')}
            </Typography>
            <Typography id="aggregate-data" variant="h5">
              {t('privacyPolicy.aggregateData')}
            </Typography>
            <Typography paragraph>
              {t('privacyPolicy.whereGoAggregateData')}
            </Typography>
            <Typography id="research-purposes" variant="h5">
              {t('privacyPolicy.researchPurposes')}
            </Typography>
            <Typography paragraph>
              {t('privacyPolicy.researchPurposesParagraph')}
            </Typography>
          </Paper>
          <Paper sx={{ p: 2 }}>
            <Typography
              id="how-long-tournesol-retains-contributors-data"
              variant="h4"
              gutterBottom
              sx={{ fontStyle: 'italic' }}
            >
              {t('privacyPolicy.howLongTournesolRetainsContributorsData')}
            </Typography>
            <Typography paragraph>
              {t(
                'privacyPolicy.howLongTournesolRetainsContributorsDataParagraph'
              )}
            </Typography>
          </Paper>
          <Paper sx={{ p: 2 }}>
            <Typography
              id="what-rights-contributors-have-over-their-data"
              variant="h4"
              gutterBottom
              sx={{ fontStyle: 'italic' }}
            >
              {t('privacyPolicy.whatRightsContributorsHaveOverTheirData')}
            </Typography>
            <Typography paragraph>
              {t(
                'privacyPolicy.whatRightsContributorsHaveOverTheirDataParagraph'
              )}
            </Typography>
          </Paper>
        </Box>
      </ContentBox>
    </>
  );
};

export default PrivacyPolicyPage;
