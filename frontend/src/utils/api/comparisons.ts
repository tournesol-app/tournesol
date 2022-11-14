/**
 * Functions and shortcuts used to interact with the Tournesol's comparisons
 * API.
 */

import {
  Comparison,
  PaginatedComparisonList,
  UsersService,
} from 'src/services/openapi';

export async function getUserComparisons(
  pollName: string,
  limit: number
): Promise<Comparison[]> {
  const comparisons = await getUserComparisonsRaw(pollName, limit);
  return comparisons.results || [];
}

export async function getUserComparisonsRaw(
  pollName: string,
  limit: number
): Promise<PaginatedComparisonList> {
  const comparisons = await UsersService.usersMeComparisonsList({
    pollName,
    limit: limit,
  });

  return comparisons;
}
