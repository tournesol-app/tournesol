import React from 'react';
import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';

import { useCurrentPoll, useLoginState } from 'src/hooks';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { getFeedTopItemsDefaultSearchParams } from 'src/utils/userSettings';

const PwaEntryPoint = () => {
  const { name: pollName, options } = useCurrentPoll();
  const langsAutoDiscovery = options?.defaultRecoLanguageDiscovery ?? false;
  const userSettings = useSelector(selectSettings)?.settings;
  const { isLoggedIn } = useLoginState();

  if (isLoggedIn) {
    return <Navigate to="/feed/foryou" replace />;
  }

  return (
    <Navigate
      to={`/feed/top${getFeedTopItemsDefaultSearchParams(
        pollName,
        options,
        userSettings,
        langsAutoDiscovery
      )}`}
      replace
    />
  );
};

export default PwaEntryPoint;
