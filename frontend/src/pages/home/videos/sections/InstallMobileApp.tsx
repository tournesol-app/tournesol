import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Paper, Typography } from '@mui/material';

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
      <Paper sx={{ p: 2 }}>
        <Grid
          container
          sx={{
            flexDirection: 'column',
            alignItems: 'center',
            gap: 3,
          }}
        >
          <Grid item>
            <Typography
              sx={{
                m: 0,
                textAlign: 'justify',
              }}
            >
              {t('home.installTheMobileAppDescription')}
            </Typography>
          </Grid>
          <Grid
            item
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
              <a
                href={googlePlayStoreMobileAppUrl}
                target="_blank"
                rel="noreferrer"
              >
                <img
                  width="200px"
                  src="/logos/GetItOnGooglePlay_Badge_Web_color_English.png"
                  alt="GetItOnGooglePlay Badge"
                />
              </a>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default InstallMobileApp;
