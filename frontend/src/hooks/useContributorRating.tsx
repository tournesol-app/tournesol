import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from 'react';
import { useLoginState } from 'src/hooks';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import {
  ContributorCriteriaScore,
  ContributorRating,
} from 'src/services/openapi';
import { getContributorRating } from 'src/utils/api/contributorRatings';

type ReasonWhyPersonalScoresCannotBeActivated =
  | undefined
  | 'notLoggedIn'
  | 'noPersonalScore'
  | 'noVideoId'
  | 'contextProviderMissing'
  | 'unknownError';

interface UseContributorRatingValue {
  loading: boolean;
  canActivatePersonalScores: boolean;
  reasonWhyPersonalScoresCannotBeActivated: ReasonWhyPersonalScoresCannotBeActivated;
  personalScoresActivated: boolean;
  setPersonalScoresActivated: (activated: boolean) => void;
  contributorRating?: ContributorRating | null;
  loadContributorRating?: () => Promise<void>;
  personalCriteriaScores?: ContributorCriteriaScore[];
}

const ContributorRatingContext = createContext<UseContributorRatingValue>({
  loading: true,
  canActivatePersonalScores: false,
  reasonWhyPersonalScoresCannotBeActivated: 'contextProviderMissing',
  personalScoresActivated: false,
  setPersonalScoresActivated: () => undefined,
});

export const ContributorRatingContextProvider = ({
  uid,
  children,
}: {
  uid?: string | null;
  children: React.ReactNode;
}) => {
  const { name: pollName } = useCurrentPoll();
  const { isLoggedIn } = useLoginState();

  const [contextValue, setContextValue] = useState<UseContributorRatingValue>({
    loading: true,
    canActivatePersonalScores: false,
    reasonWhyPersonalScoresCannotBeActivated: undefined,
    personalScoresActivated: false,
    setPersonalScoresActivated: (activated: boolean) =>
      setContextValue((value) => ({
        ...value,
        personalScoresActivated: activated,
      })),
  });

  const setCannotActivatePersonalScores = useCallback(
    (
      reason: ReasonWhyPersonalScoresCannotBeActivated,
      contributorRating?: ContributorRating
    ) => {
      setContextValue((value) => ({
        ...value,
        loading: false,
        canActivatePersonalScores: false,
        personalScoresActivated: false,
        reasonWhyPersonalScoresCannotBeActivated: reason,
        personalCriteriaScores: undefined,
        contributorRating: contributorRating,
      }));
    },
    []
  );

  const loadContributorRating = useCallback(async () => {
    if (!pollName || !uid) {
      setCannotActivatePersonalScores('noVideoId');
      return;
    }
    if (!isLoggedIn) {
      setCannotActivatePersonalScores('notLoggedIn');
      return;
    }

    setContextValue((value) => ({
      ...value,
      loading: true,
      loadContributorRating,
    }));

    let rating: ContributorRating | null = null;

    try {
      rating = await getContributorRating(pollName, uid);
    } catch {
      setCannotActivatePersonalScores('unknownError');
      return;
    }

    if (!rating) {
      setCannotActivatePersonalScores('noPersonalScore');
      return;
    }

    const personalCriteriaScores = rating.individual_rating.criteria_scores;

    if (personalCriteriaScores.length === 0) {
      setCannotActivatePersonalScores('noPersonalScore', rating);
      return;
    }

    setContextValue((value) => ({
      ...value,
      loading: false,
      canActivatePersonalScores: true,
      reasonWhyPersonalScoresCannotBeActivated: undefined,
      personalCriteriaScores,
      contributorRating: rating,
    }));
  }, [isLoggedIn, pollName, setCannotActivatePersonalScores, uid]);

  useEffect(() => {
    loadContributorRating();
  }, [loadContributorRating]);

  return (
    <ContributorRatingContext.Provider value={contextValue}>
      {children}
    </ContributorRatingContext.Provider>
  );
};

const useContributorRating = (): UseContributorRatingValue =>
  useContext(ContributorRatingContext);

export default useContributorRating;
