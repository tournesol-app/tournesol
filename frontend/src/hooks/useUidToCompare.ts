import { useCallback } from 'react';
import { getUidForComparison } from 'src/utils/video';

export const useUidToCompare = ({
  currentUid,
  otherUid,
  pollName,
}: {
  currentUid: string | null;
  otherUid: string | null;
  pollName: string;
}) => {
  const nextSuggestion = useCallback(async () => {
    return await getUidForComparison(
      currentUid || '',
      otherUid ? otherUid : null,
      pollName
    );
  }, [currentUid, otherUid, pollName]);

  return {
    nextSuggestion,
  };
};
