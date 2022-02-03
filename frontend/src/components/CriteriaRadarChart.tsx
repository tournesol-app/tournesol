import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis } from 'recharts';
import { VideoSerializerWithCriteria } from 'src/services/openapi';
import { getCriteriaName } from 'src/utils/constants';
import { useTranslation } from 'react-i18next';

interface Props {
  video: VideoSerializerWithCriteria;
}

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
  const data = shouldDisplayChart
    ? criteria_scores.filter((s) => s.criteria != 'largely_recommended')
    : undefined;

  return (
    <div>
      {shouldDisplayChart && (
        <RadarChart width={300} height={300} outerRadius="80%" data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey="criteria" tick={renderCustomAxisTick} />
          <Radar
            dataKey="score"
            stroke="#8884d8"
            fill="#8884d8"
            fillOpacity={0.6}
          />
        </RadarChart>
      )}
    </div>
  );
};

export default CriteriaRadarChart;
