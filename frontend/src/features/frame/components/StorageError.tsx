import React from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Box, Typography } from '@mui/material';
import { ExternalLink } from 'src/components';
import { getWebBrowser } from 'src/utils/extension';

const ChromeInstructions = () => {
  const { t } = useTranslation();
  return (
    <>
      <Typography variant="h6" gutterBottom>
        {t('frame.onChromeOrDerivatives')}
      </Typography>
      <Typography gutterBottom>
        <Trans t={t} i18nKey="frame.addWebsiteToChromeExceptions">
          On the settings page related to Cookies and other site data (
          <code>{{ page: 'chrome://settings/cookies' }}</code>), add{' '}
          <strong>{{ host: location.host }}</strong> to the list of{' '}
          <strong>&quot;Sites that can always use cookies&quot;</strong>.
        </Trans>
      </Typography>
      <Typography>
        <Trans t={t} i18nKey="frame.findMoreDetailsOnPage">
          Find more details on{' '}
          <ExternalLink
            href="https://support.google.com/chrome/answer/95647"
            target="_blank"
          >
            this page
          </ExternalLink>
          .
        </Trans>
      </Typography>
    </>
  );
};

const FirefoxInstructions = () => {
  const { t } = useTranslation();
  return (
    <>
      <Typography variant="h6" gutterBottom>
        {t('frame.onFirefox')}
      </Typography>
      <Typography gutterBottom>
        <Trans t={t} i18nKey="frame.addWebsiteToFirefoxExceptions">
          On the settings page about Browser Privacy (
          <code>{{ page: 'about:preferences#privacy' }}</code>), in the section
          about <strong>{'Cookies and site data'}</strong>, click on{' '}
          <strong>{'Manage Exceptions'}</strong>.<br />
          Then, add <strong>{{ host: location.host }}</strong> to the list of
          websites that are always allowed to use cookies and site data.
        </Trans>
      </Typography>
    </>
  );
};

const StorageError = () => {
  const { t } = useTranslation();
  const browser = getWebBrowser();

  return (
    <Box maxWidth="sm" my={3} mx="auto">
      <img src="/svg/LogoSmall.svg" alt="logo" />
      <Typography variant="h4" gutterBottom>
        {t('frame.tournesolInFrameIsCurrentlyBlocked')}
      </Typography>
      <Typography my={2}>
        <Trans t={t} i18nKey="frame.thirdPartyStorageIsBlockedAddException">
          It seems that using third-party storage is blocked on your browser. In
          order to access all features provided by the Tournesol web extension,
          including the integration with YouTube, you can simply add an
          exception about the website <strong>{{ host: location.host }}</strong>{' '}
          in your browser settings, by following the instructions below.
        </Trans>
      </Typography>
      <Box my={2}>
        {browser === 'firefox' ? (
          <FirefoxInstructions />
        ) : (
          <ChromeInstructions />
        )}
      </Box>
      <Typography my={2}>
        {t('frame.storageErrorReloadPageAfterApplyingChanges')}
      </Typography>
    </Box>
  );
};

export default StorageError;
