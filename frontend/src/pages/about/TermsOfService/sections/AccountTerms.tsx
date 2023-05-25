import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

const AccountTerms = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="account-terms"
      >
        {t('termsOfService.accountTerms')}
      </Typography>
      <Typography variant="h5" gutterBottom id="account-controls">
        {t('termsOfService.accountTermsSection.accountControls')}
      </Typography>
      <Typography paragraph>
        {t(
          'termsOfService.accountTermsSection.usersRetainUltimateAdministrativeControl'
        )}
      </Typography>
      <Typography variant="h5" gutterBottom id="account-requirements">
        {t('termsOfService.accountTermsSection.accountRequirements')}
      </Typography>
      <Typography paragraph>
        {t('termsOfService.accountTermsSection.inOrderToCreateAccount')}
      </Typography>
      <ul>
        <li>
          <Typography paragraph>
            {t('termsOfService.accountTermsSection.aUserLoginMayNotBeShared')}
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            {t('termsOfService.accountTermsSection.userMustBeALeast15')}
          </Typography>
        </li>
      </ul>
      <Typography variant="h5" gutterBottom id="account-security">
        {t('termsOfService.accountTermsSection.accountSecurity')}
      </Typography>
      <Typography paragraph>
        {t('termsOfService.accountTermsSection.userIsResponsibleFor')}
      </Typography>
    </Box>
  );
};

export default AccountTerms;
