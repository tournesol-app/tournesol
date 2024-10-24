import React from 'react';
import { useSelector } from 'react-redux';
import { Redirect } from 'react-router-dom';

import { useCurrentPoll, useLoginState } from 'src/hooks';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { getFeedTopItemsDefaultSearchParams } from 'src/utils/userSettings';

const PwaEntryPoint = () => {
  const { name: pollName, options } = useCurrentPoll();
  const langsAutoDiscovery = options?.defaultRecoLanguageDiscovery ?? false;
  const userSettings = useSelector(selectSettings)?.settings;
  const { isLoggedIn } = useLoginState();

  if (isLoggedIn) {
    return <Redirect to="/feed/foryou" />;
  }

  return (
    <Redirect
      to={`/feed/top${getFeedTopItemsDefaultSearchParams(
        pollName,
        options,
        userSettings,
        langsAutoDiscovery
      )}`}
    />
  );
};

export default PwaEntryPoint;
