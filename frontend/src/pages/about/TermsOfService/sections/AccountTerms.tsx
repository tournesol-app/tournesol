import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';

const AccountTerms = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        gutterBottom
        id="account-terms"
        sx={{
          fontStyle: 'italic',
        }}
      >
        {t('terms.accountTerms.accountTerms')}
      </Typography>
      <Box
        sx={{
          my: 2,
        }}
      >
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('terms.shortVersion')}</strong>
          </AlertTitle>
          {t('terms.accountTerms.shortVersion')}
        </Alert>
      </Box>
      <Typography variant="h5" gutterBottom id="account-controls">
        {t('terms.accountTerms.accountControls')}
      </Typography>
      <Typography
        sx={{
          marginBottom: '16px',
        }}
      >
        {t('terms.accountTerms.userRetainsUltimateAdministrativeControl')}
      </Typography>
      <Typography variant="h5" gutterBottom id="account-requirements">
        {t('terms.accountTerms.accountRequirements')}
      </Typography>
      <Typography
        sx={{
          marginBottom: '16px',
        }}
      >
        {t('terms.accountTerms.inOrderToCreateAccount')}
      </Typography>
      <ul>
        <li>
          <Typography
            sx={{
              marginBottom: '16px',
            }}
          >
            {t('terms.accountTerms.aUserMayNotUseMoreThanOneAccount')}
          </Typography>
        </li>
        <li>
          <Typography
            sx={{
              marginBottom: '16px',
            }}
          >
            {t('terms.accountTerms.aUserLoginMayNotBeShared')}
          </Typography>
        </li>
        <li>
          <Typography
            sx={{
              marginBottom: '16px',
            }}
          >
            {t('terms.accountTerms.aUserMustProvideAValidEmailAddress')}
          </Typography>
        </li>
        <li>
          <Typography
            sx={{
              marginBottom: '16px',
            }}
          >
            {t('terms.accountTerms.userMustBeALeast15')}
          </Typography>
        </li>
      </ul>
      <Typography variant="h5" gutterBottom id="account-security">
        {t('terms.accountTerms.accountSecurity')}
      </Typography>
      <Typography
        sx={{
          marginBottom: '16px',
        }}
      >
        {t('terms.accountTerms.userIsResponsibleFor')}
      </Typography>
    </Box>
  );
};

export default AccountTerms;
