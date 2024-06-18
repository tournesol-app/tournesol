import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Grid } from '@mui/material';

import SettingsHeading from 'src/features/settings/preferences/SettingsHeading';
import { BlankEnum, FeedForyou_dateEnum } from 'src/services/openapi';

import FeedForYouDate from '../fields/FeedForYouDate';
import BooleanField from '../fields/generics/BooleanField';

interface FeedForYouProps {
  pollName: string;
  forYouUnsafe: boolean;
  setForYouUnsafe: (target: boolean) => void;
  forYouExcludeCompared: boolean;
  setForYouExcludeCompared: (target: boolean) => void;
  forYouUploadDate: FeedForyou_dateEnum | BlankEnum;
  setForYouUploadDate: (target: FeedForyou_dateEnum | BlankEnum) => void;
}

const FeedForYou = ({
  pollName,
  forYouUnsafe,
  setForYouUnsafe,
  forYouExcludeCompared,
  setForYouExcludeCompared,
  forYouUploadDate,
  setForYouUploadDate,
}: FeedForYouProps) => {
  const { t } = useTranslation();
  return (
    <>
      <Grid item>
        <SettingsHeading
          id={`${pollName}-feed-foryou`}
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
        <FeedForYouDate
          pollName={pollName}
          value={forYouUploadDate}
          onChange={setForYouUploadDate}
        />
      </Grid>
      <Grid item container spacing={1} direction="column" alignItems="stretch">
        <Grid item>
          <BooleanField
            scope={pollName}
            name="feed_foryou__unsafe"
            label={t('videosUserSettingsForm.feed.generic.unsafe')}
            value={forYouUnsafe}
            onChange={setForYouUnsafe}
          />
        </Grid>
        <Grid item>
          <BooleanField
            scope={pollName}
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
