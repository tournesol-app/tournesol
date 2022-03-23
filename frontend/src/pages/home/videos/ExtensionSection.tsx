import React from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Typography, Button, Box } from '@mui/material';
import { getWebExtensionUrl } from 'src/utils/extension';

// ExtensionSection is a paragraph displayed on the HomePage
// that automatically detects the user webbrowser to link
// to one of our extensions (Firefox & Chrome). If another
// browser is detected, then the user is shown that they
// can use our extension on Firefox or Chrome.
const ExtensionSection = () => {
  const { t } = useTranslation();
  const webExtensionUrl = getWebExtensionUrl();
  return (
    <Box
      display="flex"
      flexDirection="column"
      maxWidth="640px"
      alignItems="flex-start"
    >
      <Typography variant="h1">{t('home.useOurExtension')}</Typography>
      <Typography paragraph>{t('home.webExtensionDescription')}</Typography>
      {webExtensionUrl ? (
        <Button
          color="primary"
          variant="contained"
          component="a"
          href={webExtensionUrl}
          target="_blank"
        >
          {t('home.getTheExtensionButton')}
        </Button>
      ) : (
        <Typography color="primary" paragraph>
          <Trans t={t} i18nKey="home.extensionNotAvailableOnYourBrowser">
            The extension is not available on your webbrowser. You may use it on{' '}
            <b>Firefox</b>, <b>Google Chrome</b> or <b>Chromium</b>.
          </Trans>
        </Typography>
      )}
    </Box>
  );
};

export default ExtensionSection;
