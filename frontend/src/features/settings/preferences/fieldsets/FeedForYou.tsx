import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, Grid, Typography } from '@mui/material';

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
        <Typography id={`${pollName}-feed-foryou`} variant="h5">
          {t('pollUserSettingsForm.feedForYou')}
        </Typography>
      </Grid>
      <Grid item>
        <Alert severity="info">
          <Trans
            t={t}
            i18nKey="pollUserSettingsForm.customizeYourDefaultSearchFilter"
          >
            Customize <strong>the default search filters</strong> according to
            your own preferences. Those filters are applied{' '}
            <strong>only</strong> when you access the recommendations from the{' '}
            <strong>main menu</strong>.
          </Trans>
        </Alert>
      </Grid>
      <Grid item>
        <FeedForYouDate
          value={forYouUploadDate}
          onChange={setForYouUploadDate}
          pollName={pollName}
        />
      </Grid>
      <Grid item container spacing={1} direction="column" alignItems="stretch">
        <Grid item>
          <BooleanField
            scope={pollName}
            name="feed_foryou__unsafe"
            label={t('videosUserSettingsForm.feed.unsafe')}
            value={forYouUnsafe}
            onChange={setForYouUnsafe}
          />
        </Grid>
        <Grid item>
          <BooleanField
            scope={pollName}
            name="feed_foryou__exclude_compared_entities"
            label={t('videosUserSettingsForm.feed.excludeCompared')}
            value={forYouExcludeCompared}
            onChange={setForYouExcludeCompared}
          />
        </Grid>
      </Grid>
    </>
  );
};

export default FeedForYou;
