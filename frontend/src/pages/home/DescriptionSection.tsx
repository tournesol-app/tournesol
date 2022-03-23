import React from 'react';

import { Trans, useTranslation } from 'react-i18next';
import { Typography, Box } from '@mui/material';

const DescriptionSection = () => {
  const { t } = useTranslation();

  return (
    <Box
      display="flex"
      flexDirection="column"
      maxWidth="640px"
      alignItems="flex-start"
    >
      <Typography variant="h1">{t('home.whatIsTournesol')}</Typography>
      <Typography paragraph>
        <Trans t={t} i18nKey="home.tournesolPlatformDescription">
          Tournesol is an <strong>open source</strong> platform which aims to{' '}
          <strong>collaboratively</strong> identify top videos of public utility
          by eliciting contributors&apos; judgements on content quality. We hope
          to contribute to making today&apos;s and tomorrow&apos;s large-scale
          algorithms <strong>robustly beneficial</strong> for all of humanity.
        </Trans>
      </Typography>
    </Box>
  );
};

export default DescriptionSection;
