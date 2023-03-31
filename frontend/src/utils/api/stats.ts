import { StatsService } from 'src/services/openapi';
import { PollStats } from '../types';

export const DEFAULT_POLL_STATS = {
  userCount: 0,
  lastMonthUserCount: 0,
  comparedEntityCount: 0,
  lastMonthComparedEntityCount: 0,
  comparisonCount: 0,
  lastMonthComparisonCount: 0,
};

export async function getPollStats(
  pollName: string
): Promise<PollStats | undefined> {
  const stats = await StatsService.statsRetrieve();
  const pollStats = stats.polls.find(({ name }) => name === pollName);
  if (pollStats === undefined) return;

  return {
    userCount: stats.active_users.total,
    comparedEntityCount: pollStats.compared_entities.total,
    comparisonCount: pollStats.comparisons.total,
    lastMonthUserCount: stats.active_users.joined_last_month,
    lastMonthComparedEntityCount: pollStats.compared_entities.added_last_month,
    lastMonthComparisonCount: pollStats.comparisons.added_last_month,
  };
}
