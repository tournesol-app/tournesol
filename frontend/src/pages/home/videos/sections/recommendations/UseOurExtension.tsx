import React from 'react';
import { useTranslation, Trans } from 'react-i18next';

import { Typography, Button, Box, Grid, Alert } from '@mui/material';

import { getWebExtensionUrl } from 'src/utils/extension';
import SectionTitle from '../SectionTitle';

const UseOurExtension = () => {
  const { t } = useTranslation();
  const webExtensionUrl = getWebExtensionUrl();

  return (
    <Box>
      <Box my={6}>
        <SectionTitle title={t('home.useOurExtension')} dividerColor="#fff" />
      </Box>
      <Grid container flexDirection="column" alignItems="center" gap={2}>
        <Grid item xl={9}>
          <Typography paragraph m={0}>
            {t('home.webExtensionDescription')}
          </Typography>
        </Grid>
        <Grid item xl={9}>
          {webExtensionUrl ? (
            <Box display="flex" justifyContent="center">
              <Button
                color="primary"
                variant="contained"
                component="a"
                href={webExtensionUrl}
                target="_blank"
              >
                {t('home.getTheExtensionButton')}
              </Button>
            </Box>
          ) : (
            <Alert severity="info">
              <Trans t={t} i18nKey="home.extensionNotAvailableOnYourBrowser">
                The extension is not available on your web browser. You may use
                it on <b>Firefox</b>, <b>Google Chrome</b> or <b>Chromium</b>.
              </Trans>
            </Alert>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default UseOurExtension;
