import React, { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { Box, Button, Divider, Grid, Paper, Typography } from '@mui/material';

import { Metrics } from 'src/features/statistics/UsageStatsSection';
import RecommendationsSubset from 'src/features/recommendation/subset/RecommendationsSubset';
import { useCurrentPoll } from 'src/hooks';
import SectionTitle from '../SectionTitle';
import UseOurExtension from './UseOurExtension';
import { useStatsRefresh } from 'src/hooks/useStatsRefresh';

/**
 * A home page section that displays a subset of recommended entities.
 */
const RecommendationsSection = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();
  const { statsState } = useStatsRefresh();

  const titleColor = '#fff';

  // Determine the date filter applied when the user click on the see more
  // button.
  const [seeMoreDate, setSeeMoreDate] = useState('Month');
  const onRecoDateChangeCallback = (selectedDate: string) => {
    setSeeMoreDate(selectedDate);
  };

  const comparedEntitiesTitle = useMemo(() => {
    switch (pollName) {
      case 'videos':
        return t('stats.ratedVideos');
      case 'presidentielle2022':
        return t('stats.ratedCandidates');
      default:
        throw new Error(`Unknown poll: ${pollName}`);
    }
  }, [pollName, t]);

  console.log('Recommendations section statsState :', statsState);

  return (
    <Box>
      <SectionTitle
        title={t('recommendationsSection.recommendations')}
        color={titleColor}
        dividerColor={titleColor}
      />

      <Grid container justifyContent="center" spacing={4}>
        <Grid item lg={3} xl={3}>
          <Paper elevation={0}>
            <Box p={2} borderRadius={1}>
              <Typography paragraph fontSize={17}>
                {t('recommendationsSection.eachComparisonHelps')}
              </Typography>
              <Box pb={2}>
                <Divider />
              </Box>
              <Box textAlign="center">
                <Metrics
                  text={comparedEntitiesTitle}
                  count={statsState.comparedEntityCount}
                  lastMonthCount={statsState.lastMonthComparedEntityCount}
                  lastMonthAsText
                />
              </Box>
            </Box>
          </Paper>
        </Grid>
        <Grid item lg={9} xl={6}>
          <Box
            display="flex"
            justifyContent="center"
            flexDirection="column"
            gap={2}
          >
            <RecommendationsSubset
              displayControls
              onRecoDateChange={onRecoDateChangeCallback}
            />
            <Box display="flex" justifyContent="center">
              <Button
                variant="contained"
                component={Link}
                to={`/recommendations?date=${seeMoreDate}`}
              >
                {t('recommendationsSection.seeMore')}
              </Button>
            </Box>
          </Box>
        </Grid>
      </Grid>
      <UseOurExtension titleColor={titleColor} />
    </Box>
  );
};

export default RecommendationsSection;
