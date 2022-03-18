import React from 'react';
import { Bar, BarChart, XAxis, YAxis, Cell } from 'recharts';
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
        x={x - 42}
        y={y - 21}
        width="42"
        height="42"
        viewBox="0 0 42 42"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <image
          x="0"
          y="0"
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
    .map((s) => ({
      ...s,
      score: between(
        BAR_CHART_CRITERIA_SCORE_MIN,
        BAR_CHART_CRITERIA_SCORE_MAX,
        s.score
      ),
    }));

  return (
    <BarChart width={500} height={500} layout="vertical" data={data}>
      <XAxis
        type="number"
        domain={[BAR_CHART_CRITERIA_SCORE_MIN, BAR_CHART_CRITERIA_SCORE_MAX]}
        hide={true}
      />
      <YAxis
        type="category"
        dataKey="criteria"
        tick={renderCustomAxisTick}
        interval={0}
        axisLine={false}
        tickLine={false}
      />
      <Bar dataKey="score" barSize={16}>
        {data.map((entry) => (
          <Cell
            key={entry.criteria}
            fill={criteriaColors[entry.criteria] || criteriaColors['default']}
          />
        ))}
      </Bar>
    </BarChart>
  );
};

export default CriteriaBarChart;
