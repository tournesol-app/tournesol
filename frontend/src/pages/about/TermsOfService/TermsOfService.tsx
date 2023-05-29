import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';

import AcceptableUse from './sections/AcceptableUse';
import AccountTerms from './sections/AccountTerms';
import CancellationAndTermination from './sections/CancellationAndTermination';
import Definitions from './sections/Definitions';
import Moderation from './sections/Moderation';

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
          <AcceptableUse />
          <Moderation />
          <CancellationAndTermination />
          <Typography
            variant="h4"
            fontStyle="italic"
            gutterBottom
            id="communications-with-association"
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
