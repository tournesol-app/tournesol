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
        backgroundImage: "url('/svg/backgrounds/chandelier.svg')",
        backgroundPosition: 'center',
        backgroundRepeatY: 'no-repeat',
        height: '100%',
      }}
    >
      <Box
        display="flex"
        alignItems="center"
        flexDirection="column"
        justifyContent="center"
        textAlign="center"
        pt={22}
        pb={2}
      >
        <Typography variant="h2">
          {t('pageNotFound.sorryPageNotFound')}
        </Typography>
        <Typography variant="subtitle1">
          {t('pageNotFound.theRequestedAddressIsErroneous')}
        </Typography>
        <Box mt={2}>
          <Button variant="contained" component={Link} to={path}>
            {t('pageNotFound.backToHomePage')}
          </Button>
        </Box>
      </Box>
      <Box display="flex" flexDirection="row" justifyContent="center">
        <img src="/svg/Watering.svg" height="380px" />
      </Box>
    </Box>
  );
};

export default PageNotFound;
