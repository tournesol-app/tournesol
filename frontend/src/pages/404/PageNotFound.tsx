import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box, Button, Typography } from '@mui/material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

const PageNotFound = () => {
  const { t } = useTranslation();
  const { options } = useCurrentPoll();
  const path = options?.path ?? '/';

  return (
    <Box
      sx={{
        backgroundColor: '#eeeeec',
        backgroundImage: "url('/svg/backgrounds/chandelier.svg')",
        backgroundPosition: 'top',
        backgroundRepeat: 'repeat-x',
        height: '100%',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          flexDirection: 'column',
          justifyContent: 'center',
          textAlign: 'center',
          pt: '280px',
          pb: 2,
        }}
      >
        <Typography variant="h2">
          {t('pageNotFound.sorryPageNotFound')}
        </Typography>
        <Typography variant="subtitle1">
          {t('pageNotFound.theRequestedAddressIsErroneous')}
        </Typography>
        <Box
          sx={{
            mt: 2,
          }}
        >
          <Button variant="contained" component={Link} to={path}>
            {t('pageNotFound.backToHomePage')}
          </Button>
        </Box>
      </Box>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'row',
          justifyContent: 'center',
        }}
      >
        <img src="/svg/Watering.svg" height="380px" />
      </Box>
    </Box>
  );
};

export default PageNotFound;
