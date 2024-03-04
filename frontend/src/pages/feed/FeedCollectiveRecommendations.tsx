import React from 'react';
import { useSelector } from 'react-redux';
import { Redirect } from 'react-router-dom';

import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { useCurrentPoll } from 'src/hooks';
import { getDefaultRecommendationsSearchParams } from 'src/utils/userSettings';

const FeedCollectiveRecommendations = () => {
  const { name: pollName, options } = useCurrentPoll();
  const userSettings = useSelector(selectSettings).settings;

  const searchParams = getDefaultRecommendationsSearchParams(
    pollName,
    options,
    userSettings
  );

  return <Redirect to={`/recommendations${searchParams.toString()}`} />;
};

export default FeedCollectiveRecommendations;
