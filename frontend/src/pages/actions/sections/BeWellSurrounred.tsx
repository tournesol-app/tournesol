import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

import { ExternalLink } from 'src/components';
import { discordTournesolInviteUrl } from 'src/utils/url';

const BeWellSurrounred = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        gutterBottom
        id="be-well-surrounded"
        sx={{
          fontStyle: 'italic',
        }}
      >
        {t('actionsPage.beWellSurrounded.beWellSurrounded')}
      </Typography>
      <ul>
        <li>
          <Typography>
            <Trans t={t} i18nKey="actionsPage.beWellSurrounded.joinDiscord">
              Join{' '}
              <ExternalLink href={discordTournesolInviteUrl}>
                Tournesol Discord
              </ExternalLink>{' '}
              (say hi and present yourself).
            </Trans>
          </Typography>
        </li>
        <li>
          <Typography>
            {t('actionsPage.beWellSurrounded.joinGroups')}
          </Typography>
        </li>
      </ul>
      <Typography
        sx={{
          marginBottom: 2,
        }}
      >
        {t('actionsPage.beWellSurrounded.takeCareMentalHealth')}
      </Typography>
    </Box>
  );
};

export default BeWellSurrounred;
