import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box } from '@mui/material';

import { ContentHeader } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import Comparison from 'src/features/comparisons/Comparison';
import ComparisonSeries from 'src/features/comparisonSeries/ComparisonSeries';
import {
  Comparison as ComparisonModel,
  UsersService,
} from 'src/services/openapi';

export function getUserComparisons(
  pollName: string
): Promise<ComparisonModel[]> {
  const comparisons: Promise<ComparisonModel[]> =
    UsersService.usersMeComparisonsList({
      pollName,
    }).then((data) => data.results ?? []);
  return comparisons;
}

const ComparisonPage = () => {
  const { t } = useTranslation();

  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const series: string = searchParams.get('series') || 'false';

  const { options, name: pollName } = useCurrentPoll();
  const tutorialLength = options?.tutorialLength ?? 0;
  const tutorialAlternatives = options?.tutorialAlternatives ?? undefined;
  const tutorialDialogs = options?.tutorialDialogs ?? undefined;
  const [alreadyMadeComparisons, setAlreadyMadeComparisons] = useState<
    Array<string>
  >([]);

  let dialogs;
  if (tutorialDialogs) {
    dialogs = tutorialDialogs(t);
  }

  /**
   * If 'series' is present in the URL parameters, retrieve the user's
   * comparisons to avoid suggesting couple of entities that have been already
   * compared.
   */
  useEffect(() => {
    async function getUserComparisonsAsync(pName: string) {
      const comparisons = await getUserComparisons(pName);
      setAlreadyMadeComparisons(
        comparisons.map((c) => c.entity_a.uid + '/' + c.entity_b.uid)
      );
    }

    if (series === 'true') {
      getUserComparisonsAsync(pollName);
    }
  }, [pollName, series]);

  return (
    <>
      <ContentHeader title={t('comparison.submitAComparison')} />
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          flexDirection: 'column',
          py: 2,
        }}
      >
        {series === 'true' ? (
          <ComparisonSeries
            alreadyMadeComparisons={alreadyMadeComparisons}
            dialogs={dialogs}
            generateInitial={true}
            getAlternatives={tutorialAlternatives}
            length={tutorialLength}
          />
        ) : (
          <Comparison />
        )}
      </Box>
    </>
  );
};

export default ComparisonPage;
