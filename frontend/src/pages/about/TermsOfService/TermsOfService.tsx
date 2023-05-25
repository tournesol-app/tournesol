import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';

import AccountTerms from './sections/AccountTerms';
import Definitions from './sections/DefinitionsSection';

const TermsOfServicePage = () => {
  const { t } = useTranslation();
  return (
    <>
      <ContentHeader
        title={`${t('menu.about')} > ${t('termsOfService.termsOfService')}`}
      />
      <ContentBox maxWidth="md">
        <Typography variant="h3" gutterBottom>
          {t('termsOfService.termsOfService')}
        </Typography>
        <Box display="flex" flexDirection="column" gap={4}>
          <Definitions />
          <AccountTerms />
          <Typography
            variant="h4"
            fontStyle="italic"
            gutterBottom
            id="acceptable-use"
          >
            {t('termsOfService.acceptableUse')}
          </Typography>
          <Typography
            variant="h4"
            fontStyle="italic"
            gutterBottom
            id="moderation"
          >
            {t('termsOfService.moderation')}
          </Typography>
          <Typography
            variant="h4"
            fontStyle="italic"
            gutterBottom
            id="cancellation"
          >
            {t('termsOfService.cancellationAndTermination')}
          </Typography>
          <Typography
            variant="h4"
            fontStyle="italic"
            gutterBottom
            id="communications"
          >
            {t('termsOfService.communicationsWithTheAssociation')}
          </Typography>
          <Typography
            variant="h4"
            fontStyle="italic"
            gutterBottom
            id="changes-to-these-terms"
          >
            {t('termsOfService.changesToTheseTerms')}
          </Typography>
        </Box>
      </ContentBox>
    </>
  );
};

export default TermsOfServicePage;
