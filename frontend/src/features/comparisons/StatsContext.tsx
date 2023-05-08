import React, {
  createContext,
  useCallback,
  useMemo,
  useRef,
  useState,
} from 'react';
import { Statistics, StatsService } from 'src/services/openapi';

interface StatsContextValue {
  stats: Statistics;
  refreshStats: () => void;
  getStats: () => Statistics;
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
  refreshStats: () => undefined,
  getStats: () => initialState,
});

export const StatsLazyProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const loading = useRef(false);
  const [stats, setStats] = useState(initialState);

  const refreshStats = useCallback(async () => {
    setStats(await StatsService.statsRetrieve());
    loading.current = false;
  }, []);

  /**
   * Return the current `stats` if any, else refresh them.
   */
  const getStats = useCallback(() => {
    if (stats.polls.length === 0 && !loading.current) {
      loading.current = true;
      refreshStats();
      return initialState;
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
