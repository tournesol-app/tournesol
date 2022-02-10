import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import makeStyles from '@mui/styles/makeStyles';
import { Grid, Typography, Box } from '@mui/material';
import clsx from 'clsx';

import ExtensionSection from './ExtensionSection';
import ContributeSection from './ContributeSection';
import LightComparison from 'src/features/comparisons/LightComparison';
import { useLoginState } from '../../hooks';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
  },
  title: {
    fontWeight: 'bold',
    textAlign: 'left',
    [theme.breakpoints.down('md')]: {
      textAlign: 'center',
    },
    float: 'right',
    marginBottom: '24px',
    maxWidth: 1000,
  },
  titleContainer: {
    background: '#1282B2',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: 24,
    [theme.breakpoints.down('md')]: {
      padding: 4,
    },
  },
  imageContainer: {
    background: '#1282B2',
    display: 'flex',
    justifyContent: 'center',
    maxHeight: '400px',
    [theme.breakpoints.down('md')]: {
      justifyContent: 'center',
      maxHeight: '300px',
    },
    padding: 40,
    maxWidth: '100%',
    '& img': {
      maxWidth: '100%',
      maxHeight: '100%',
    },
  },
  container: {
    display: 'flex',
    justifyContent: 'center',
    padding: 32,
    [theme.breakpoints.down('md')]: {
      padding: '32px 8px 32px 8px',
    },
  },
  containerBlue: {
    backgroundColor: '#1282B2',
    color: 'white',
  },
}));

const HomePage = () => {
  const { isLoggedIn } = useLoginState();
  const { t } = useTranslation();
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Grid container>
        <Grid item xs={12} md={4} className={classes.imageContainer}>
          <img src="/svg/Watering.svg" />
        </Grid>
        <Grid item xs={12} md={8} className={classes.titleContainer}>
          <Typography
            variant="h1"
            color="primary.light"
            className={classes.title}
          >
            {t('home.collaborativeContentRecommendations')}
          </Typography>
          <Box
            display="flex"
            flexDirection="column"
            maxWidth="640px"
            alignItems="flex-start"
            color="white"
          >
            <Typography paragraph>
              <Trans t={t} i18nKey="home.tournesolPlatformDescription">
                Tournesol is an <strong>open source</strong> platform which aims
                to <strong>collaboratively</strong> identify top videos of
                public utility by eliciting contributors&apos; judgements on
                content quality. We hope to contribute to making today&apos;s
                and tomorrow&apos;s large-scale algorithms{' '}
                <strong>robustly beneficial</strong> for all of humanity.
              </Trans>
            </Typography>
          </Box>
        </Grid>
        {isLoggedIn && (
          <>
            <Grid
              item
              xs={12}
              className={classes.container}
              sx={{ color: '#1282B2', bgcolor: 'white' }}
            >
              <Grid
                container
                direction="column"
                textAlign="center"
                alignItems="center"
              >
                <Grid item>
                  <Typography variant="h1" component="h1">
                    {t('home.giveYourOpinionNow')}
                  </Typography>
                </Grid>
                <Grid item>
                  <Typography variant="h3" component="h3">
                    {t('home.and')}
                  </Typography>
                </Grid>
                <Grid item>
                  <Typography variant="h3" component="h3">
                    {t('home.makeTheRecommendationsBetter')}
                  </Typography>
                </Grid>
              </Grid>
            </Grid>
            <Grid item xs={12} className={classes.container}>
              <LightComparison />
            </Grid>
          </>
        )}
        <Grid
          item
          xs={12}
          className={clsx(classes.container, {
            [classes.containerBlue]: isLoggedIn,
          })}
        >
          <ExtensionSection />
        </Grid>
        <Grid
          item
          xs={12}
          className={clsx(classes.container, {
            [classes.containerBlue]: !isLoggedIn,
          })}
        >
          <ContributeSection />
        </Grid>
      </Grid>
    </div>
  );
};

export default HomePage;
