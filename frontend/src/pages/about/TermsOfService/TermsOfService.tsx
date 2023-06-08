import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';

import AcceptableUse from './sections/AcceptableUse';
import AccountTerms from './sections/AccountTerms';
import CancellationAndTermination from './sections/CancellationAndTermination';
import ChangesToTheseTerms from './sections/ChangesToTheseTerms';
import CommunicationWithAssociation from './sections/CommunicationWithAssociation';
import Definitions from './sections/Definitions';
import Moderation from './sections/Moderation';

const TermsOfServicePage = () => {
  const { t } = useTranslation();
  return (
    <>
      <ContentHeader
        title={`${t('menu.about')} > ${t('terms.termsOfService')}`}
      />
      <ContentBox maxWidth="md">
        <Typography variant="h3" gutterBottom>
          {t('terms.termsOfService')}
        </Typography>
        <Box display="flex" flexDirection="column" gap={4}>
          <Definitions />
          <AccountTerms />
          <AcceptableUse />
          <Moderation />
          <CancellationAndTermination />
          <CommunicationWithAssociation />
          <ChangesToTheseTerms />
        </Box>
      </ContentBox>
    </>
  );
};

export default TermsOfServicePage;
