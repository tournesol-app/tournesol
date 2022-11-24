import React from 'react';
import { useTranslation, Trans } from 'react-i18next';

import {
  Typography,
  Stack,
  Paper,
  Button,
  Box,
  Grid,
  Alert,
} from '@mui/material';

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

      <Grid container flexDirection="column" alignItems="center" mb={6}>
        <Grid item lg={5} width="100%">
          <Box display="flex" justifyContent="space-evenly">
            <img
              width="80px"
              src="/logos/Fx-Browser-icon-fullColor.svg"
              alt="Mozilla Firefox browser logo."
            />
            <img
              width="80px"
              src="/logos/Chrome-Browser-icon-fullColor.svg"
              alt="Google Chrome browser logo."
            />
          </Box>
        </Grid>
      </Grid>

      <Grid container flexDirection="column" alignItems="center">
        <Grid item xl={9}>
          <Paper sx={{ p: 2 }}>
            <Stack direction="column" alignItems="center" spacing={2}>
              <Typography paragraph m={0}>
                {t('home.webExtensionDescription')}
              </Typography>
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
                <Alert severity="info" variant="filled">
                  <Trans
                    t={t}
                    i18nKey="home.extensionNotAvailableOnYourBrowser"
                  >
                    The extension is not available on your web browser. You may
                    use it on <b>Firefox</b>, <b>Google Chrome</b>.
                  </Trans>
                </Alert>
              )}
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default UseOurExtension;
