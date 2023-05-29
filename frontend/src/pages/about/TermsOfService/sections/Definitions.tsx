import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';
import {
  LooksOne,
  LooksTwo,
  Looks3,
  Looks4,
  Looks5,
} from '@mui/icons-material';
import { Link } from 'react-router-dom';

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
        {t('termsOfService.definitions')}
      </Typography>
      <Section
        icon={<LooksOne />}
        text={t('termsOfService.definitionsSection.account')}
      />
      <Section
        icon={<LooksTwo />}
        text={
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
        }
      />
      <Section
        icon={<Looks3 />}
        text={t('termsOfService.definitionsSection.association')}
      />{' '}
      <Section
        icon={<Looks4 />}
        text={t('termsOfService.definitionsSection.service')}
      />
      <Section
        icon={<Looks5 />}
        text={t('termsOfService.definitionsSection.user')}
      />
    </Box>
  );
};

export default Definitions;
