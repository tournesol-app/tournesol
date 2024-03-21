import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Box, Link, Typography } from '@mui/material';

const BeWellSurrounred = () => {
  const { t } = useTranslation();
  return (
    <Box
      sx={{
        '& li': { mt: 1 },
        '& a': { color: 'revert', textDecoration: 'revert' },
      }}
    >
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="be-well-surrounred"
      >
        {t('actionsPage.beWellSurrounded.beWellSurrounred')}
      </Typography>
      <ul>
        <li>
          <Typography>
            <Trans t={t} i18nKey="actionsPage.beWellSurrounded.joinDiscord">
              Join{' '}
              <Link
                href="https://discord.com/invite/TvsFB8RNBV"
                target="_blank"
                rel="noopener"
              >
                Tournesol Discord
              </Link>{' '}
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
      <Typography paragraph>
        {t('actionsPage.beWellSurrounded.takeCareMentalHealth')}
      </Typography>
    </Box>
  );
};

export default BeWellSurrounred;
