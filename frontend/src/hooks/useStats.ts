import { useState, useEffect, useContext } from 'react';
import StatsContext from 'src/features/statistics/StatsContext';
import { Statistics } from 'src/services/openapi';

interface Props {
  poll: string;
}

export const useStats = ({ poll }: Props) => {
  const { getStats } = useContext(StatsContext);
  const [stats, setStats] = useState<Statistics>(getStats(poll));

  useEffect(() => {
    setStats(getStats(poll));
  }, [poll, getStats]);

  return stats;
};
