import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';
import { LooksOne, LooksTwo, Looks3, Looks4 } from '@mui/icons-material';
import { Link } from 'react-router-dom';

const DefinitionSection = ({
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
    <>
      <DefinitionSection
        icon={<LooksOne />}
        text={t('termsOfService.definitionsSection.account')}
      />
      <DefinitionSection
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
      <DefinitionSection
        icon={<Looks3 />}
        text={t('termsOfService.definitionsSection.association')}
      />
      <DefinitionSection
        icon={<Looks4 />}
        text={t('termsOfService.definitionsSection.user')}
      />
    </>
  );
};

export default Definitions;
