import React from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Box, Grid, Typography, useTheme } from '@mui/material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { PRESIDENTIELLE_2022_POLL_NAME } from 'src/utils/constants';

const TitleSection = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  return (
    <Grid container>
      <Grid
        item
        xs={12}
        md={4}
        sx={{
          display: 'flex',
          justifyContent: 'center',
          maxWidth: '100%',
          maxHeight: '400px',
          [theme.breakpoints.down('md')]: {
            maxHeight: '300px',
          },
          padding: '40px',
          '& img': {
            maxWidth: '100%',
            maxHeight: '100%',
          },
        }}
      >
        <img
          src="/svg/Watering.svg"
          style={{
            maxWidth: '100%',
          }}
        />
      </Grid>
      <Grid
        item
        xs={12}
        md={8}
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: 3,
          [theme.breakpoints.down('md')]: {
            padding: 1,
          },
        }}
      >
        <Typography
          variant="h1"
          sx={{
            fontWeight: 'bold',
            textAlign: 'left',
            [theme.breakpoints.down('md')]: {
              textAlign: 'center',
            },
            float: 'right',
            marginBottom: '24px',
          }}
        >
          {pollName === PRESIDENTIELLE_2022_POLL_NAME
            ? t('home.beneficialCollaborativeDecisions')
            : t('home.collaborativeContentRecommendations')}
        </Typography>
        <Box
          display="flex"
          flexDirection="column"
          maxWidth="640px"
          alignItems="flex-start"
          sx={{
            [theme.breakpoints.down('md')]: {
              alignSelf: 'center',
            },
          }}
        >
          <Typography paragraph>
            <Trans t={t} i18nKey="home.tournesolPlatformDescription">
              Tournesol is an <strong>open source</strong> platform which aims
              to <strong>collaboratively</strong> identify top videos of public
              utility by eliciting contributors&apos; judgements on content
              quality. We hope to contribute to making today&apos;s and
              tomorrow&apos;s large-scale algorithms{' '}
              <strong>robustly beneficial</strong> for all of humanity.
            </Trans>
          </Typography>
        </Box>
      </Grid>
    </Grid>
  );
};

export default TitleSection;
