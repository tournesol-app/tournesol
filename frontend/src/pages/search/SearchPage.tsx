import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useHistory, useLocation } from 'react-router-dom';

import { Alert, Box } from '@mui/material';

import {
  BackIconButton,
  ContentBox,
  ContentHeader,
  LoaderWrapper,
  Pagination,
  PreferencesIconButtonLink,
} from 'src/components';
import { useCurrentPoll } from 'src/hooks';
import EntityList from 'src/features/entities/EntityList';
import { selectLogin } from 'src/features/login/loginSlice';
import ShareMenuButton from 'src/features/menus/ShareMenuButton';
import SearchFilter from 'src/features/recommendation/SearchFilter';
import { PaginatedRecommendationList } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';

const ENTITIES_LIMIT = 20;

const SearchPage = () => {
  const { t } = useTranslation();

  const history = useHistory();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const offset = Number(searchParams.get('offset') || 0);

  const { name: pollName, criterias, options } = useCurrentPoll();
  const loginState = useSelector(selectLogin);

  const [isLoading, setIsLoading] = useState(true);
  const [loadingError, setLoadingError] = useState(false);
  const [entities, setEntities] = useState<PaginatedRecommendationList>({
    count: 0,
    results: [],
  });

  const onOffsetChange = (newOffset: number) => {
    searchParams.set('offset', newOffset.toString());
    history.push({ search: searchParams.toString() });
  };

  useEffect(() => {
    // `searchParams` is defined as a mutable object outside of this effect.
    // It's safer to recreate it here, instead of adding a dependency to the
    // current effect.
    const searchString = new URLSearchParams(location.search);
    searchString.set('offset', offset.toString());

    if (searchString.get('language') === null) {
      searchString.set('language', '');
      history.replace({ search: searchString.toString() });
      return;
    }

    const fetchEntities = async () => {
      setIsLoading(true);
      try {
        const newEntities = await getRecommendations(
          pollName,
          ENTITIES_LIMIT,
          searchString.toString(),
          criterias,
          options
        );
        setEntities(newEntities);
        setLoadingError(false);
      } catch (error) {
        console.log(error);
        setLoadingError(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEntities();
  }, [criterias, history, location.search, offset, options, pollName]);

  const createBackButtonPath = () => {
    const backPath = loginState.backPath;
    const backParams = loginState.backParams;

    if (!backPath) {
      return '';
    }

    return backParams ? backPath + '?' + backParams : backPath;
  };

  const backButtonPath = createBackButtonPath();

  return (
    <>
      <ContentHeader
        title={t('searchPage.search')}
        subtitle={t('searchPage.exploreTheRecommendationsUsingSearchFilters')}
      />
      <ContentBox noMinPaddingX maxWidth="lg">
        <Box
          sx={{
            px: { xs: 2, sm: 0 },
          }}
        >
          <SearchFilter
            appearExpanded
            extraActions={
              <Box
                sx={{
                  display: 'flex',
                  gap: 1,
                }}
              >
                <ShareMenuButton isIcon />
                {backButtonPath && <BackIconButton path={backButtonPath} />}
                <PreferencesIconButtonLink hash={`#${pollName}-search`} />
              </Box>
            }
          />
        </Box>
        {loadingError && !isLoading && entities.count === 0 && (
          <Box
            sx={{
              mb: 1,
              px: { xs: 2, sm: 0 },
            }}
          >
            <Alert severity="warning">
              {t('genericError.errorOnLoadingTryAgainLater')}
            </Alert>
          </Box>
        )}
        <LoaderWrapper isLoading={isLoading}>
          <EntityList
            entities={entities.results}
            emptyMessage={
              isLoading ? '' : t('entityList.noItemMatchesYourFilters')
            }
          />
        </LoaderWrapper>
        {!isLoading && (entities.count ?? 0) > 0 && (
          <Pagination
            offset={offset}
            count={entities.count ?? 0}
            onOffsetChange={onOffsetChange}
            limit={ENTITIES_LIMIT}
          />
        )}
      </ContentBox>
    </>
  );
};

export default SearchPage;
