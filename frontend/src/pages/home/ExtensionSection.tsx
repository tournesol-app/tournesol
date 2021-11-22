import React, { useState } from 'react';

import { Typography, Button, Box } from '@material-ui/core';

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
  const [browser] = useState(getWebBrowser());
  return (
    <Box
      display="flex"
      flexDirection="column"
      color="white"
      maxWidth="640px"
      alignItems="flex-start"
    >
      <Typography variant="h1">Use our extension!</Typography>
      <Typography paragraph>
        When using the extension, you will find videos recommended by
        Tournesol&apos;s community directly on your Youtube home page. You can
        also add a video in your rate later list or immediatly rate the video
        with just a few clicks.
      </Typography>
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
          Get the extension
        </Button>
      ) : (
        <Typography color="primary" paragraph>
          The extension is not available on your webbrowser. You may use it on{' '}
          <b>Firefox</b>, <b>Google Chrome</b> or <b>Chromium</b>.
        </Typography>
      )}
    </Box>
  );
};

export default ExtensionSection;
