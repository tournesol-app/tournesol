import React, {
  createContext,
  useCallback,
  useMemo,
  useRef,
  useState,
} from 'react';
import { Statistics, StatsService } from 'src/services/openapi';

// Stats are considered outdated after this amount of miliseconds.
const EXPIRATION_TIME = 4000;

interface StatsContextValue {
  stats: Statistics;
  getStats: () => Statistics;
  refreshStats: () => void;
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
  const loading = useRef(false);
  const lastRefreshAt = useRef(0);

  const [stats, setStats] = useState(initialState);

  const refreshStats = useCallback(async () => {
    setStats(await StatsService.statsRetrieve());
    loading.current = false;
    lastRefreshAt.current = Date.now();
  }, []);

  /**
   * Return the current `stats` if any, else refresh them.
   */
  const getStats = useCallback(() => {
    const currentTime = Date.now();

    // Initialize the stats if they are empty.
    if (stats.polls.length === 0 && !loading.current) {
      loading.current = true;
      refreshStats();
      return initialState;
    }

    // Refresh the stats when the existing stats are outdated.
    if (
      stats.polls.length !== 0 &&
      currentTime - lastRefreshAt.current >= EXPIRATION_TIME
    ) {
      refreshStats();
      return stats;
    }

    return stats;
  }, [stats, refreshStats]);

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
