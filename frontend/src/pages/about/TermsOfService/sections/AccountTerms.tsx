import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';

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
        {t('termsOfService.accountTerms.accountTerms')}
      </Typography>
      <Box my={2}>
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('termsOfService.shortVersion')}</strong>
          </AlertTitle>
          {t('termsOfService.accountTerms.shortVersion')}
        </Alert>
      </Box>
      <Typography variant="h5" gutterBottom id="account-controls">
        {t('termsOfService.accountTerms.accountControls')}
      </Typography>
      <Typography paragraph>
        {t(
          'termsOfService.accountTerms.usersRetainUltimateAdministrativeControl'
        )}
      </Typography>
      <Typography variant="h5" gutterBottom id="account-requirements">
        {t('termsOfService.accountTerms.accountRequirements')}
      </Typography>
      <Typography paragraph>
        {t('termsOfService.accountTerms.inOrderToCreateAccount')}
      </Typography>
      <ul>
        <li>
          <Typography paragraph>
            {t('termsOfService.accountTerms.aUserLoginMayNotBeShared')}
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            {t('termsOfService.accountTerms.aUserMayNotUseMoreThanOneAccount')}
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            {t(
              'termsOfService.accountTerms.aUserMustProvideAValidEmailAddress'
            )}
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            {t('termsOfService.accountTerms.userMustBeALeast15')}
          </Typography>
        </li>
      </ul>
      <Typography variant="h5" gutterBottom id="account-security">
        {t('termsOfService.accountTerms.accountSecurity')}
      </Typography>
      <Typography paragraph>
        {t('termsOfService.accountTerms.userIsResponsibleFor')}
      </Typography>
    </Box>
  );
};

export default AccountTerms;
