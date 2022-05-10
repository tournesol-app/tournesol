import React from 'react';
import {
  Bar,
  BarChart,
  XAxis,
  YAxis,
  Cell,
  Tooltip,
  TooltipProps,
  ResponsiveContainer,
} from 'recharts';
import {
  VideoSerializerWithCriteria,
  Recommendation,
  EntityCriteriaScore,
} from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { displayScore, criteriaIcon } from 'src/utils/criteria';
import { PRESIDENTIELLE_2022_POLL_NAME } from 'src/utils/constants';

const BAR_CHART_CRITERIA_SCORE_MIN = -1;
const BAR_CHART_CRITERIA_SCORE_MAX = 1;

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
  default: '#506ad4',
};

const SizedBarChart = ({
  criteriaScores,
  width,
  height,
}: {
  criteriaScores: Array<EntityCriteriaScore>;
  width?: number;
  height?: number;
}) => {
  const { getCriteriaLabel, options, name: pollName } = useCurrentPoll();
  const mainCriterionName = options?.mainCriterionName ?? '';

  const renderCustomAxisTick = ({
    x,
    y,
    payload,
  }: {
    x: number;
    y: number;
    payload: { value: string };
  }) => {
    const criteriaName = payload.value;
    const { emoji, imagePath } = criteriaIcon(criteriaName);
    return (
      <svg
        x={x - 30 + (width || 0) / 2}
        y={y - 30}
        width="60"
        height="60"
        viewBox="0 0 60 60"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <style>{'.emoji { font-size: 42px; fill: black; }'}</style>
        <rect x="0" y="15" width="60" height="60" fill="white" />
        {emoji ? (
          <text x="9" y="9" dominantBaseline="hanging" className="emoji">
            {emoji}
          </text>
        ) : (
          <image x="9" y="9" width="42" height="42" href={imagePath} />
        )}
        <title>{getCriteriaLabel(criteriaName)}</title>
      </svg>
    );
  };

  const shouldDisplayChart = criteriaScores && criteriaScores.length > 0;

  if (!shouldDisplayChart) {
    return <div></div>;
  }

  const data = criteriaScores
    .filter((s) => mainCriterionName !== s.criteria)
    .map((s) => {
      // TODO: below is a bad hack necessary because scores on multiple
      // polls are not scaled in the same way. We should have a simpler
      // manner to address this.
      const _score = s.score || 0;
      const clipped_score = between(
        BAR_CHART_CRITERIA_SCORE_MIN,
        BAR_CHART_CRITERIA_SCORE_MAX,
        pollName === PRESIDENTIELLE_2022_POLL_NAME ? 4 * _score : _score
      );
      return {
        ...s,
        clipped_score,
      };
    });

  return (
    <BarChart layout="vertical" width={width} height={height} data={data}>
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
                {getCriteriaLabel(criteria)}: {displayScore(score)}
              </pre>
            );
          }
          return null;
        }}
      />
    </BarChart>
  );
};

interface Props {
  video?: VideoSerializerWithCriteria;
  entity?: Recommendation;
}

const CriteriaBarChart = ({ video, entity }: Props) => {
  const criteriaScores: Array<EntityCriteriaScore> =
    video?.criteria_scores || entity?.criteria_scores || [];

  const height = criteriaScores.length * 60;

  // ResponsiveContainer adds the width and height props to its child component.
  // We need the width to position the icons.
  return (
    <ResponsiveContainer width="100%" height={height}>
      <SizedBarChart criteriaScores={criteriaScores} />
    </ResponsiveContainer>
  );
};

export default CriteriaBarChart;
