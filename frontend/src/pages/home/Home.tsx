import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import { Grid, Typography } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
  },
  rectangle67: {
    width: '100%',
    padding: 24,
    background: '#1282B2',
  },
  content: {
    padding: 24,
    [theme.breakpoints.down('sm')]: {
      padding: 8,
    },
    marginBottom: 32,
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
    fontFamily: 'Poppins',
    maxWidth: 1000,
  },
  titleContainer: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: 24,
    [theme.breakpoints.down('sm')]: {
      padding: 4,
    },
  },
  imageContainer: {
    display: 'flex',
    justifyContent: 'left',
    [theme.breakpoints.down('sm')]: {
      justifyContent: 'center',
    },
  },
  intro: {
    maxWidth: 640,
    fontFamily: 'Poppins',
    textAlign: 'justify',
  },
  introContainer: {
    display: 'flex',
    justifyContent: 'center',
    marginTop: 32,
  },
}));

const HomePage = () => {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Grid container className={classes.rectangle67}>
        <Grid item xs={12} md={8} className={classes.titleContainer}>
          <Typography variant="h1" className={classes.title}>
            Collaborative Content Recommendations
          </Typography>
        </Grid>
        <Grid item xs={12} md={4} className={classes.imageContainer}>
          <img src="/svg/Watering.svg" className={classes.wateringSunflower} />
        </Grid>
      </Grid>
      <Grid container className={classes.content}>
        <Grid item xs={12} className={classes.introContainer}>
          <Typography paragraph className={classes.intro}>
            Tournesol is an <strong>open source</strong> platform which aims to{' '}
            <strong>collaboratively</strong> identify top videos of public
            utility by eliciting contributors&apos; judgements on content
            quality. We hope to contribute to making today&apos;s and
            tomorrow&apos;s large-scale algorithms{' '}
            <strong>robustly beneficial</strong> for all of humanity.
          </Typography>
        </Grid>
      </Grid>
    </div>
  );
};

export default HomePage;
