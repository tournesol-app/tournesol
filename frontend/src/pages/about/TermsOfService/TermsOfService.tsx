import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Link, Paper, Typography } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';

import AcceptableUse from './sections/AcceptableUse';
import AccountTerms from './sections/AccountTerms';
import CancellationAndTermination from './sections/CancellationAndTermination';
import ChangesToTheseTerms from './sections/ChangesToTheseTerms';
import CommunicationsWithAssociation from './sections/CommunicationsWithAssociation';
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
          <CommunicationsWithAssociation />
          <ChangesToTheseTerms />
          <Paper sx={{ p: 2 }}>
            <Typography paragraph>
              {t('terms.copying.thisDocumentIsInspiredByTheGitHubTos')}
            </Typography>
            <Typography paragraph mb={0}>
              <Trans
                t={t}
                i18nKey="terms.copying.thePresentTextsAreDedicatedToThePublicDomain"
              >
                The present texts are dedicated to the Public Domain, as stated
                by the license{' '}
                <Link
                  href="https://creativecommons.org/publicdomain/zero/1.0/"
                  target="_blank"
                  rel="noopener"
                  sx={{
                    color: 'revert',
                    textDecoration: 'revert',
                  }}
                >
                  Creative Commons Zero v1.0 Universal (CC0 1.0)
                </Link>
                .
              </Trans>
            </Typography>
          </Paper>
        </Box>
      </ContentBox>
    </>
  );
};

export default TermsOfServicePage;
