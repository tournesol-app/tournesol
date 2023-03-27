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

import {
  VideoSerializerWithCriteria,
  Recommendation,
} from 'src/services/openapi';

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
}: {
  criterion: string;
  criteriaDistributionScore: CriteriaDistributionScore;
}) => {
  const { t } = useTranslation();
  const { bins, distribution } = criteriaDistributionScore;
  const barColors = new Array(20).fill(criterionColor(criterion));

  const { score: userScore, color } = useCriterionScoreData({
    index: criterion,
    personal: true,
  });

  if (userScore) {
    // transform a score like 78.75 to 70
    const roundedScore = Math.floor(userScore / 10) * 10;

    // step are 10 since granularity is 20
    // Beware if granularity change
    for (let i = -100, j = 0; i <= 100; i += 10, j++) {
      if (i == roundedScore) {
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
  video: VideoSerializerWithCriteria;
  entity?: Recommendation;
}

const CriteriaScoresDistribution = ({
  video,
  entity,
}: CriteriaScoresDistributionProps) => {
  const { name: pollName } = useCurrentPoll();
  const { selectedCriterion, setSelectedCriterion } = useSelectedCriterion();

  const [criteriaScoresDistribution, setCriteriaScoresDistribution] = useState<
    CriteriaDistributionScore[]
  >([]);

  const { data, personalScoresActivated, domain } = useCriteriaChartData({
    video,
    entity,
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
          uid: video.uid,
        });
      setCriteriaScoresDistribution(result.criteria_scores_distributions);
    };
    getDistribution();
  }, [video.uid, pollName]);

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
          />
        </Box>
      )}
    </ChartContext.Provider>
  );
};

export default CriteriaScoresDistribution;
