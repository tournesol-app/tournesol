import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Paper, Typography } from '@mui/material';

import SectionTitle from '../SectionTitle';

interface UseOurExtensionProps {
  titleColor?: string;
}

const InstallMobileApp = ({ titleColor }: UseOurExtensionProps) => {
  const { t } = useTranslation();

  return (
    <Box>
      <Box
        sx={{
          my: 6,
        }}
      >
        <SectionTitle
          title={t('home.installTheMobileAppTitle')}
          color={titleColor}
          dividerColor={titleColor}
          headingId="use-extension"
        />
      </Box>
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
                IMAGES ???
              </Grid>
              <Grid item xl={9}>
                <Typography
                  sx={{
                    m: 0,
                    textAlign: 'justify',
                  }}
                >
                  {t('home.installTheMobileApp')}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default InstallMobileApp;
