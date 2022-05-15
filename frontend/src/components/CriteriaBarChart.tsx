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
} from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { displayScore, criteriaIcon } from 'src/utils/criteria';
import useCriteriaChartData, {
  CriteriaChartDatum,
} from 'src/hooks/useCriteriaChartData';
import { useTranslation } from 'react-i18next';

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

// Copied from https://stackoverflow.com/a/59387478
const lighten = (color: string, lighten: number) => {
  const c = color.replace('#', '');
  const rgb = [
    parseInt(c.substr(0, 2), 16),
    parseInt(c.substr(2, 2), 16),
    parseInt(c.substr(4, 2), 16),
  ];
  let returnstatement = '#';
  rgb.forEach((color) => {
    returnstatement += Math.round(
      (255 - color) * (1 - Math.pow(Math.E, -lighten)) + color
    ).toString(16);
  });
  return returnstatement;
};

const SizedBarChart = ({
  data,
  personalScoresActivated,
  domain,
  width,
  height,
}: {
  data: CriteriaChartDatum[];
  personalScoresActivated: boolean;
  domain: number[];
  width?: number;
  height?: number;
}) => {
  const { getCriteriaLabel } = useCurrentPoll();
  const { t } = useTranslation();

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
        <rect x="0" y="0" width="60" height="60" fill="white" />
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

  return (
    <BarChart layout="vertical" width={width} height={height} data={data}>
      <XAxis type="number" domain={domain} hide={true} />

      <Bar dataKey="clippedScore" barSize={20}>
        {data.map((entry) => (
          <Cell
            key={entry.criteria}
            fill={criteriaColors[entry.criteria] || criteriaColors['default']}
          />
        ))}
      </Bar>
      {personalScoresActivated && (
        <Bar dataKey="clippedPersonalScore" barSize={20}>
          {data.map((entry) => (
            <Cell
              key={entry.criteria}
              fill={lighten(
                criteriaColors[entry.criteria] || criteriaColors['default'],
                0.5
              )}
            />
          ))}
        </Bar>
      )}
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
            const { criteria, score, personalScore } = payload[0].payload;
            return (
              <pre>
                {getCriteriaLabel(criteria)}: {displayScore(score)}
                {personalScoresActivated &&
                  `\n${t('personalCriteriaScores.chartTooltip', {
                    score: displayScore(personalScore),
                  })}`}
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
  const { shouldDisplayChart, data, personalScoresActivated, domain } =
    useCriteriaChartData({ video, entity });

  if (!shouldDisplayChart) return null;

  const height = data.length * 60;

  // We use a separated component for the chart because we need the width to position the icons.
  // ResponsiveContainer adds the width and height props to its child component.
  return (
    <ResponsiveContainer width="100%" height={height}>
      <SizedBarChart
        data={data}
        personalScoresActivated={personalScoresActivated}
        domain={domain}
      />
    </ResponsiveContainer>
  );
};

export default CriteriaBarChart;
