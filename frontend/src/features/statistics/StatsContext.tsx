import React, {
  createContext,
  useCallback,
  useMemo,
  useRef,
  useState,
} from 'react';
import {
  CancelError,
  CancelablePromise,
  Statistics,
  StatsService,
} from 'src/services/openapi';

// Stats are considered outdated after this amount of miliseconds.
const EXPIRATION_TIME = 4000;

interface StatsContextValue {
  stats: Statistics;
  getStats: (poll: string) => Statistics;
  refreshStats: (poll: string) => void;
}

const initialState: Statistics = {
  active_users: {
    total: 0,
    joined_last_month: 0,
    joined_last_30_days: 0,
  },
  polls: [],
};

const StatsContext = createContext<StatsContextValue>({
  stats: initialState,
  getStats: () => initialState,
  refreshStats: () => undefined,
});

export const StatsLazyProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const loading = useRef<CancelablePromise<Statistics> | null>(null);
  const lastRefreshAt = useRef(0);
  const lastPoll = useRef<string | undefined>(undefined);

  const [stats, setStats] = useState(initialState);

  const refreshStats = useCallback(async (poll: string) => {
    if (loading.current) {
      loading.current.cancel();
    }
    loading.current = StatsService.statsRetrieve({ poll });
    try {
      const newStats = await loading.current;
      lastRefreshAt.current = Date.now();
      loading.current = null;
      setStats(newStats);
    } catch (err) {
      if (err instanceof CancelError) {
        return;
      }
      console.error(err);
    }
  }, []);

  /**
   * Initialize the stats if they are empty or refresh them if they are
   * outdated.
   *
   * Note that the getStats implementation assumes that only the stats of a
   * single poll are displayed per page.
   */
  const getStats = useCallback(
    (poll: string) => {
      const currentTime = Date.now();

      if (loading.current) {
        if (poll === lastPoll.current) {
          return stats;
        } else {
          lastPoll.current = poll;
          refreshStats(poll);
        }
      } else {
        if (
          stats.polls.length === 0 ||
          poll !== lastPoll.current ||
          currentTime - lastRefreshAt.current >= EXPIRATION_TIME
        ) {
          lastPoll.current = poll;
          refreshStats(poll);
        }
      }

      return stats;
    },
    [stats, refreshStats]
  );

  const contextValue = useMemo(
    () => ({
      stats,
      getStats,
      refreshStats,
    }),
    [stats, getStats, refreshStats]
  );

  return (
    <StatsContext.Provider value={contextValue}>
      {children}
    </StatsContext.Provider>
  );
};

export default StatsContext;
