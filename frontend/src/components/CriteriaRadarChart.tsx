import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts';
import { VideoSerializerWithCriteria } from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import useCriteriaChartData from 'src/hooks/useCriteriaChartData';

interface Props {
  video: VideoSerializerWithCriteria;
}

const CriteriaRadarChart = ({ video }: Props) => {
  const { getCriteriaLabel } = useCurrentPoll();
  const { shouldDisplayChart, data, domain } = useCriteriaChartData({ video });

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
        <title>{getCriteriaLabel(payload.value)}</title>
      </svg>
    );
  };

  if (!shouldDisplayChart) {
    return null;
  }

  return (
    <ResponsiveContainer width="100%" aspect={1}>
      <RadarChart outerRadius="80%" data={data}>
        <PolarGrid />
        <PolarAngleAxis dataKey="criteria" tick={renderCustomAxisTick} />
        {/* An invisible PolarRadiusAxis used to enforce the axis between 0 and 1 */}
        <PolarRadiusAxis domain={domain} axisLine={false} tick={false} />
        <Radar
          dataKey="clippedScore"
          stroke="#8884d8"
          fill="#8884d8"
          fillOpacity={0.6}
        />
        <Radar
          dataKey="clippedPersonalScore"
          stroke="#82ca9d"
          fill="#82ca9d"
          fillOpacity={0.6}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
};

export default CriteriaRadarChart;
