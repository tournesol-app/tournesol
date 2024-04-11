import { useCallback } from 'react';
import { getUidForComparison } from 'src/utils/video';

export const useSuggestions = () => {
  const nextSuggestion = useCallback(async (uidA, uidB, pollName) => {
    return await getUidForComparison(uidA, uidB, pollName);
  }, []);

  return {
    nextSuggestion,
  };
};
