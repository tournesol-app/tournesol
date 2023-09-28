import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Paper, Typography, useTheme } from '@mui/material';

import { LoaderWrapper } from 'src/components';
import EntityCard from 'src/components/entity/EntityCard';
import { useCurrentPoll } from 'src/hooks';
import { Recommendation } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';
import RecommendationsSubsetControls from './RecommendationsSubsetControls';

interface RecommendationsSubsetProps {
  // the maximum number of entity to display
  nbr?: number;
  // if true display few buttons allowing to filter the recommendations
  displayControls?: boolean;
  // the color of the control buttons
  controlsColor?: string;
  // called when the recommendation date is changed by the controls
  onRecoDateChange?: (selectedDate: string) => void;
}

const RecommendationsSubset = ({
  nbr = 4,
  displayControls = false,
  controlsColor = '#fff',
  onRecoDateChange,
}: RecommendationsSubsetProps) => {
  const theme = useTheme();

  const { i18n, t } = useTranslation();
  const { criterias, name: pollName } = useCurrentPoll();

  const [isLoading, setIsLoading] = useState(true);

  const [recoDate, setRecoDate] = useState('Month');
  const [entities, setEntities] = useState<Array<Recommendation>>([]);
  const currentLang = i18n.resolvedLanguage || i18n.language;

  useEffect(() => {
    const searchParams = new URLSearchParams();
    searchParams.append('date', recoDate);
    searchParams.append('language', currentLang);

    const getRecommendationsAsync = async () => {
      setIsLoading(true);

      const recommendations = await getRecommendations(
        pollName,
        nbr,
        searchParams.toString(),
        criterias
      );

      setIsLoading(false);
      setEntities(recommendations.results ?? []);
    };

    getRecommendationsAsync();
  }, [criterias, currentLang, nbr, pollName, recoDate]);

  const dateControlChangeCallback = (value: string) => {
    setRecoDate(value);

    if (onRecoDateChange) {
      onRecoDateChange(value);
    }
  };

  return (
    <Box>
      {displayControls && (
        <Box mb={2}>
          <RecommendationsSubsetControls
            controlsColor={controlsColor}
            selectedDate={recoDate}
            dateControlChangeCallback={dateControlChangeCallback}
          />
        </Box>
      )}
      <LoaderWrapper isLoading={isLoading}>
        {entities.length === 0 ? (
          <Typography paragraph textAlign="center" color="#fff">
            {t('recommendationsSubset.noRecommendationHasBeenFound')}
          </Typography>
        ) : (
          <Paper sx={{ p: 1, bgcolor: 'background.primary' }}>
            <Grid container gap={1} direction="column" wrap="nowrap">
              {entities.map((reco) => (
                <Grid
                  item
                  key={reco.entity.uid}
                  // Allow the RecommendationsSubset's parent to overwrite the
                  // text color without impacting the EntityCard.
                  sx={{ color: theme.palette.text.primary }}
                >
                  <EntityCard
                    result={reco}
                    compact={false}
                    entityTypeConfig={{ video: { displayPlayer: false } }}
                  />
                </Grid>
              ))}
            </Grid>
          </Paper>
        )}
      </LoaderWrapper>
    </Box>
  );
};

export default RecommendationsSubset;
