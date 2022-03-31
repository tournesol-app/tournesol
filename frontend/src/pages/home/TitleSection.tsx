import React from 'react';
import { Box, Grid, Typography, useTheme } from '@mui/material';

interface Props {
  title: string;
  children: React.ReactNode;
}

const TitleSection = ({ title, children }: Props) => {
  const theme = useTheme();

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
          maxHeight: '380px',
          [theme.breakpoints.up('md')]: {
            py: '20px',
          },
          [theme.breakpoints.down('md')]: {
            maxHeight: '200px',
            marginBottom: '32px',
          },
          px: '40px',
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
        }}
      >
        <Typography
          variant="h1"
          sx={{
            fontWeight: 'bold',
            textAlign: 'left',
            maxWidth: '1000px',
            [theme.breakpoints.down('md')]: {
              textAlign: 'center',
              maxWidth: '100%',
            },
            float: 'right',
            marginBottom: '24px',
          }}
        >
          {title}
        </Typography>
        <Box
          display="flex"
          flexDirection="column"
          maxWidth="min(100%, 800px)"
          alignItems="flex-start"
          sx={{
            [theme.breakpoints.down('md')]: {
              alignSelf: 'center',
            },
          }}
        >
          {children}
        </Box>
      </Grid>
    </Grid>
  );
};

export default TitleSection;
