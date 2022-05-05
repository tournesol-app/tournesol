import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { PollsService, CriteriaDistributionScore } from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks';
import {
  Bar,
  BarChart,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import CriteriaSelector from 'src/features/criteria/CriteriaSelector';
import { useTranslation, TFunction } from 'react-i18next';

const displayScore = (score: number) => (10 * score).toFixed(0);

const binLabel = (index: number, bins: number[], t: TFunction) => {
  if (index === 0)
    return t('criteriaScoreDistributions.lessThan', {
      score: displayScore(bins[1]),
    });
  if (index > 0 && index < bins.length - 2)
    return t('criteriaScoreDistributions.fromTo', {
      from: displayScore(bins[index]),
      to: displayScore(bins[index + 1]),
    });
  if (index === bins.length - 2)
    return t('criteriaScoreDistributions.greaterThan', {
      score: displayScore(bins[bins.length - 2]),
    });
};

const CriteriaDistributionScoreChart = ({
  criteriaDistributionScore,
}: {
  criteriaDistributionScore: CriteriaDistributionScore;
}) => {
  const { distribution, bins } = criteriaDistributionScore;
  const { t } = useTranslation();
  const data = useMemo(
    () =>
      distribution.map((value, index) => ({
        value,
        label: binLabel(index, bins, t),
      })),
    [distribution, bins, t]
  );

  const tooltipFormatter = useCallback(
    (value: number) => [value, t('criteriaScoreDistributions.label')],
    [t]
  );

  return (
    <ResponsiveContainer width="100%" height={360}>
      <BarChart width={430} height={360} data={data}>
        <XAxis dataKey="label" />
        <YAxis />
        <Tooltip formatter={tooltipFormatter} />
        <Bar dataKey="value" fill="#1282b2" />
      </BarChart>
    </ResponsiveContainer>
  );
};

interface Props {
  uid: string;
}

const CriteriaScoreDistributions = ({ uid }: Props) => {
  const { name: pollName } = useCurrentPoll();
  const [criteriaScoresDistributions, setCriteriaScoresDistributions] =
    useState<CriteriaDistributionScore[]>([]);
  const [selectedCriteria, setSelectedCriteria] = useState<string>('');

  useEffect(() => {
    const load = async () => {
      const result =
        await PollsService.pollsEntitiesCriteriaScoresDistributionsRetrieve({
          name: pollName,
          uid,
        });
      setCriteriaScoresDistributions(result.criteria_scores_distributions);
    };
    load();
  }, [uid, pollName]);

  const criteriaDistributionScore = useMemo(
    () =>
      criteriaScoresDistributions.find(
        ({ criteria }) => criteria === selectedCriteria
      ),
    [selectedCriteria, criteriaScoresDistributions]
  );

  return (
    <>
      <CriteriaSelector
        criteria={selectedCriteria}
        setCriteria={setSelectedCriteria}
      />
      {criteriaDistributionScore && (
        <CriteriaDistributionScoreChart
          criteriaDistributionScore={criteriaDistributionScore}
        />
      )}
    </>
  );
};

export default CriteriaScoreDistributions;
