import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';

import { ExternalLink } from 'src/components';
import { githubTournesolTermsOfServiceHistoryUrl } from 'src/utils/url';

const ChangesToTheseTerms = () => {
  const { t } = useTranslation();

  return (
    <Box>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="changes-to-these-terms"
      >
        {t('terms.changesToTheseTerms.changesToTheseTerms')}
      </Typography>
      <Box my={2}>
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('terms.shortVersion')}</strong>
          </AlertTitle>
          {t('terms.changesToTheseTerms.shortVersion')}
        </Alert>
      </Box>
      <Typography paragraph>
        {t('terms.changesToTheseTerms.weMayAmendTheseTermsAtAnyTime')}
      </Typography>
      <Typography paragraph>
        <Trans t={t} i18nKey="terms.changesToTheseTerms.weWillNotifyTheUsers">
          We will notify the Users of material changes to this Agreement, at
          least 30 days prior to the change taking effect by posting a notice on
          our website or sending email to the email address specified in your
          Account. User&apos;s continued use of the Service after those 30 days
          constitutes agreement to those revisions of this Agreement. For any
          other non-impacting modifications, User&apos;s continued use of the
          Service constitutes agreement to our revisions of these Terms of
          Service. You can view all changes to these Terms in our{' '}
          <ExternalLink href={githubTournesolTermsOfServiceHistoryUrl}>
            GitHub repository
          </ExternalLink>
          .
        </Trans>
      </Typography>
    </Box>
  );
};

export default ChangesToTheseTerms;
