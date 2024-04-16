import { useCallback } from 'react';
import {
  selectorAHistory as historyA,
  selectorBHistory as historyB,
} from 'src/features/entity_selector/EntitySelectorHistory';
import { getUidForComparison } from 'src/utils/video';

export type HistoryId = 'A' | 'B';

export const useSuggestions = () => {
  const nextSuggestion = useCallback(
    async (
      uidA: string | null,
      uidB: string | null,
      pollName: string,
      historyId: HistoryId
    ) => {
      const history = historyId === 'A' ? historyA : historyB;

      if (history.hasNext(pollName)) {
        return history.next(pollName);
      }

      const suggestion = await getUidForComparison(uidA, uidB, pollName);

      if (suggestion) {
        history.push(pollName, suggestion);
      }

      return suggestion;
    },
    []
  );

  const previousSuggestion = useCallback(
    (pollName: string, historyId: HistoryId) => {
      const history = historyId === 'A' ? historyA : historyB;
      return history.previous(pollName);
    },
    []
  );

  return {
    nextSuggestion,
    previousSuggestion,
  };
};
