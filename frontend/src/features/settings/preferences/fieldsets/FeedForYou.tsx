import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Grid } from '@mui/material';

import SettingsHeading from 'src/features/settings/preferences/SettingsHeading';
import { BlankEnum, FeedForyou_dateEnum } from 'src/services/openapi';

import FeedForYouDate from '../fields/FeedForYouDate';
import ItemsLanguages from '../fields/ItemsLanguages';
import BooleanField from '../fields/generics/BooleanField';

interface FeedForYouProps {
  scope: string;
  forYouLanguages: string[];
  setForYouLanguages: (target: string[]) => void;
  forYouUploadDate: FeedForyou_dateEnum | BlankEnum;
  setForYouUploadDate: (target: FeedForyou_dateEnum | BlankEnum) => void;
  forYouUnsafe: boolean;
  setForYouUnsafe: (target: boolean) => void;
  forYouExcludeCompared: boolean;
  setForYouExcludeCompared: (target: boolean) => void;
}

const FeedForYou = ({
  scope,
  forYouLanguages,
  setForYouLanguages,
  forYouUploadDate,
  setForYouUploadDate,
  forYouUnsafe,
  setForYouUnsafe,
  forYouExcludeCompared,
  setForYouExcludeCompared,
}: FeedForYouProps) => {
  const { t } = useTranslation();
  return (
    <>
      <Grid item>
        <SettingsHeading
          id={`${scope}-feed-foryou`}
          text={t('videosUserSettingsForm.feed.forYou.feedForYou')}
        />
      </Grid>
      <Grid item>
        <Alert severity="info">
          {t(
            'videosUserSettingsForm.feed.forYou.customizeItemsAppearingInTheFeedForYou'
          )}
        </Alert>
      </Grid>
      <Grid item>
        <ItemsLanguages
          label={t('videosUserSettingsForm.feed.forYou.forYouVideosLanguages')}
          helpText={t(
            'videosUserSettingsForm.feed.forYou.keepEmptyToSelectAllLang'
          )}
          value={forYouLanguages}
          onChange={setForYouLanguages}
        />
      </Grid>
      <Grid item>
        <FeedForYouDate
          scope={scope}
          value={forYouUploadDate}
          onChange={setForYouUploadDate}
        />
      </Grid>
      <Grid
        item
        container
        spacing={1}
        direction="column"
        sx={{
          alignItems: 'stretch',
        }}
      >
        <Grid item>
          <BooleanField
            scope={scope}
            name="feed_foryou__unsafe"
            label={t('videosUserSettingsForm.feed.generic.unsafe')}
            value={forYouUnsafe}
            onChange={setForYouUnsafe}
          />
        </Grid>
        <Grid item>
          <BooleanField
            scope={scope}
            name="feed_foryou__exclude_compared_entities"
            label={t('videosUserSettingsForm.feed.generic.excludeCompared')}
            value={forYouExcludeCompared}
            onChange={setForYouExcludeCompared}
          />
        </Grid>
      </Grid>
    </>
  );
};

export default FeedForYou;
