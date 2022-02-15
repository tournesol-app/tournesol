import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from 'recharts';
import { VideoSerializerWithCriteria } from 'src/services/openapi';
import { getCriteriaName } from 'src/utils/constants';
import { useTranslation } from 'react-i18next';

const RADAR_CHART_CRITERIA_SCORE_MIN = -1;
const RADAR_CHART_CRITERIA_SCORE_MAX = 1;

interface Props {
  video: VideoSerializerWithCriteria;
}

const between = (a: number, b: number, x: number | undefined): number => {
  // clips x between a and b
  return Math.min(b, Math.max(a, x || 0));
};

const CriteriaRadarChart = ({ video }: Props) => {
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
    return (
      <svg
        x={x - 16}
        y={y - 16}
        width="32"
        height="32"
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <image
          x="0"
          y="0"
          width="32"
          height="28"
          href={`/svg/${payload.value}.svg`}
        />
        <title>{getCriteriaName(t, payload.value)}</title>
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
        RADAR_CHART_CRITERIA_SCORE_MIN,
        RADAR_CHART_CRITERIA_SCORE_MAX,
        s.score
      ),
    }));

  return (
    <RadarChart width={300} height={300} outerRadius="80%" data={data}>
      <PolarGrid />
      <PolarAngleAxis dataKey="criteria" tick={renderCustomAxisTick} />
      {/* An invisible PolarRadiusAxis used to enforce the axis between 0 and 1 */}
      <PolarRadiusAxis
        domain={[
          RADAR_CHART_CRITERIA_SCORE_MIN,
          RADAR_CHART_CRITERIA_SCORE_MAX,
        ]}
        axisLine={false}
        tick={false}
      />
      <Radar
        dataKey="score"
        stroke="#8884d8"
        fill="#8884d8"
        fillOpacity={0.6}
      />
    </RadarChart>
  );
};

export default CriteriaRadarChart;
