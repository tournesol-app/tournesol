import { useCallback } from 'react';
import { autoHistory } from 'src/features/rateLater/autoSuggestions';
import { getUidForComparison } from 'src/utils/video';

export const useSuggestions = () => {
  const nextSuggestion = useCallback(
    async (uidA: string | null, uidB: string | null, pollName: string) => {
      if (autoHistory.hasNext(pollName)) {
        return autoHistory.next(pollName);
      }

      return await getUidForComparison(uidA, uidB, pollName);
    },
    []
  );

  const previousSuggestion = useCallback((pollName: string) => {
    return autoHistory.previous(pollName);
  }, []);

  return {
    nextSuggestion,
    previousSuggestion,
  };
};
