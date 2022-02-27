import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { PollContext } from 'src/app/poll';
import { PollsService, PollCriteria, Poll } from 'src/services/openapi';
import { polls } from 'src/utils/constants';

const pollsCache: Record<string, Promise<Poll>> = {};

const getPoll = async (name: string, currentLang: string) => {
  const cacheKey = `${name},${currentLang}`;
  if (!pollsCache[cacheKey]) {
    pollsCache[cacheKey] = PollsService.pollsRetrieve({ name });
  }
  return await pollsCache[cacheKey];
};

export const useCurrentPoll = () => {
  const { i18n } = useTranslation();
  const { name } = React.useContext(PollContext);

  // FIXME: criterias should not be empty on first render if value is cached
  const [criterias, setCriterias] = React.useState<PollCriteria[]>([]);

  const pollOptions = polls.find((p) => p.name === name);
  const withSearchBar = pollOptions?.withSearchBar || false;

  const getCriteriaLabel = (criteriaName: string) =>
    criterias.find((c) => c.name === criteriaName)?.label ?? '';

  const criteriaByName = React.useMemo(() => {
    return Object.fromEntries(criterias.map((c) => [c.name, c]));
  }, [criterias]);

  useEffect(() => {
    const loadCriterias = async () => {
      const poll = await getPoll(name, i18n.resolvedLanguage);
      setCriterias(poll.criterias);
    };
    loadCriterias();
  }, [name, i18n.resolvedLanguage]);

  return {
    name,
    criterias,
    withSearchBar,
    getCriteriaLabel,
    criteriaByName,
  };
};
