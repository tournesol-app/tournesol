import { Statistics, StatsService } from 'src/services/openapi';
import { PollStats } from '../types';

export const DEFAULT_POLL_STATS = {
  // "active_users"
  userCount: 0,
  lastMonthUserCount: 0,
  lastThirtyDaysUserCount: 0,
  // "compared_entities"
  comparedEntityCount: 0,
  lastMonthComparedEntityCount: 0,
  lastThirtyDaysComparedEntityCount: 0,
  // "comparisons"
  comparisonCount: 0,
  lastMonthComparisonCount: 0,
  lastThirtyDaysComparisonCount: 0,
  currentWeekComparisonCount: 0,
};

export async function getPollStats(
  pollName: string
): Promise<PollStats | undefined> {
  const stats: Statistics = await StatsService.statsRetrieve();
  const pollStats = stats.polls.find(({ name }) => name === pollName);
  if (pollStats === undefined) return;

  return {
    userCount: stats.active_users.total,
    comparedEntityCount: pollStats.compared_entities.total,
    comparisonCount: pollStats.comparisons.total,
    lastMonthUserCount: stats.active_users.joined_last_month,
    lastMonthComparedEntityCount: pollStats.compared_entities.added_last_month,
    lastMonthComparisonCount: pollStats.comparisons.added_last_month,
    lastThirtyDaysUserCount: stats.active_users.joined_last_30_days,
    lastThirtyDaysComparedEntityCount:
      pollStats.compared_entities.added_last_30_days,
    lastThirtyDaysComparisonCount: pollStats.comparisons.added_last_30_days,
    currentWeekComparisonCount: pollStats.comparisons.added_current_week,
  };
}
