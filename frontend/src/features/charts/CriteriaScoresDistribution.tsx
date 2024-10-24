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
  Cell,
} from 'recharts';

import { Box } from '@mui/material';

import { Recommendation } from 'src/services/openapi';

import CriteriaSelector from 'src/features/criteria/CriteriaSelector';
import useCriterionScoreData, {
  ChartContext,
  ChartContextValue,
} from 'src/hooks/useCriterionScoreData';
import useCriteriaChartData from 'src/hooks/useCriteriaChartData';
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
  yMax = 'dataMax',
}: {
  criterion: string;
  criteriaDistributionScore: CriteriaDistributionScore;
  yMax?: string | number;
}) => {
  const { t } = useTranslation();
  const { bins, distribution } = criteriaDistributionScore;
  const barColors = new Array(20).fill(criterionColor(criterion));

  const { score: userScore, color } = useCriterionScoreData({
    index: criterion,
    personal: true,
  });

  /**
   * Use a different color for the bin in which the logged user's score is.
   */
  if (userScore) {
    // Transform scores like 78.75 in 70.
    const roundedScore = Math.floor(userScore / 10) * 10;

    // The step is 10 because the scores interval [-100, 100] is divided in 20
    // bins. If this granularity changes, the step and `roundedScore` must be
    // updated.
    for (let i = -100, j = 0; i <= 100; i += 10, j++) {
      if (i === roundedScore) {
        barColors[j] = color;
        break;
      }
    }
  }

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
          interval={0}
          height={50}
          tickMargin={8}
          tickFormatter={(value, index) => {
            const split = value.split(' ');
            if (index === 0 || index % 2) {
              return '';
            } else {
              return split.length > 2 ? split[0] : split[1];
            }
          }}
        />
        <YAxis
          domain={[0, yMax]}
          // Only display a tick for integer steps.
          tickCount={
            typeof yMax === 'number' && yMax <= 5 ? yMax + 1 : undefined
          }
          label={{
            value: t('criteriaScoresDistribution.numberOfRatings'),
            angle: -90,
            position: 'insideLeft',
            textAnchor: 'middle',
          }}
        />
        <Tooltip formatter={tooltipFormatter} />
        <Bar dataKey="value">
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={barColors[index]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

interface CriteriaScoresDistributionProps {
  reco: Recommendation;
}

const CriteriaScoresDistribution = ({
  reco,
}: CriteriaScoresDistributionProps) => {
  const { name: pollName } = useCurrentPoll();
  const { selectedCriterion, setSelectedCriterion } = useSelectedCriterion();
  const entity = reco.entity;

  const [yAxisMax, setYAxisMax] = useState(0);
  const [criteriaScoresDistribution, setCriteriaScoresDistribution] = useState<
    CriteriaDistributionScore[]
  >([]);

  const { data, personalScoresActivated, domain } = useCriteriaChartData({
    reco,
  });

  const contextValue = useMemo<ChartContextValue>(
    () => ({
      data,
      domain,
      chartWidth: 250,
      chartHeight: 400,
      personalScoresActivated,
    }),
    [data, domain, personalScoresActivated]
  );

  useEffect(() => {
    const getDistribution = async () => {
      const result =
        await PollsService.pollsEntitiesCriteriaScoresDistributionsRetrieve({
          name: pollName,
          uid: entity.uid,
        });
      setCriteriaScoresDistribution(result.criteria_scores_distributions);

      let yMax = 0;
      result.criteria_scores_distributions.forEach((criterion) => {
        const distribMax = Math.max(...criterion.distribution);
        if (distribMax > yMax) {
          yMax = distribMax;
        }
      });

      setYAxisMax(yMax);
    };
    getDistribution();
  }, [entity.uid, pollName]);

  const criteriaDistributionScore = useMemo(
    () =>
      criteriaScoresDistribution.find(
        ({ criteria: criterion }) => criterion === selectedCriterion
      ),
    [selectedCriterion, criteriaScoresDistribution]
  );

  return (
    <ChartContext.Provider value={contextValue}>
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
            yMax={yAxisMax}
          />
        </Box>
      )}
    </ChartContext.Provider>
  );
};

export default CriteriaScoresDistribution;
