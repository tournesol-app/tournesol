import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from 'react';
import { ContributorCriteriaScore } from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { UsersService } from 'src/services/openapi';
import { useLoginState } from 'src/hooks';

type ReasonWhyPersonalScoresCannotBeActivated =
  | undefined
  | 'notLoggedIn'
  | 'noPersonalScore'
  | 'noVideoId'
  | 'contextProviderMissing'
  | 'unknownError';

interface UsePersonalCriteriaScoresValue {
  canActivatePersonalScores: boolean;
  reasonWhyPersonalScoresCannotBeActivated: ReasonWhyPersonalScoresCannotBeActivated;
  personalScoresActivated: boolean;
  setPersonalScoresActivated: (activated: boolean) => void;
  personalCriteriaScores?: ContributorCriteriaScore[];
}

const PersonalCriteriaScoresContext =
  createContext<UsePersonalCriteriaScoresValue>({
    canActivatePersonalScores: false,
    reasonWhyPersonalScoresCannotBeActivated: 'contextProviderMissing',
    personalScoresActivated: false,
    setPersonalScoresActivated: () => undefined,
  });

export const PersonalCriteriaScoresContextProvider = ({
  uid,
  children,
}: {
  uid: string;
  children: React.ReactNode;
}) => {
  const { name: pollName } = useCurrentPoll();
  const { isLoggedIn } = useLoginState();
  const [contextValue, setContextValue] =
    useState<UsePersonalCriteriaScoresValue>({
      canActivatePersonalScores: false,
      reasonWhyPersonalScoresCannotBeActivated: undefined,
      personalScoresActivated: false,
      setPersonalScoresActivated: (activated: boolean) =>
        setContextValue((value) => ({
          ...value,
          personalScoresActivated: activated,
        })),
    });

  const { personalScoresActivated } = contextValue;

  const setCannotActivatePersonalScores = useCallback(
    (reason: ReasonWhyPersonalScoresCannotBeActivated) => {
      setContextValue((value) => ({
        ...value,
        canActivatePersonalScores: false,
        personalScoresActivated: false,
        reasonWhyPersonalScoresCannotBeActivated: reason,
        personalCriteriaScores: undefined,
      }));
    },
    []
  );

  useEffect(() => {
    if (pollName === undefined || uid === undefined) {
      setCannotActivatePersonalScores('noVideoId');
      return;
    }
    if (!isLoggedIn) {
      setCannotActivatePersonalScores('notLoggedIn');
      return;
    }
    const load = async () => {
      let contributorRating;
      try {
        contributorRating =
          await UsersService.usersMeContributorRatingsRetrieve({
            pollName,
            uid,
          });
      } catch (e) {
        const reason = e.status === 404 ? 'noPersonalScore' : 'unknownError';
        setCannotActivatePersonalScores(reason);
        return;
      }
      const personalCriteriaScores =
        contributorRating.individual_rating.criteria_scores;
      if (personalCriteriaScores.length === 0) {
        setCannotActivatePersonalScores('noPersonalScore');
        return;
      }
      setContextValue((value) => ({
        ...value,
        canActivatePersonalScores: true,
        reasonWhyPersonalScoresCannotBeActivated: undefined,
        personalCriteriaScores,
      }));
    };
    load();
  }, [
    personalScoresActivated,
    pollName,
    uid,
    isLoggedIn,
    setCannotActivatePersonalScores,
  ]);

  return (
    <PersonalCriteriaScoresContext.Provider value={contextValue}>
      {children}
    </PersonalCriteriaScoresContext.Provider>
  );
};

const usePersonalCriteriaScores = (): UsePersonalCriteriaScoresValue =>
  useContext(PersonalCriteriaScoresContext);

export default usePersonalCriteriaScores;
