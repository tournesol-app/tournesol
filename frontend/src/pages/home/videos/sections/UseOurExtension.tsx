import React from 'react';
import { useTranslation, Trans } from 'react-i18next';

import { Alert, Box, Button, Grid, Paper, Typography } from '@mui/material';
import { Extension } from '@mui/icons-material';

import { getWebExtensionUrl } from 'src/utils/extension';
import SectionTitle from './SectionTitle';

interface UseOurExtensionProps {
  titleColor?: string;
}

const UseOurExtension = ({ titleColor }: UseOurExtensionProps) => {
  const { t } = useTranslation();
  const webExtensionUrl = getWebExtensionUrl();

  return (
    <Box>
      <SectionTitle
        title={t('home.useOurExtension')}
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
                width="64px"
                src="/logos/Fx-Browser-icon-fullColor.svg"
                alt="Mozilla Firefox browser logo."
              />
              <img
                width="64px"
                src="/logos/Chrome-Browser-icon-fullColor.svg"
                alt="Google Chrome browser logo."
              />
              <img
                width="64px"
                src="/logos/Edge-Browser-icon-fullColor.svg"
                alt="Microsoft Edge browser logo."
              />
            </Box>
          </Grid>
          <Grid item>
            <Typography
              sx={{
                m: 0,
                textAlign: 'justify',
              }}
            >
              {t('home.webExtensionDescription')}
            </Typography>
          </Grid>
          <Grid item width="100%">
            {webExtensionUrl ? (
              <Button
                fullWidth
                color="primary"
                variant="contained"
                component="a"
                href={webExtensionUrl}
                startIcon={<Extension />}
              >
                {t('home.getTheExtensionButton')}
              </Button>
            ) : (
              <Alert severity="info" variant="filled">
                <Trans t={t} i18nKey="home.extensionNotAvailableOnYourBrowser">
                  The extension is not available on your web browser. You may
                  use it on <b>Firefox</b>, <b>Google Chrome</b>.
                </Trans>
              </Alert>
            )}
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default UseOurExtension;
