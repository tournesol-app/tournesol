import { useCallback } from 'react';
import {
  selectorAHistory as historyA,
  selectorBHistory as historyB,
} from 'src/features/entity_selector/EntitySelectorHistory';
import {
  autoSuggestionsRandom,
  fillAutoSuggestions,
  isAutoSuggestionsEmpty,
} from 'src/features/rateLater/autoSuggestions';
import { UsersService } from 'src/services/openapi';

export async function randomUidFromSuggestions(
  poll: string,
  exclude: Array<string | null>
): Promise<string | null> {
  const excluded = exclude.filter((elem) => elem != null) as string[];

  if (isAutoSuggestionsEmpty(poll)) {
    const suggestions = await UsersService.usersMeSuggestionsTocompareList({
      pollName: poll,
    });

    if (suggestions && suggestions.length > 0) {
      fillAutoSuggestions(
        poll,
        suggestions.map((item) => item.entity.uid),
        excluded
      );
    }
  }

  if (isAutoSuggestionsEmpty(poll)) {
    return null;
  }

  return autoSuggestionsRandom(poll, excluded);
}

export type HistoryId = 'A' | 'B';

export const useSuggestions = () => {
  /**
   * Return a new UID to compare from the suggestion pool.
   *
   * If the history has been browsed backwards, return the next entry in the
   * history instead.
   */
  const nextSuggestion = useCallback(
    async (
      pollName: string,
      exclude: Array<string | null>,
      historyId: HistoryId
    ) => {
      const history = historyId === 'A' ? historyA : historyB;

      if (history.hasNext(pollName)) {
        return history.next(pollName);
      }

      const suggestion = await randomUidFromSuggestions(pollName, exclude);

      if (suggestion) {
        history.push(pollName, suggestion);
      }

      return suggestion;
    },
    []
  );

  /**
   * Return the UID preceding the current point in the history.
   */
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
