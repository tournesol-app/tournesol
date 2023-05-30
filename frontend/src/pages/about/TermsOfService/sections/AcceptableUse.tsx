import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

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
        {t('termsOfService.acceptableUse.cAcceptableUse')}
      </Typography>
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
        <li>is unlawful or promotes unlawful activities;</li>
        <li>
          is false, inaccurate, or intentionally deceptive information and
          likely to adversely affect the public interest (including health,
          safety, election integrity, and civic participation);
        </li>
        <li>or goes against out Code of Conduct.</li>
      </ul>
      <Typography variant="h5" gutterBottom id="inauthentic-activity-and-spam">
        {t('termsOfService.acceptableUse.titles.3InauthenticActivityAndSpam')}
      </Typography>
      <p>
        We do not allow activity the Platform that is: inauthentic interactions,
        such as fake accounts and automated inauthentic activity; or automated
        excessive bulk activity and coordinated inauthentic activity.
      </p>
    </Box>
  );
};

export default AcceptableUse;
