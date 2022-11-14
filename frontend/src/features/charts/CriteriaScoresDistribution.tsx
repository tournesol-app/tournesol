import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useTranslation, TFunction } from 'react-i18next';
import {
  Bar,
  BarChart,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';

import { Box } from '@mui/material';

import CriteriaSelector from 'src/features/criteria/CriteriaSelector';
import { useCurrentPoll } from 'src/hooks';
import { PollsService, CriteriaDistributionScore } from 'src/services/openapi';
import useSelectedCriterion from 'src/hooks/useSelectedCriterion';
import { criterionColor } from 'src/utils/criteria';

const binLabel = (index: number, bins: number[], t: TFunction) => {
  if (index === 0)
    return t('criteriaScoresDistribution.lessThan', {
      score: bins[1].toFixed(0),
    });
  if (index > 0 && index < bins.length - 2)
    return t('criteriaScoresDistribution.fromTo', {
      from: bins[index].toFixed(0),
      to: bins[index + 1].toFixed(0),
    });
  if (index === bins.length - 2)
    return t('criteriaScoresDistribution.greaterThan', {
      score: bins[bins.length - 2].toFixed(0),
    });
};

const CriteriaScoresDistributionChart = ({
  criterion,
  criteriaDistributionScore,
}: {
  criterion: string;
  criteriaDistributionScore: CriteriaDistributionScore;
}) => {
  const { t } = useTranslation();
  const { bins, distribution } = criteriaDistributionScore;

  const data = useMemo(
    () =>
      distribution.map((value, index) => ({
        value,
        label: binLabel(index, bins, t),
      })),
    [distribution, bins, t]
  );

  const tooltipFormatter: (value: number) => [number, string] = useCallback(
    (value: number) => [value, t('criteriaScoresDistribution.label')],
    [t]
  );

  const barColor = criterionColor(criterion);

  return (
    <ResponsiveContainer width="100%" height={360}>
      <BarChart width={430} height={360} data={data}>
        <CartesianGrid strokeDasharray="4 4" />
        <XAxis
          label={{
            value: t('criteriaScoresDistribution.scores'),
            position: 'insideBottom',
            offset: -4,
            textAnchor: 'middle',
          }}
          dataKey="label"
        />
        <YAxis
          label={{
            value: t('criteriaScoresDistribution.numberOfRatings'),
            angle: -90,
            position: 'insideLeft',
            textAnchor: 'middle',
          }}
        />
        <Tooltip formatter={tooltipFormatter} />
        <Bar dataKey="value" fill={barColor} />
      </BarChart>
    </ResponsiveContainer>
  );
};

interface CriteriaScoresDistributionProps {
  uid: string;
}

const CriteriaScoresDistribution = ({
  uid,
}: CriteriaScoresDistributionProps) => {
  const { name: pollName } = useCurrentPoll();
  const { selectedCriterion, setSelectedCriterion } = useSelectedCriterion();

  const [criteriaScoresDistribution, setCriteriaScoresDistribution] = useState<
    CriteriaDistributionScore[]
  >([]);

  useEffect(() => {
    const getDistribution = async () => {
      const result =
        await PollsService.pollsEntitiesCriteriaScoresDistributionsRetrieve({
          name: pollName,
          uid,
        });
      setCriteriaScoresDistribution(result.criteria_scores_distributions);
    };
    getDistribution();
  }, [uid, pollName]);

  const criteriaDistributionScore = useMemo(
    () =>
      criteriaScoresDistribution.find(
        ({ criteria: criterion }) => criterion === selectedCriterion
      ),
    [selectedCriterion, criteriaScoresDistribution]
  );

  return (
    <>
      <Box px={2} pt={1} pb={1}>
        <CriteriaSelector
          criteria={selectedCriterion}
          setCriteria={setSelectedCriterion}
        />
      </Box>
      {criteriaDistributionScore && (
        <Box py={1}>
          <CriteriaScoresDistributionChart
            criterion={selectedCriterion}
            criteriaDistributionScore={criteriaDistributionScore}
          />
        </Box>
      )}
    </>
  );
};

export default CriteriaScoresDistribution;
