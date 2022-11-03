import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Button, Grid, Stack, useTheme } from '@mui/material';
import { RadioButtonUnchecked, CheckCircleOutline } from '@mui/icons-material';

import EntityCard from 'src/components/entity/EntityCard';
import { useCurrentPoll } from 'src/hooks';
import { Recommendation } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';

interface RecommendationsSubsetProps {
  nbr?: number;
  displayControls?: boolean;
  controlsColor?: string;
}

const RecommendationsSubset = ({
  nbr = 4,
  displayControls = false,
  controlsColor = '#fff',
}: RecommendationsSubsetProps) => {
  const theme = useTheme();

  const { t } = useTranslation();
  const { criterias, name: pollName } = useCurrentPoll();

  const [recoDate, setRecoDate] = useState('');
  const [entities, setEntities] = useState<Array<Recommendation>>([]);

  useEffect(() => {
    const searchParams = new URLSearchParams();
    searchParams.append('date', recoDate);

    const getRecommendationsAsync = async () => {
      const recommendations = await getRecommendations(
        pollName,
        nbr,
        searchParams.toString(),
        criterias
      );
      setEntities(recommendations.results ?? []);
    };

    getRecommendationsAsync();
  }, [criterias, nbr, pollName, recoDate]);

  const onDateControlClick = (event: React.MouseEvent<HTMLElement>) => {
    setRecoDate(event.currentTarget.getAttribute('data-reco-date') ?? '');
  };

  return (
    <Box>
      {displayControls && (
        <Box mb={2}>
          <Stack direction="row" justifyContent="center" spacing={2}>
            <Button
              variant="outlined"
              endIcon={
                recoDate === '' ? (
                  <CheckCircleOutline />
                ) : (
                  <RadioButtonUnchecked />
                )
              }
              disableElevation
              sx={{
                color:
                  recoDate === '' ? theme.palette.primary.main : controlsColor,
                borderColor:
                  recoDate === '' ? theme.palette.primary.main : controlsColor,
                '&:hover': { color: theme.palette.primary.main },
              }}
              data-reco-date=""
              onClick={onDateControlClick}
            >
              {t('recommendationsSubset.bestOfLastMonth')}
            </Button>
            <Button
              variant="outlined"
              endIcon={
                recoDate === 'Month' ? (
                  <CheckCircleOutline />
                ) : (
                  <RadioButtonUnchecked />
                )
              }
              disableElevation
              sx={{
                color:
                  recoDate === 'Month'
                    ? theme.palette.primary.main
                    : controlsColor,
                borderColor:
                  recoDate === 'Month'
                    ? theme.palette.primary.main
                    : controlsColor,
                '&:hover': { color: theme.palette.primary.main },
              }}
              data-reco-date="Month"
              onClick={onDateControlClick}
            >
              {t('recommendationsSubset.bestOfAllTime')}
            </Button>
          </Stack>
        </Box>
      )}
      <Grid container gap={2} flexDirection="column">
        {entities.map((entity) => (
          <Grid item key={entity.uid}>
            <EntityCard
              entity={entity}
              compact={false}
              entityTypeConfig={{ video: { displayPlayer: false } }}
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default RecommendationsSubset;
