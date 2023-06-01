import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Link, Typography } from '@mui/material';

import { githubTournesolCodeOfConductUrl } from 'src/utils/url';

const AcceptableUse = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="acceptable-use"
      >
        {t('termsOfService.acceptableUse.acceptableUse')}
      </Typography>
      <Box my={2}>
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('termsOfService.shortVersion')}</strong>
          </AlertTitle>
          {t('termsOfService.acceptableUse.shortVersion')}
        </Alert>
      </Box>
      <Typography
        variant="h5"
        gutterBottom
        id="compliance-with-laws-and-regulation"
      >
        {t(
          'termsOfService.acceptableUse.titles.1ComplianceWithLawsAndRegulation'
        )}
      </Typography>
      <Typography paragraph>
        {t(
          'termsOfService.acceptableUse.paragraphs.complianceWithLawsAndRegulation'
        )}
      </Typography>
      <Typography variant="h5" gutterBottom id="user-safety">
        {t('termsOfService.acceptableUse.titles.2UserSafety')}
      </Typography>
      <Typography paragraph>
        {t('termsOfService.acceptableUse.paragraphs.userSafetyIntro')}
      </Typography>
      <ul>
        <li>
          <Typography paragraph>
            {t(
              'termsOfService.acceptableUse.paragraphs.isUnlawlfulOrPromoteUnlawful'
            )}
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            {t(
              'termsOfService.acceptableUse.paragraphs.isFalseInaccurateOrDeceptive'
            )}
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            <Trans
              t={t}
              i18nKey="termsOfService.acceptableUse.paragraphs.orGoesAgainstOurCodeOfConduct"
            >
              or goes against our{' '}
              <Link
                href={githubTournesolCodeOfConductUrl}
                target="_blank"
                rel="noopener"
                sx={{
                  color: 'revert',
                  textDecoration: 'revert',
                }}
              >
                Code of Conduct
              </Link>
              .
            </Trans>
          </Typography>
        </li>
      </ul>
      <Typography variant="h5" gutterBottom id="inauthentic-activity-and-spam">
        {t('termsOfService.acceptableUse.titles.3InauthenticActivityAndSpam')}
      </Typography>
      <Typography paragraph>
        {t(
          'termsOfService.acceptableUse.paragraphs.inauthenticActivityAndSpamIntro'
        )}
      </Typography>
    </Box>
  );
};

export default AcceptableUse;
