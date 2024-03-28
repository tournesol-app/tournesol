import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';

import { InternalLink } from 'src/components';

const Section = ({
  text,
  num,
}: {
  num: number;
  text: string | React.ReactElement;
}) => {
  return (
    <Box display="flex" gap={1}>
      <Typography
        px={2}
        color="secondary.main"
        fontSize="1.2em"
        fontWeight="bold"
      >
        {num}
      </Typography>
      <Typography
        paragraph
        sx={{
          '& span.pre': {
            unicodeBidi: 'embed',
            fontFamily: 'monospace',
            whiteSpace: 'pre',
          },
        }}
      >
        {text}
      </Typography>
    </Box>
  );
};

const Definitions = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography variant="h4" fontStyle="italic" gutterBottom id="definitions">
        {t('terms.definitions.definitions')}
      </Typography>
      <Box my={2}>
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('terms.shortVersion')}</strong>
          </AlertTitle>
          {t('terms.definitions.shortVersion')}
        </Alert>
      </Box>
      <Section num={1} text={t('terms.definitions.account')} />
      <Section
        num={2}
        text={
          <Trans t={t} i18nKey="terms.definitions.agreement">
            The &quot;Agreement&quot; refers, collectively, to all the terms,
            conditions, notices contained or referenced in this document (the
            &quot;Terms of Service&quot; or the Terms) and all other operating
            rules, policies (including our{' '}
            <InternalLink to="/about/privacy_policy">
              Privacy Policy
            </InternalLink>
            ) and procedures that we may publish from time to time on the
            website.
          </Trans>
        }
      />
      <Section num={3} text={t('terms.definitions.association')} />
      <Section num={4} text={t('terms.definitions.content')} />
      <Section num={5} text={t('terms.definitions.service')} />
      <Section num={6} text={t('terms.definitions.user')} />
      <Section
        num={7}
        text={
          <Trans t={t} i18nKey="terms.definitions.website">
            The &quot;Website&quot; refers to the Tournesol project&apos;s
            website located at <InternalLink to="/">tournesol.app</InternalLink>
            , and all content and services provided by the Association at or
            through the Website. It also refers to the Association-owned
            subdomains of tournesol.app, such as{' '}
            <span className="pre">api.tournesol.app</span>. Occasionally,
            websites owned by the Association may provide different or
            additional terms of service. If those additional terms conflict with
            this Agreement, the more specific terms apply to the relevant page
            or service.
          </Trans>
        }
      />
    </Box>
  );
};

export default Definitions;
