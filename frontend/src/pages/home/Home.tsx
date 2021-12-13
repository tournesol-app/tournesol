import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import { Grid, Typography, Box } from '@material-ui/core';

import ExtensionSection from './ExtensionSection';
import ContributeSection from './ContributeSection';
import PublicDownloadSection from './PublicDownloadSection'

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    paddingBottom: 32,
  },
  wateringSunflower: {
    maxWidth: '100%',
  },
  title: {
    color: '#ffffff',
    textAlign: 'right',
    fontSize: '400%',
    [theme.breakpoints.down('md')]: {
      fontSize: '300%',
    },
    [theme.breakpoints.down('xs')]: {
      fontSize: '200%',
    },
    [theme.breakpoints.down('sm')]: {
      textAlign: 'center',
    },
    float: 'right',
    marginTop: 24,
    marginBottom: 24,
    maxWidth: 1000,
  },
  titleContainer: {
    background: '#1282B2',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: 24,
    [theme.breakpoints.down('sm')]: {
      padding: 4,
    },
  },
  imageContainer: {
    background: '#1282B2',
    display: 'flex',
    justifyContent: 'left',
    [theme.breakpoints.down('sm')]: {
      justifyContent: 'center',
    },
    padding: 16,
  },
  container: {
    display: 'flex',
    justifyContent: 'center',
    padding: 32,
    [theme.breakpoints.down('sm')]: {
      padding: '32px 8px 32px 8px',
    },
  },
}));

const HomePage = () => {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Grid container>
        <Grid item xs={12} md={8} className={classes.titleContainer}>
          <Typography variant="h1" className={classes.title}>
            Collaborative Content Recommendations
          </Typography>
        </Grid>
        <Grid item xs={12} md={4} className={classes.imageContainer}>
          <img src="/svg/Watering.svg" className={classes.wateringSunflower} />
        </Grid>
        <Grid item xs={12} className={classes.container}>
          <Box
            display="flex"
            flexDirection="column"
            maxWidth="640px"
            alignItems="flex-start"
          >
            <Typography variant="h1">What is Tournesol?</Typography>
            <Typography paragraph>
              Tournesol is an <strong>open source</strong> platform which aims
              to <strong>collaboratively</strong> identify top videos of public
              utility by eliciting contributors&apos; judgements on content
              quality. We hope to contribute to making today&apos;s and
              tomorrow&apos;s large-scale algorithms{' '}
              <strong>robustly beneficial</strong> for all of humanity.
            </Typography>
          </Box>
        </Grid>
        <Grid
          item xs={12} className={classes.container}
          style={{ background: '#1282B2' }}
        >
          <ExtensionSection />
        </Grid>
        <Grid item xs={12} className={classes.container}>
          <ContributeSection />
        </Grid>
        <Grid
          item xs={12} className={classes.container}
          style={{ background: '#1282B2' }}
        >
          <PublicDownloadSection />
        </Grid>
      </Grid>
    </div>
  );
};

export default HomePage;
