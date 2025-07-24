import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Chip, Grid } from '@mui/material';
import { Person } from '@mui/icons-material';

import { ContentBox, ContentHeader, LoaderWrapper } from 'src/components';
import Pagination from 'src/components/Pagination';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import EntityList from 'src/features/entities/EntityList';
import SearchFilter from 'src/features/recommendation/SearchFilter';
import ShareMenuButton from 'src/features/menus/ShareMenuButton';
import type {
  PaginatedContributorRecommendationsList,
  PaginatedRecommendationList,
} from 'src/services/openapi';
import {
  getPublicPersonalRecommendations,
  getRecommendations,
} from 'src/utils/api/recommendations';
import { getRecommendationPageName } from 'src/utils/constants';

/**
 * Display a collective or personal recommendations.
 *
 * The page also display a the search filters allowed in the current poll.
 */
function RecommendationsPage() {
  const { t } = useTranslation();

  const navigate = useNavigate();
  const location = useLocation();
  const { baseUrl, name: pollName, criterias, options } = useCurrentPoll();
  const langsAutoDiscovery = options?.defaultRecoLanguageDiscovery ?? false;

  const [isLoading, setIsLoading] = useState(true);

  const allowPublicPersonalRecommendations =
    options?.allowPublicPersonalRecommendations ?? false;
  const { username } = useParams<{ username: string }>();

  // Can be compared to the current pathname, to determine if the
  // desired recommendations are collective or personal.
  const collectiveRecoPathname = `${baseUrl}/recommendations`;

  const displayPersonalRecommendations =
    allowPublicPersonalRecommendations &&
    location.pathname !== collectiveRecoPathname &&
    username !== undefined;

  const prov:
    | PaginatedRecommendationList
    | PaginatedContributorRecommendationsList = {
    count: 0,
    results: [],
  };

  const [entities, setEntities] = useState(prov);
  const entitiesCount = entities.count || 0;
  const searchParams = new URLSearchParams(location.search);

  const limit = 20;
  const offset = Number(searchParams.get('offset') || 0);

  const locationSearchRef = useRef<string>();

  function handleOffsetChange(newOffset: number) {
    searchParams.set('offset', newOffset.toString());
    navigate({ search: searchParams.toString() });
  }

  useEffect(() => {
    if (location.search === locationSearchRef.current) {
      // This ref is used as a precaution, to avoid triggering
      // this effect redundantly, eg if "history" has changed.
      return;
    }
    locationSearchRef.current = location.search;

    // `searchParams` is defined as a mutable object outside of this
    // effect. So it's safer to recreate it here, instead of adding
    // a dependency to the current effect.
    const searchParams = new URLSearchParams(location.search);
    if (langsAutoDiscovery && searchParams.get('language') === null) {
      searchParams.set('language', '');
      navigate({ search: searchParams.toString() }, { replace: true });
      return;
    }

    const fetchEntities = async () => {
      setIsLoading(true);

      const newEntities = displayPersonalRecommendations
        ? // Get personal recommendations.
          await getPublicPersonalRecommendations(
            username,
            pollName,
            limit,
            location.search,
            criterias,
            options
          )
        : // Get collective recommendations.
          await getRecommendations(
            pollName,
            limit,
            location.search,
            criterias,
            options
          );

      // A response corresponding to a previous filter state is ignored.
      if (locationSearchRef.current === location.search) {
        setEntities(newEntities);
        setIsLoading(false);
      }
    };

    fetchEntities();
  }, [
    criterias,
    displayPersonalRecommendations,
    langsAutoDiscovery,
    location.search,
    navigate,
    options,
    pollName,
    username,
  ]);

  return (
    <>
      {displayPersonalRecommendations ? (
        <ContentHeader
          title={getRecommendationPageName(t, pollName, true)}
          subtitle={
            <Trans
              t={t}
              i18nKey="recommendationsPage.basedOnUserPublicContributions"
            >
              Based on public contributions by{' '}
              <Chip icon={<Person />} label={username} />
            </Trans>
          }
        />
      ) : (
        <ContentHeader title={getRecommendationPageName(t, pollName)} />
      )}
      <ContentBox noMinPaddingX maxWidth="lg">
        <Box
          sx={{
            px: { xs: 2, sm: 0 },
          }}
        >
          <Grid container>
            {/* Filters section. */}
            <Grid item xs={12}>
              {/* Unsafe filter is not available when fetching personal recommendations */}
              <SearchFilter
                disableAdvanced={displayPersonalRecommendations}
                extraActions={
                  <Box
                    sx={{
                      display: 'flex',
                      gap: 1,
                    }}
                  >
                    <ShareMenuButton isIcon />
                  </Box>
                }
              />
            </Grid>
          </Grid>
        </Box>
        <LoaderWrapper isLoading={isLoading}>
          <EntityList
            entities={entities.results}
            emptyMessage={
              isLoading ? '' : t('entityList.noItemMatchesYourFilters')
            }
          />
        </LoaderWrapper>
        {!isLoading && entitiesCount > 0 && (
          <Pagination
            offset={offset}
            count={entitiesCount}
            onOffsetChange={handleOffsetChange}
            limit={limit}
          />
        )}
      </ContentBox>
    </>
  );
}

export default RecommendationsPage;
