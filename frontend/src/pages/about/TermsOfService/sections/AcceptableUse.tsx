import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';

import { ExternalLink } from 'src/components';
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
        {t('terms.acceptableUse.acceptableUse')}
      </Typography>
      <Box my={2}>
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('terms.shortVersion')}</strong>
          </AlertTitle>
          {t('terms.acceptableUse.shortVersion')}
        </Alert>
      </Box>
      <Typography
        variant="h5"
        gutterBottom
        id="compliance-with-laws-and-regulation"
      >
        {t('terms.acceptableUse.titles.1ComplianceWithLawsAndRegulation')}
      </Typography>
      <Typography paragraph>
        {t('terms.acceptableUse.p.complianceWithLawsAndRegulation')}
      </Typography>
      <Typography variant="h5" gutterBottom id="user-safety">
        {t('terms.acceptableUse.titles.2UserSafety')}
      </Typography>
      <Typography paragraph>
        {t('terms.acceptableUse.p.userSafetyIntro')}
      </Typography>
      <ul>
        <li>
          <Typography paragraph>
            {t('terms.acceptableUse.p.isUnlawlfulOrPromoteUnlawful')}
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            {t('terms.acceptableUse.p.isFalseInaccurateOrDeceptive')}
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            <Trans
              t={t}
              i18nKey="terms.acceptableUse.p.orGoesAgainstOurCodeOfConduct"
            >
              or goes against our{' '}
              <ExternalLink href={githubTournesolCodeOfConductUrl}>
                Code of Conduct
              </ExternalLink>
              .
            </Trans>
          </Typography>
        </li>
      </ul>
      <Typography variant="h5" gutterBottom id="inauthentic-activity-and-spam">
        {t('terms.acceptableUse.titles.3InauthenticActivityAndSpam')}
      </Typography>
      <Typography paragraph>
        {t('terms.acceptableUse.p.inauthenticActivityAndSpamIntro')}
      </Typography>
    </Box>
  );
};

export default AcceptableUse;
