import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Link, Typography } from '@mui/material';

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
        {t('termsOfService.changesToTheseTerms.changesToTheseTerms')}
      </Typography>
      <Box my={2}>
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('termsOfService.shortVersion')}</strong>
          </AlertTitle>
          {t('termsOfService.changesToTheseTerms.shortVersion')}
        </Alert>
      </Box>
      <Typography paragraph>
        <Trans
          t={t}
          i18nKey="termsOfService.changesToTheseTerms.weMayAmendTheseTerms"
        >
          We may amend these Terms of Service at any time. We will notify the
          Users of material changes to this Agreement, at least 30 days prior to
          the change taking effect by posting a notice on our website or sending
          email to the email address specified in your Account. User&apos;s
          continued use of the Service after those 30 days constitutes agreement
          to those revisions of this Agreement. For any other non-impacting
          modifications, User&apos;s continued use of the Service constitutes
          agreement to our revisions of these Terms of Service. You can view all
          changes to these Terms in our{' '}
          <Link
            href={githubTournesolTermsOfServiceHistoryUrl}
            target="_blank"
            rel="noopener"
            sx={{
              color: 'revert',
              textDecoration: 'revert',
            }}
          >
            GitHub repository.
          </Link>
        </Trans>
      </Typography>
    </Box>
  );
};

export default ChangesToTheseTerms;
