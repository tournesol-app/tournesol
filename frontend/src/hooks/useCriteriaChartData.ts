import { useMemo, useCallback } from 'react';
import {
  VideoSerializerWithCriteria,
  Recommendation,
  EntityCriteriaScore,
} from 'src/services/openapi';
import usePersonalCriteriaScores from 'src/hooks/usePersonalCriteriaScores';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { PRESIDENTIELLE_2022_POLL_NAME } from 'src/utils/constants';

const between = (a: number, b: number, x: number | undefined): number => {
  // clips x between a and b
  return Math.min(b, Math.max(a, x || 0));
};

const SCORE_MIN = -1;
const SCORE_MAX = 1;
const DOMAIN = [SCORE_MIN, SCORE_MAX];

export interface CriterionChartScores {
  criterion: string;
  score: number | undefined;
  clippedScore: number | undefined;
  personalScore: number | undefined;
  clippedPersonalScore: number | undefined;
}

export interface UseCriteriaChartDataValue {
  shouldDisplayChart: boolean; // Whether the chart should be displayed
  data: CriterionChartScores[]; // The scores per criterion
  personalScoresActivated: boolean; // True if the data also contains personal scores
  domain: number[]; // Minimum and maximum score values that should be displayed (scores in data may be outside this domain)
}

interface ScoreByCriterion {
  [criterion: string]: {
    score: number | undefined;
    clippedScore: number | undefined;
  };
}

const useCriteriaChartData = ({
  video,
  entity,
}: {
  video?: VideoSerializerWithCriteria;
  entity?: Recommendation;
}): UseCriteriaChartDataValue => {
  const criteriaScores: Array<EntityCriteriaScore> = useMemo(
    () => video?.criteria_scores || entity?.criteria_scores || [],
    [video, entity]
  );
  const shouldDisplayChart = criteriaScores && criteriaScores.length > 0;

  const { name: pollName, criterias: pollCriteria } = useCurrentPoll();

  const { personalScoresActivated, personalCriteriaScores } =
    usePersonalCriteriaScores();

  const clipScore = useCallback(
    (score) =>
      between(
        SCORE_MIN,
        SCORE_MAX,
        // TODO: below is a bad hack necessary because scores on multiple
        // polls are not scaled in the same way. We should have a simpler
        // manner to address this.
        pollName === PRESIDENTIELLE_2022_POLL_NAME ? 4 * score : score
      ),
    [pollName]
  );

  const personalScoreByCriterion = useMemo(() => {
    if (!personalScoresActivated || personalCriteriaScores === undefined)
      return {};

    const result: ScoreByCriterion = {};
    personalCriteriaScores.forEach(({ criteria: criterion, score }) => {
      result[criterion] = {
        score,
        clippedScore: clipScore(score),
      };
    });
    return result;
  }, [personalScoresActivated, personalCriteriaScores, clipScore]);

  const scoreByCriterion = useMemo(() => {
    const result: ScoreByCriterion = {};
    criteriaScores.forEach(({ criteria: criterion, score }) => {
      result[criterion] = {
        score,
        clippedScore: clipScore(score),
      };
    });
    return result;
  }, [criteriaScores, clipScore]);

  const data = useMemo<CriterionChartScores[]>(() => {
    if (!shouldDisplayChart) return [];

    return pollCriteria.map((pollCriterion) => {
      const criterion = pollCriterion.name;
      const { score, clippedScore } = scoreByCriterion[criterion] || {};
      const { score: personalScore, clippedScore: clippedPersonalScore } =
        personalScoreByCriterion[criterion] || {};
      return {
        criterion,
        score,
        clippedScore,
        personalScore,
        clippedPersonalScore,
      };
    });
  }, [
    shouldDisplayChart,
    pollCriteria,
    scoreByCriterion,
    personalScoreByCriterion,
  ]);

  return {
    shouldDisplayChart,
    data,
    personalScoresActivated,
    domain: DOMAIN,
  };
};

export default useCriteriaChartData;
