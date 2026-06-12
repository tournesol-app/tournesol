import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, AlertTitle } from '@mui/material';

import { ExternalLink } from 'src/components';
import { useIsExtensionInstalled } from 'src/hooks';
import { getWebExtensionUrl } from 'src/utils/extension';

import RateLaterOnVideoWatchedSetting from './RateLaterOnVideoWatchedSetting';

const RateLaterExtensionSection = () => {
  const { t } = useTranslation();
  const extensionInstalled = useIsExtensionInstalled();

  if (extensionInstalled) {
    return <RateLaterOnVideoWatchedSetting />;
  }

  return (
    <Alert severity="info" sx={{ width: '100%' }}>
      <AlertTitle>{t('ratelater.addFromYoutube')}</AlertTitle>
      <Trans t={t} i18nKey="ratelater.installExtensionToAddVideosEasily">
        Install our{' '}
        <ExternalLink
          href={getWebExtensionUrl() ?? getWebExtensionUrl('chrome')}
        >
          browser extension
        </ExternalLink>{' '}
        to add videos to your rate-later list directly from YouTube.
      </Trans>
    </Alert>
  );
};

export default RateLaterExtensionSection;
