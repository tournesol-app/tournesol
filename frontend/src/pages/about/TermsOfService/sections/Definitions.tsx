import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';
import { LooksOne, LooksTwo } from '@mui/icons-material';
import { Link } from 'react-router-dom';

const Definitions = () => {
  const { t } = useTranslation();
  return (
    <>
      <Box display="flex" gap={1}>
        <LooksOne />
        <Typography paragraph>
          {t('termsOfService.definitionsSection.anAccountRepresents')}
        </Typography>
      </Box>
      <Box display="flex" gap={1}>
        <LooksTwo />
        <Typography paragraph>
          <Trans t={t} i18nKey="termsOfService.definitionsSection.agreement">
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
        </Typography>
      </Box>
    </>
  );
};

export default Definitions;
