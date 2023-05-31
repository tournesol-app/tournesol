import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';
import {
  LooksOne,
  LooksTwo,
  Looks3,
  Looks4,
  Looks5,
  Looks6,
} from '@mui/icons-material';

const Section = ({
  icon,
  text,
}: {
  icon: React.ReactElement;
  text: string | React.ReactElement;
}) => {
  return (
    <Box display="flex" gap={1}>
      {icon}
      <Typography paragraph>{text}</Typography>
    </Box>
  );
};

const Definitions = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography variant="h4" fontStyle="italic" gutterBottom id="definitions">
        {t('termsOfService.definitions.definitions')}
      </Typography>
      <Box my={2}>
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('termsOfService.shortVersion')}</strong>
          </AlertTitle>
          {t('termsOfService.definitions.shortVersion')}
        </Alert>
      </Box>
      <Section
        icon={<LooksOne />}
        text={t('termsOfService.definitions.account')}
      />
      <Section
        icon={<LooksTwo />}
        text={
          <Trans t={t} i18nKey="termsOfService.definitions.agreement">
            The &quot;Agreement&quot; refers, collectively, to all the terms,
            conditions, notices contained or referenced in this document (the
            &quot;Terms of Service&quot; or the Terms) and all other operating
            rules, policies (including the Tournesol Privacy Policy, available
            at{' '}
            <Link to="/about/privacy_policy">
              https://tournesol.app/about/privacy_policy
            </Link>
            ).
          </Trans>
        }
      />
      <Section
        icon={<Looks3 />}
        text={t('termsOfService.definitions.association')}
      />
      <Section
        icon={<Looks4 />}
        text={t('termsOfService.definitions.content')}
      />
      <Section
        icon={<Looks5 />}
        text={t('termsOfService.definitions.service')}
      />
      <Section icon={<Looks6 />} text={t('termsOfService.definitions.user')} />
    </Box>
  );
};

export default Definitions;
