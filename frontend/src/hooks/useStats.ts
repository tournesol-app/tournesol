import { useState, useEffect, useContext } from 'react';
import StatsContext from 'src/features/statistics/StatsContext';
import { Statistics } from 'src/services/openapi';

export const useStats = () => {
  const { getStats } = useContext(StatsContext);
  const [stats, setStats] = useState<Statistics>(getStats());

  useEffect(() => {
    setStats(getStats());
  }, [getStats]);

  return stats;
};
