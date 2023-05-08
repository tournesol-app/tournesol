import { useState, useEffect, useContext } from 'react';
import StatsContext from 'src/features/comparisons/StatsContext';
import { Statistics } from 'src/services/openapi';

export const useStats = () => {
  const [stats, setStats] = useState<Statistics>();

  const { getStats } = useContext(StatsContext);

  useEffect(() => {
    setStats(getStats());
  }, [getStats]);

  return stats;
};
