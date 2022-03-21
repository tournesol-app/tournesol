import React from 'react';
import { Box, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';

const PageNotFound = () => {
  const { t } = useTranslation();
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
        pt={26}
        pb={2}
      >
        <Typography variant="h2">
          {t('pageNotFound.sorryPageNotFound')}
        </Typography>
        <Typography variant="subtitle1">
          {t('pageNotFound.theRequestedAddressIsErroneous')}
        </Typography>
      </Box>
      <Box
        display="flex"
        flexDirection="row"
        justifyContent="center"
        alignItems="flex-end"
      >
        <img src="/svg/Watering.svg" height="400px" />
      </Box>
    </Box>
  );
};

export default PageNotFound;
