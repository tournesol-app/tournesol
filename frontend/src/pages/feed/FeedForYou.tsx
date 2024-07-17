import React, { useEffect, useMemo, useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { useHistory, useLocation } from 'react-router-dom';

import { Alert, Box } from '@mui/material';

import {
  ContentBox,
  ContentHeader,
  InternalLink,
  LoaderWrapper,
  Pagination,
  PreferencesIconButtonLink,
  SearchIconButtonLink,
} from 'src/components';
import EntityList from 'src/features/entities/EntityList';
import { updateBackNagivation } from 'src/features/login/loginSlice';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { useCurrentPoll } from 'src/hooks';
import { PaginatedRecommendationList } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';
import { getFeedForYouDefaultSearchParams } from 'src/utils/userSettings';

const ENTITIES_LIMIT = 20;

const FeedForYou = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();

  const history = useHistory();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const offset = Number(searchParams.get('offset') || 0);

  const { name: pollName, criterias, options } = useCurrentPoll();
  const langsAutoDiscovery = options?.defaultRecoLanguageDiscovery ?? false;
  const userSettings = useSelector(selectSettings).settings;

  const userPreferences: URLSearchParams = useMemo(() => {
    return getFeedForYouDefaultSearchParams(
      pollName,
      options,
      userSettings,
      langsAutoDiscovery
    );
  }, [langsAutoDiscovery, options, pollName, userSettings]);

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
    dispatch(
      updateBackNagivation({
        backPath: location.pathname,
        backParams: '',
      })
    );
  }, [dispatch, location.pathname]);

  useEffect(() => {
    const searchString = new URLSearchParams(userPreferences);
    searchString.append('offset', offset.toString());

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
        console.error(error);
        setLoadingError(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEntities();
  }, [criterias, offset, options, pollName, userPreferences]);

  const makeSearchPageSearchParams = () => {
    const searchPageSearchParams = new URLSearchParams(userPreferences);
    searchPageSearchParams.set('offset', offset.toString());
    return searchPageSearchParams;
  };

  return (
    <>
      <ContentHeader
        title={t('feedForYou.forYou')}
        subtitle={
          <Trans t={t} i18nKey="feedForYou.accordingToYourPreferences">
            According to{' '}
            <InternalLink to={`/settings/preferences#${pollName}-feed-foryou`}>
              your preferences
            </InternalLink>
          </Trans>
        }
      />
      <ContentBox noMinPaddingX maxWidth="lg">
        <Box
          px={{ xs: 2, sm: 0 }}
          mb={1}
          display="flex"
          justifyContent="flex-end"
          gap={1}
        >
          <SearchIconButtonLink
            params={makeSearchPageSearchParams().toString()}
          />
          <PreferencesIconButtonLink hash={`#${pollName}-feed-foryou`} />
        </Box>
        {!isLoading && entities.count === 0 && (
          <Box mb={1} px={{ xs: 2, sm: 0 }}>
            {loadingError ? (
              <Alert severity="warning">
                {t('feedForYou.errorOnLoadingTryAgainLater')}
              </Alert>
            ) : (
              <Alert severity="info">
                {t('feedForYou.thisPageDisplaysItemsAccordingToYourFilters')}
              </Alert>
            )}
          </Box>
        )}
        <LoaderWrapper isLoading={isLoading}>
          <EntityList
            entities={entities.results}
            emptyMessage={isLoading ? '' : t('entityList.noItems')}
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

export default FeedForYou;
