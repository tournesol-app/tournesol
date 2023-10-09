import React, {
  useRef,
  useLayoutEffect,
  useState,
  useMemo,
  useCallback,
} from 'react';
import { Recommendation } from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { criteriaIcon, criterionColor } from 'src/utils/criteria';
import useCriteriaChartData, {
  CriterionChartScores,
} from 'src/hooks/useCriteriaChartData';
import { useTranslation } from 'react-i18next';
import { Tooltip } from '@mui/material';
import useResizeObserver from '@react-hook/resize-observer';
import useSelectedCriterion from 'src/hooks/useSelectedCriterion';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import useCriterionScoreData, {
  useChartContext,
  ChartContext,
  ChartContextValue,
} from 'src/hooks/useCriterionScoreData';
const barMargin = 40; // The horizontal margin around the bar (must be enough for the icon and the score value)
const criterionChartHeight = 40; // The height of a single criterion chart (circle + icon + bars)
const scoreBarHeight = 10;
const scoreBarsSpacing = 4;
const scoreLabelSpacingWithBar = 4;
const selectedCriterionBackgroundColor = 'rgb(238, 238, 238)';

const calculateScoreBarY = ({
  index,
  personalScoresActivated,
  personal,
}: {
  index: number;
  personalScoresActivated: boolean;
  personal: boolean;
}) => {
  let y =
    criterionChartHeight * index +
    criterionChartHeight / 2 -
    scoreBarHeight / 2;

  if (personalScoresActivated) {
    if (personal) y += scoreBarHeight / 2 + scoreBarsSpacing / 2;
    else y -= scoreBarHeight / 2 + scoreBarsSpacing / 2;
  }

  return y;
};

const calculateScoreBarWidth = ({
  chartWidth,
  clippedScore,
  domain,
}: {
  chartWidth: number;
  clippedScore: number;
  domain: number[];
}) => {
  const maxBarWidth = chartWidth - 2 * barMargin;
  const [min, max] = domain;
  const scoreWidth = ((clippedScore - min) / (max - min)) * maxBarWidth;
  return scoreWidth;
};

const ScoreBar = ({
  index,
  personal,
}: {
  index: number;
  personal: boolean;
}) => {
  const { chartWidth, domain, personalScoresActivated } = useChartContext();
  const { clippedScore, color } = useCriterionScoreData({
    index,
    personal,
  });

  if (personal && !personalScoresActivated) return null;
  if (clippedScore === undefined) return null;

  const y = calculateScoreBarY({ index, personalScoresActivated, personal });
  const scoreWidth = calculateScoreBarWidth({
    chartWidth,
    clippedScore,
    domain,
  });

  // We make the bar start inside the margin instead of the minimum value to make it look like it comes from below the circle
  const barOffsetInsideMargin = barMargin * 0.5;

  return (
    <rect
      x={barMargin - barOffsetInsideMargin}
      y={y}
      width={scoreWidth + barOffsetInsideMargin}
      height={scoreBarHeight}
      fill={color}
    />
  );
};

const ScoreLabel = ({
  index,
  personal,
}: {
  index: number;
  personal: boolean;
}) => {
  const { chartWidth, domain, personalScoresActivated } = useChartContext();
  const { score, clippedScore, color } = useCriterionScoreData({
    index,
    personal,
  });

  if (personal && !personalScoresActivated) return null;
  if (score === undefined) return null;

  const y = calculateScoreBarY({ index, personalScoresActivated, personal });
  const scoreWidth = calculateScoreBarWidth({
    chartWidth,
    clippedScore: clippedScore || 0,
    domain,
  });

  return (
    <text
      x={barMargin + scoreWidth + scoreLabelSpacingWithBar}
      y={y + scoreBarHeight / 2}
      dominantBaseline="middle"
      fill={color}
      style={{ fontSize: 14, fontWeight: 'bold' }}
    >
      {score.toFixed(0)}
    </text>
  );
};

const SVGTooltip = ({
  x,
  y,
  width,
  height,
  debug = false,
  ...tooltipProps
}: {
  title: string;
  x: number;
  y: number;
  width: number;
  height: number;
  debug?: boolean;
  [tooltipProps: string]: unknown;
}) => (
  <foreignObject x={x} y={y} width={width} height={height}>
    <Tooltip {...tooltipProps}>
      <div
        style={{
          width,
          height,
          background: debug ? 'rgba(255, 0, 0, 0.3)' : undefined,
        }}
      />
    </Tooltip>
  </foreignObject>
);

const ScoreTooltip = ({
  index,
  personal,
}: {
  index: number;
  personal: boolean;
}) => {
  const { chartWidth, domain, personalScoresActivated } = useChartContext();
  const { clippedScore } = useCriterionScoreData({
    index,
    personal,
  });
  const { t } = useTranslation();

  const theme = useTheme();
  const smallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const { placement, popperProps } = useMemo(() => {
    if (smallScreen)
      return {
        placement: 'top',
        popperProps: {
          modifiers: [
            {
              name: 'offset',
              options: {
                offset: [0, -10],
              },
            },
          ],
        },
      };
    else return { placement: 'right' };
  }, [smallScreen]);

  if (personal && !personalScoresActivated) return null;

  const tooltip = personal
    ? t('criteriaBarChart.personalScoreTooltip')
    : t('criteriaBarChart.scoreTooltip');

  const y = calculateScoreBarY({ index, personalScoresActivated, personal });
  const scoreWidth = calculateScoreBarWidth({
    chartWidth,
    clippedScore: clippedScore || 0,
    domain,
  });

  const extraVerticalSize = 2;
  const maxLabelWidth = 30;

  const width = scoreWidth + scoreLabelSpacingWithBar + maxLabelWidth;
  const height = scoreBarHeight + extraVerticalSize / 2;

  return (
    <SVGTooltip
      x={barMargin - 2}
      y={y - extraVerticalSize / 2}
      width={width + 2}
      height={height + extraVerticalSize}
      title={tooltip}
      placement={placement}
      PopperProps={popperProps}
      arrow
    />
  );
};

const SVGCriterionIcon = ({
  criterion,
  centerX,
  centerY,
}: {
  criterion: string;
  centerX: number;
  centerY: number;
}) => {
  // We don't use the CriteriaIcon component here (inside a foreignObject) because it makes the image or emoji not centered

  const { getCriteriaLabel } = useCurrentPoll();
  const { emoji, imagePath } = criteriaIcon(criterion);

  return (
    <>
      {emoji ? (
        <text
          x={centerX}
          y={centerY + 2}
          width="18"
          height="20"
          dominantBaseline="middle"
          textAnchor="middle"
        >
          {emoji}
        </text>
      ) : (
        <foreignObject x={centerX - 9} y={centerY - 10} width="18" height="20">
          <img src={imagePath} width="18" />
        </foreignObject>
      )}
      <SVGTooltip
        x={centerX - 18}
        y={centerY - 18}
        width={36}
        height={36}
        title={getCriteriaLabel(criterion)}
        placement="right"
        arrow
      />
    </>
  );
};

const CriterionLabel = ({ index }: { index: number }) => {
  const { data } = useChartContext();
  const criterionScores = data[index];
  const { criterion } = criterionScores;
  const color = criterionColor(criterion);
  const { selectedCriterion } = useSelectedCriterion();

  return (
    <>
      <circle
        cx="20"
        cy={criterionChartHeight * index + 20}
        r={16}
        stroke={color}
        strokeWidth="4"
        fill={
          criterion === selectedCriterion
            ? selectedCriterionBackgroundColor
            : 'white'
        }
      />
      <SVGCriterionIcon
        criterion={criterion}
        centerX={20}
        centerY={criterionChartHeight * index + criterionChartHeight / 2}
      />
    </>
  );
};

const AxisLine = () => {
  const { chartWidth, chartHeight, domain } = useChartContext();
  const x =
    barMargin +
    calculateScoreBarWidth({ chartWidth, clippedScore: 0.0, domain });
  return (
    <line
      x1={x}
      x2={x}
      y1={0}
      y2={chartHeight}
      stroke="black"
      strokeDasharray="5,5"
    />
  );
};

const SelectedCriterionIndicator = ({ index }: { index: number }) => {
  return (
    <rect
      x={0}
      y={criterionChartHeight * index}
      width="100%"
      height={criterionChartHeight}
      fill={selectedCriterionBackgroundColor}
      rx="4"
    />
  );
};

const SizedBarChart = ({
  data,
  personalScoresActivated,
  domain,
  width,
}: {
  data: CriterionChartScores[];
  personalScoresActivated: boolean;
  domain: number[];
  width: number;
}) => {
  const { selectedCriterion, setSelectedCriterion } = useSelectedCriterion();

  const height = criterionChartHeight * data.length;

  const contextValue = useMemo<ChartContextValue>(
    () => ({
      data,
      domain,
      chartWidth: width,
      chartHeight: height,
      personalScoresActivated,
    }),
    [data, domain, width, height, personalScoresActivated]
  );

  const svgRef = useRef<SVGSVGElement>(null);

  const handleClick = useCallback(
    (event) => {
      event.preventDefault();

      const clickY = event.clientY;
      const containerY = svgRef.current?.getBoundingClientRect().top;
      if (containerY === undefined) return;

      const y = clickY - containerY;
      const index = Math.floor(y / criterionChartHeight);

      if (index < 0 || index >= data.length) return;
      const { criterion } = data[index];

      setSelectedCriterion(criterion);
    },
    [data, setSelectedCriterion]
  );

  return (
    <ChartContext.Provider value={contextValue}>
      <svg
        width={width}
        height={height}
        ref={svgRef}
        onClick={handleClick}
        style={{ cursor: 'pointer', WebkitTapHighlightColor: 'transparent' }}
      >
        {data.map(({ criterion }, index) => (
          <React.Fragment key={criterion}>
            {criterion === selectedCriterion && (
              <SelectedCriterionIndicator index={index} />
            )}
            <ScoreBar index={index} personal={false} />
            <ScoreBar index={index} personal={true} />
            <CriterionLabel index={index} />
          </React.Fragment>
        ))}
        <AxisLine />
        {data.map(({ criterion }, index) => (
          <React.Fragment key={criterion}>
            <ScoreLabel index={index} personal={false} />
            <ScoreLabel index={index} personal={true} />
            <ScoreTooltip index={index} personal={false} />
            <ScoreTooltip index={index} personal={true} />
          </React.Fragment>
        ))}
      </svg>
    </ChartContext.Provider>
  );
};

interface Props {
  reco: Recommendation;
}

const CriteriaBarChart = ({ reco }: Props) => {
  const { shouldDisplayChart, data, personalScoresActivated, domain } =
    useCriteriaChartData({ reco });

  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState<number | undefined>(undefined);

  useLayoutEffect(() => {
    const rect = containerRef.current?.getBoundingClientRect();
    const width = rect?.width;
    setWidth(width);
  }, []);

  useResizeObserver(containerRef, (entry) => setWidth(entry.contentRect.width));

  if (!shouldDisplayChart) return null;

  return (
    <div ref={containerRef}>
      {width !== undefined && (
        <SizedBarChart
          data={data}
          domain={domain}
          personalScoresActivated={personalScoresActivated}
          width={width}
        />
      )}
    </div>
  );
};

export default CriteriaBarChart;
