import React from 'react';
import { useTranslation } from 'react-i18next';
import { Grid, Typography, useTheme } from '@mui/material';

const TitleSection = () => {
  const theme = useTheme();
  const { t } = useTranslation();

  return (
    <Grid container>
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
            textAlign: 'right',
            fontSize: '340%',
            [theme.breakpoints.down('lg')]: {
              fontSize: '240%',
            },
            [theme.breakpoints.down('sm')]: {
              fontSize: '180%',
            },
            [theme.breakpoints.down('md')]: {
              textAlign: 'center',
            },
            float: 'right',
            margin: '24px 8px',
            maxWidth: 1000,
          }}
        >
          {t('home.collaborativeContentRecommendations')}
        </Typography>
      </Grid>
      <Grid
        item
        xs={12}
        md={4}
        sx={{
          display: 'flex',
          justifyContent: 'left',
          [theme.breakpoints.down('md')]: {
            justifyContent: 'center',
          },
          padding: 2,
        }}
      >
        <img
          src="/svg/Watering.svg"
          style={{
            maxWidth: '100%',
          }}
        />
      </Grid>{' '}
    </Grid>
  );
};

export default TitleSection;
