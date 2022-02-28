import React, {
  useCallback,
  useContext,
  useEffect,
  useState,
  useMemo,
} from 'react';
import { useTranslation } from 'react-i18next';
import { PollsService, Poll } from 'src/services/openapi';
import { polls } from 'src/utils/constants';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';

const pollsCache: Record<string, Promise<Poll>> = {};

const getPoll = async (name: string, currentLang: string) => {
  const cacheKey = `${name},${currentLang}`;
  if (!pollsCache[cacheKey]) {
    pollsCache[cacheKey] = PollsService.pollsRetrieve({ name });
  }
  return await pollsCache[cacheKey];
};

interface PollContextValue {
  name: string;
  poll?: Poll;
  setPollName: (name: string) => void;
}

const pollContext = React.createContext<PollContextValue>({
  name: YOUTUBE_POLL_NAME,
  setPollName: () => undefined,
});

export const PollProvider = ({ children }: { children: React.ReactNode }) => {
  const { i18n } = useTranslation();

  const initPollContext = () => {
    const pollName =
      polls.find((p) => location.pathname.startsWith(p.path))?.name ??
      YOUTUBE_POLL_NAME;
    return {
      name: pollName,
      setPollName: () => undefined,
    };
  };

  const [contextValue, setContextValue] =
    useState<PollContextValue>(initPollContext);

  const setPollName = useCallback((name: string) => {
    setContextValue((value) => ({
      ...value,
      name: name,
      poll: undefined,
    }));
  }, []);

  useEffect(() => {
    console.info('POLL');
    setContextValue((value) => ({
      ...value,
      setPollName,
    }));
  }, [setPollName]);

  useEffect(() => {
    getPoll(contextValue.name, i18n.resolvedLanguage).then((poll) => {
      setContextValue((value) => {
        if (value.name === poll.name) {
          return {
            ...value,
            poll,
          };
        }
        return value;
      });
    });
  }, [i18n.resolvedLanguage, contextValue.name]);

  return (
    <pollContext.Provider value={contextValue}>{children}</pollContext.Provider>
  );
};

export const useCurrentPoll = () => {
  const contextValue = useContext(pollContext);
  const poll = contextValue.poll;

  const getCriteriaLabel = (criteriaName: string) =>
    (poll?.criterias || []).find((c) => c.name === criteriaName)?.label ?? '';

  const criteriaByName = React.useMemo(() => {
    const criterias = poll?.criterias ?? [];
    return Object.fromEntries(criterias.map((c) => [c.name, c]));
  }, [poll?.criterias]);

  const pollOptions = useMemo(
    () => polls.find((p) => p.name === contextValue.name),
    [contextValue.name]
  );

  return {
    ...contextValue,
    criterias: poll?.criterias ?? [],
    options: pollOptions,
    getCriteriaLabel,
    criteriaByName,
    isReady: contextValue.poll != undefined,
  };
};
