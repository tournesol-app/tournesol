import React, { useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Typography, Button, Box } from '@mui/material';

const getWebBrowser = () => {
  if (navigator.userAgent.includes('Chrome/')) return 'chrome';
  if (navigator.userAgent.includes('Chromium/')) return 'chromium';
  if (navigator.userAgent.includes('Firefox/')) return 'firefox';
  return 'other';
};

// ExtensionSection is a paragraph displayed on the HomePage
// that automatically detects the user webbrowser to link
// to one of our extensions (Firefox & Chrome). If another
// browser is detected, then the user is shown that they
// can use our extension on Firefox or Chrome.
const ExtensionSection = () => {
  const { t } = useTranslation();
  const [browser] = useState(getWebBrowser());
  return (
    <Box
      display="flex"
      flexDirection="column"
      color="white"
      maxWidth="640px"
      alignItems="flex-start"
    >
      <Typography variant="h1">{t('home.useOurExtension')}</Typography>
      <Typography paragraph>{t('home.webExtensionDescription')}</Typography>
      {browser !== 'other' ? (
        <Button
          color="primary"
          variant="contained"
          component="a"
          href={
            browser == 'firefox'
              ? 'https://addons.mozilla.org/en-US/firefox/addon/tournesol-extension/'
              : 'https://chrome.google.com/webstore/detail/tournesol-extension/nidimbejmadpggdgooppinedbggeacla'
          }
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
