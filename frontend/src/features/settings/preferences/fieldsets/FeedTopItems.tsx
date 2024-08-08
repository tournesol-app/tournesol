import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Grid } from '@mui/material';

import SettingsHeading from 'src/features/settings/preferences/SettingsHeading';

import ItemsLanguages from '../fields/ItemsLanguages';

interface FeedForYouProps {
  scope: string;
  topItemsLanguages: string[];
  setTopItemsLangauges: (target: string[]) => void;
}

const FeedTopItems = ({
  scope,
  topItemsLanguages,
  setTopItemsLangauges,
}: FeedForYouProps) => {
  const { t } = useTranslation();
  return (
    <>
      <Grid item>
        <SettingsHeading
          id={`${scope}-feed-top`}
          text={t('videosUserSettingsForm.feed.topItems.feedTopVideos')}
        />
      </Grid>
      <Grid item>
        <Alert severity="info">
          {t(
            'videosUserSettingsForm.feed.topItems.customizeItemsAppearingInTheFeedTopVideos'
          )}
        </Alert>
      </Grid>
      <Grid item>
        <ItemsLanguages
          label={t('videosUserSettingsForm.feed.topItems.topVideosLanguages')}
          helpText={t(
            'videosUserSettingsForm.feed.topItems.keepEmptyToSelectAllLang'
          )}
          value={topItemsLanguages}
          onChange={setTopItemsLangauges}
        />
      </Grid>
    </>
  );
};

export default FeedTopItems;
