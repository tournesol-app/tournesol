import React from 'react';
import {
  Bar,
  BarChart,
  XAxis,
  YAxis,
  Cell,
  Tooltip,
  TooltipProps,
} from 'recharts';
import { VideoSerializerWithCriteria } from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

const BAR_CHART_CRITERIA_SCORE_MIN = -1;
const BAR_CHART_CRITERIA_SCORE_MAX = 1;

interface Props {
  video: VideoSerializerWithCriteria;
}

const between = (a: number, b: number, x: number | undefined): number => {
  // clips x between a and b
  return Math.min(b, Math.max(a, x || 0));
};

const criteriaColors: { [criteria: string]: string } = {
  reliability: '#4F77DD',
  importance: '#DC8A5D',
  engaging: '#DFC642',
  pedagogy: '#C28BED',
  layman_friendly: '#4BB061',
  diversity_inclusion: '#76C6CB',
  backfire_risk: '#D37A80',
  better_habits: '#9DD654',
  entertaining_relaxing: '#D8B36D',
  default: '#000000',
};

const CriteriaBarChart = ({ video }: Props) => {
  const { getCriteriaLabel } = useCurrentPoll();

  const renderCustomAxisTick = ({
    x,
    y,
    payload,
  }: {
    x: number;
    y: number;
    payload: { value: string };
  }) => {
    return (
      <svg
        x={x - 30 + 250}
        y={y - 30}
        width="60"
        height="60"
        viewBox="0 0 60 60"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect x="0" y="15" width="60" height="30" fill="white" />
        <image
          x="9"
          y="9"
          width="42"
          height="42"
          href={`/svg/${payload.value}.svg`}
        />
        <title>{getCriteriaLabel(payload.value)}</title>
      </svg>
    );
  };

  const { criteria_scores } = video;
  const shouldDisplayChart = criteria_scores && criteria_scores.length > 0;

  if (!shouldDisplayChart) {
    return <div></div>;
  }

  const data = criteria_scores
    .filter((s) => s.criteria != 'largely_recommended')
    .map((s) => {
      const clipped_score = between(
        BAR_CHART_CRITERIA_SCORE_MIN,
        BAR_CHART_CRITERIA_SCORE_MAX,
        s.score
      );
      return {
        ...s,
        clipped_score,
      };
    });

  return (
    <BarChart width={500} height={500} layout="vertical" data={data}>
      <XAxis
        type="number"
        domain={[BAR_CHART_CRITERIA_SCORE_MIN, BAR_CHART_CRITERIA_SCORE_MAX]}
        hide={true}
      />

      <Bar dataKey="clipped_score" barSize={20}>
        {data.map((entry) => (
          <Cell
            key={entry.criteria}
            fill={criteriaColors[entry.criteria] || criteriaColors['default']}
          />
        ))}
      </Bar>
      <YAxis
        type="category"
        dataKey="criteria"
        tick={renderCustomAxisTick}
        interval={0}
        axisLine={false}
        tickLine={false}
        width={6}
      />
      <Tooltip
        cursor={{ stroke: 'black', strokeWidth: 2, fill: 'transparent' }}
        content={(props: TooltipProps<number, string>) => {
          const payload = props?.payload;
          if (payload && payload[0]) {
            const { criteria, score } = payload[0].payload;
            return (
              <pre>
                {getCriteriaLabel(criteria)}: {(10 * score).toFixed(2)}
              </pre>
            );
          }
          return null;
        }}
      />
    </BarChart>
  );
};

export default CriteriaBarChart;
