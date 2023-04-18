import { createContext, useContext } from 'react';
import { lighten } from 'src/utils/color';
import { CriterionChartScores } from 'src/hooks/useCriteriaChartData';
import { criterionColor } from 'src/utils/criteria';

export interface ChartContextValue {
  data: CriterionChartScores[];
  domain: number[];
  chartWidth: number;
  chartHeight: number;
  personalScoresActivated: boolean;
}

export const ChartContext = createContext<ChartContextValue>({
  data: [],
  domain: [0.0, 1.0],
  chartWidth: 0,
  chartHeight: 0,
  personalScoresActivated: false,
});
export const useChartContext = () => useContext(ChartContext);

const useCriterionScoreData = ({
  index,
  personal,
}: {
  index: number | string;
  personal: boolean;
}) => {
  const { data } = useChartContext();

  const criterionScores =
    typeof index == 'number'
      ? data[index]
      : data[data.findIndex(({ criterion }) => criterion == index)];

  const {
    criterion,
    score,
    clippedScore,
    personalScore,
    clippedPersonalScore,
  } = criterionScores;
  const color = criterionColor(criterion);

  if (personal)
    return {
      score: personalScore,
      clippedScore: clippedPersonalScore,
      color: lighten(color, 0.5),
    };
  else
    return {
      score,
      clippedScore,
      color,
    };
};

export default useCriterionScoreData;
