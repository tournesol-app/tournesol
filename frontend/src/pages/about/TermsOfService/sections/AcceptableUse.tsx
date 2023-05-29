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
        {t('termsOfService.acceptableUse')}
      </Typography>
      <Typography variant="h5" gutterBottom id="compliance-with-laws">
        {t(
          'termsOfService.acceptableUseSection.titles.1ComplianceWithLawsAndRegulation'
        )}
      </Typography>
      <Typography paragraph>
        {t(
          'termsOfService.acceptableUseSection.paragraphs.complianceWithLawsAndRegulation'
        )}
      </Typography>
      <Typography variant="h5" gutterBottom id="user-safety">
        {t('termsOfService.acceptableUseSection.titles.2UserSafety')}
      </Typography>
      <Typography paragraph>
        {t('termsOfService.acceptableUseSection.paragraphs.userSafetyIntro')}
      </Typography>
      <ul>
        <li>is unlawful or promotes unlawful activities;</li>
        <li>
          is false, inaccurate, or intentionally deceptive information and
          likely to adversely affect the public interest (including health,
          safety, election integrity, and civic participation);
        </li>
        <li>or goes against out Code of Conduct</li>
      </ul>
      <Typography variant="h5" gutterBottom id="account-security">
        {t(
          'termsOfService.acceptableUseSection.titles.3InauthenticActivityAndSpam'
        )}
      </Typography>
      <p>
        We do not allow activity the Platform that is: inauthentic interactions,
        such as fake accounts and automated inauthentic activity; or automated
        excessive bulk activity and coordinated inauthentic activity.
      </p>
      <Typography variant="h5" gutterBottom id="service-usage-limits">
        {t('termsOfService.acceptableUseSection.titles.4ServiceUsageLimits')}
      </Typography>
      <p>
        todo: make a better distinction between the source code and the service
      </p>
      <p>
        Our Source Code, including the code, the documentations, the images and
        the other materials used by the Service can be used by following the
        terms of their licenses.
      </p>
      <p>
        Nevertheless, you will not reproduce, duplicate, copy, sell, resell or
        exploit any portion of the Service itself, use of the Service, or access
        to the Service without our express written permission.
      </p>
    </Box>
  );
};

export default AcceptableUse;
