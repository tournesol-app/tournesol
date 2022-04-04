import { useEffect } from 'react';
import { LAST_POLL_NAME_STORAGE_KEY, polls } from 'src/utils/constants';
import { useCurrentPoll } from './useCurrentPoll';

const lastSessionPollName = localStorage?.getItem(LAST_POLL_NAME_STORAGE_KEY);

const useLastPoll = () => {
  // Hook that will activate the last poll that was persisted
  // in localStorage during a previous session
  const { name: currentPollName, setPollName } = useCurrentPoll();

  useEffect(() => {
    if (
      lastSessionPollName != null &&
      lastSessionPollName !== currentPollName &&
      polls.map((p) => p.name).includes(lastSessionPollName)
    ) {
      setPollName(lastSessionPollName);
    }
  }, [currentPollName, setPollName]);
};

export default useLastPoll;
