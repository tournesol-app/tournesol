import { useCallback } from 'react';
import { getUidForComparison } from 'src/utils/video';

interface UseSuggestionsProps {
  uidA: string | null;
  uidB: string | null;
  pollName: string;
}

export const useSuggestions = ({
  uidA,
  uidB,
  pollName,
}: UseSuggestionsProps) => {
  const nextSuggestion = useCallback(async () => {
    return await getUidForComparison(uidA, uidB, pollName);
  }, [uidA, uidB, pollName]);

  return {
    nextSuggestion,
  };
};
