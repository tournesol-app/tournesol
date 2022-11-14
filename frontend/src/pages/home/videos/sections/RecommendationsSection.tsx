import React, { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { Box, Button, Divider, Grid, Paper, Typography } from '@mui/material';

import { Metrics } from 'src/features/statistics/UsageStatsSection';
import RecommendationsSubset from 'src/features/recommendation/subset/RecommendationsSubset';
import { useCurrentPoll } from 'src/hooks';

interface ComparedEntityStats {
  comparedEntityCount: number;
  lastMonthComparedEntityCount: number;
}

interface RecommendationsSectionProps {
  comparedEntityStats?: ComparedEntityStats;
}

/**
 * A home page section that displays a subset of recommended entities.
 */
const RecommendationsSection = ({
  comparedEntityStats,
}: RecommendationsSectionProps) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

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

  return (
    <Box>
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        mb={6}
        width="100%"
      >
        <Divider
          component="div"
          role="presentation"
          sx={{
            width: { xs: '100%', lg: '75%' },
            '&::before, &::after': { borderColor: '#fff' },
          }}
        >
          <Typography
            variant="h1"
            component="h2"
            textAlign="center"
            pl={4}
            pr={4}
          >
            {t('recommendationsSection.recommendations')}
          </Typography>
        </Divider>
      </Box>

      <Grid container justifyContent="center" spacing={4}>
        <Grid item lg={3} xl={3}>
          <Box
            display="flex"
            flexDirection="column"
            justifyContent="space-between"
            gap={2}
          >
            <Paper elevation={0}>
              <Box p={2} bgcolor="#fff" borderRadius={1}>
                <Typography paragraph fontSize={17}>
                  {t('recommendationsSection.eachComparisonHelps')}
                </Typography>
                <Box pb={2}>
                  <Divider />
                </Box>
                <Box textAlign="center">
                  <Metrics
                    text={comparedEntitiesTitle}
                    count={comparedEntityStats?.comparedEntityCount || 0}
                    lastMonthCount={
                      comparedEntityStats?.lastMonthComparedEntityCount || 0
                    }
                    lastMonthAsText
                  />
                </Box>
              </Box>
            </Paper>
          </Box>
        </Grid>
        <Grid item lg={6} xl={6}>
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
    </Box>
  );
};

export default RecommendationsSection;
