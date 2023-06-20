import React, {
  useCallback,
  useContext,
  useEffect,
  useState,
  useMemo,
} from 'react';
import { useTranslation } from 'react-i18next';
import { PollsService, Poll } from 'src/services/openapi';
import { LAST_POLL_NAME_STORAGE_KEY, polls } from 'src/utils/constants';
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
  const currentLang = i18n.resolvedLanguage || i18n.language;

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
    setContextValue((value) =>
      value.name !== name
        ? {
            ...value,
            name: name,
            poll: undefined,
          }
        : value
    );
  }, []);

  useEffect(() => {
    // Expose setPollName callback after this provider itself
    // has been initialized.
    setContextValue((value) => ({
      ...value,
      setPollName,
    }));
  }, [setPollName]);

  useEffect(() => {
    // Persist the last poll in localStorage for future sessions (after signup, etc.)
    if (localStorage) {
      localStorage.setItem(LAST_POLL_NAME_STORAGE_KEY, contextValue.name);
    }
  }, [contextValue.name]);

  useEffect(() => {
    // Fetch poll details from API, whenever the current context relates to another poll,
    // or the UI language has changed.
    getPoll(contextValue.name, currentLang).then((poll) => {
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
  }, [currentLang, contextValue.name]);

  return (
    <pollContext.Provider value={contextValue}>{children}</pollContext.Provider>
  );
};

export const useCurrentPoll = () => {
  const contextValue = useContext(pollContext);
  const poll = contextValue.poll;

  const criteriaByName = useMemo(() => {
    const criterias = poll?.criterias ?? [];
    return Object.fromEntries(criterias.map((c) => [c.name, c]));
  }, [poll?.criterias]);

  const getCriteriaLabel = (criteriaName: string) =>
    criteriaByName[criteriaName]?.label;

  const pollOptions = useMemo(
    () => polls.find((p) => p.name === contextValue.name),
    [contextValue.name]
  );

  return {
    ...contextValue,
    active: contextValue.poll?.active ?? false,
    baseUrl: pollOptions?.path.replace(/\/+$/g, ''),
    criterias: poll?.criterias ?? [],
    options: pollOptions,
    getCriteriaLabel,
    criteriaByName,
    isReady: contextValue.poll != undefined,
  };
};
