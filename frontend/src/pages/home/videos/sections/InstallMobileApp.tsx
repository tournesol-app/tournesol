import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Paper, Typography, Button } from '@mui/material';
import { InstallMobile } from '@mui/icons-material';

import SectionTitle from './SectionTitle';

interface UseOurExtensionProps {
  titleColor?: string;
}

const InstallMobileApp = ({ titleColor }: UseOurExtensionProps) => {
  const { t } = useTranslation();
  const googlePlayStoreMobileAppUrl =
    'https://play.google.com/store/apps/details?id=app.tournesol.twa';

  return (
    <Box>
      <SectionTitle
        title={t('home.installTheMobileAppTitle')}
        color={titleColor}
        dividerColor={titleColor}
        headingId="use-extension"
      />
      <Grid
        container
        sx={{
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Grid item xl={9}>
          <Paper sx={{ p: 2 }}>
            <Grid
              container
              sx={{
                flexDirection: 'column',
                alignItems: 'center',
                gap: 3,
              }}
            >
              <Grid
                item
                lg={7}
                sx={{
                  width: '100%',
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-evenly',
                  }}
                >
                  <img
                    width="256px"
                    src="/logos/Google_Play_2022_logo.svg"
                    alt="Google Play Store logo."
                  />
                </Box>
              </Grid>
              <Grid item xl={9}>
                <Typography
                  sx={{
                    m: 0,
                    textAlign: 'justify',
                  }}
                >
                  {t('home.installTheMobileAppDescription')}
                </Typography>
              </Grid>
              <Grid item xl={9}>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'center',
                  }}
                >
                  <Button
                    color="primary"
                    variant="contained"
                    component="a"
                    href={googlePlayStoreMobileAppUrl}
                    startIcon={<InstallMobile />}
                  >
                    {t('home.installTheMobileAppButton')}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default InstallMobileApp;
