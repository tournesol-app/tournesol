/**
 * Functions and shortcuts used to interact with the Tournesol's comparisons
 * API.
 */

import { Comparison, UsersService } from 'src/services/openapi';

export async function getUserComparisons(
  pollName: string,
  limit: number
): Promise<Comparison[]> {
  const comparisons = await UsersService.usersMeComparisonsList({
    pollName,
    limit: limit,
  });

  return comparisons.results || [];
}
