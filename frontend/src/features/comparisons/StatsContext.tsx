import React, { createContext, useCallback, useMemo, useState } from 'react';
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

export const StatsContext = createContext<StatsContextValue>({
  stats: initialState,
  refreshStats: () => undefined,
  getStats: () => initialState,
});

export const StatsProvider = ({ children }: { children: React.ReactNode }) => {
  const [stats, setStats] = useState(initialState);

  const refreshStats = useCallback(async () => {
		const refreshedStats = await StatsService.statsRetrieve();
		setStats(refreshedStats);
  }, []);

  const getStats = useCallback(() => {
		if(stats===initialState){
			console.log("coucuo");
			refreshStats();
			return stats;
		}
		return stats;
	}, []);

	const contextValue = useMemo(
    () => ({
      stats,
      refreshStats,
			getStats,
    }),
    [stats]
  );

  return (
    <StatsContext.Provider value={contextValue}>
      {children}
    </StatsContext.Provider>
  );
};
