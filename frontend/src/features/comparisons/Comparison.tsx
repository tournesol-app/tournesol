import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Redirect, useHistory, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { CircularProgress, Grid, Typography, Card } from '@mui/material';

import { useNotifications } from 'src/hooks';
import { UsersService, ComparisonRequest } from 'src/services/openapi';
import ComparisonSliders from 'src/features/comparisons/ComparisonSliders';
import EntitySelector, {
  SelectorValue,
} from 'src/features/entity_selector/EntitySelector';
import { getEntityName, UID_YT_NAMESPACE } from 'src/utils/constants';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import ComparisonHelper from './ComparisonHelper';

export const UID_PARAMS: { vidA: string; vidB: string } = {
  vidA: 'uidA',
  vidB: 'uidB',
};
const LEGACY_PARAMS: { vidA: string; vidB: string } = {
  vidA: 'videoA',
  vidB: 'videoB',
};

/**
 * Return an URLSearchParams without legacy parameters.
 */
const rewriteLegacyParameters = (
  uidA: string,
  uidB: string,
  legacyA: string | null,
  legacyB: string | null,
  paramVidA: string,
  paramVidB: string
) => {
  const searchParams = new URLSearchParams();
  searchParams.append(paramVidA, uidA);
  searchParams.append(paramVidB, uidB);

  if (legacyA && uidA === '') {
    searchParams.delete(paramVidA);
    searchParams.append(paramVidA, UID_YT_NAMESPACE + legacyA);
  }

  if (legacyB && uidB === '') {
    searchParams.delete(paramVidB);
    searchParams.append(paramVidB, UID_YT_NAMESPACE + legacyB);
  }

  return searchParams;
};

interface Props {
  afterSubmitCallback?: (
    uidA: string,
    uidB: string
  ) => { uid: string; refreshLeft: boolean };
}

/**
 * The comparison UI.
 *
 * Containing two entity selectors and the criteria sliders. Note that it
 * currently uses the `useLocation` hook to update the URL parameters when
 * a entity uid is changed. Adding this component into a page will also add
 * these uids in the URL parameters.
 */
const Comparison = ({ afterSubmitCallback }: Props) => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();
  const { showSuccessAlert } = useNotifications();
  const { name: pollName } = useCurrentPoll();
  const [isLoading, setIsLoading] = useState(true);
  const [initialComparison, setInitialComparison] =
    useState<ComparisonRequest | null>(null);

  const searchParams = new URLSearchParams(location.search);
  const uidA: string = searchParams.get(UID_PARAMS.vidA) || '';
  const uidB: string = searchParams.get(UID_PARAMS.vidB) || '';

  // clean the URL by replacing legacy parameters by UIDs
  const legacyA = searchParams.get(LEGACY_PARAMS.vidA);
  const legacyB = searchParams.get(LEGACY_PARAMS.vidB);
  const newSearchParams = rewriteLegacyParameters(
    uidA,
    uidB,
    legacyA,
    legacyB,
    UID_PARAMS.vidA,
    UID_PARAMS.vidB
  );

  const [selectorA, setSelectorA] = useState<SelectorValue>({
    uid: uidA,
    rating: null,
  });
  const [selectorB, setSelectorB] = useState<SelectorValue>({
    uid: uidB,
    rating: null,
  });

  const onChange = useCallback(
    (uidKey: string) => (newValue: SelectorValue) => {
      // `window.location` is used here, to avoid memoizing the location
      // defined in component state, which could be obsolete and cause a
      // race condition when the 2 selectors are updated concurrently.
      const searchParams = new URLSearchParams(window.location.search);
      const uid = newValue.uid;

      if ((searchParams.get(uidKey) || '') !== uid) {
        searchParams.delete(uidKey);

        if (uid) {
          searchParams.append(uidKey, uid);
        }
        history.push({ search: searchParams.toString() });
      }
      if (uidKey === UID_PARAMS.vidA) {
        setSelectorA(newValue);
      } else if (uidKey === UID_PARAMS.vidB) {
        setSelectorB(newValue);
      }
    },
    [history]
  );

  const onChangeA = useMemo(() => onChange(UID_PARAMS.vidA), [onChange]);
  const onChangeB = useMemo(() => onChange(UID_PARAMS.vidB), [onChange]);

  useEffect(() => {
    setIsLoading(true);
    setInitialComparison(null);
    if (selectorA.uid !== uidA) {
      setSelectorA({ uid: uidA, rating: null });
    }
    if (selectorB.uid !== uidB) {
      setSelectorB({ uid: uidB, rating: null });
    }
    if (uidA && uidB)
      UsersService.usersMeComparisonsRetrieve({
        pollName,
        uidA,
        uidB,
      })
        .then((comparison) => {
          setInitialComparison(comparison);
          setIsLoading(false);
        })
        .catch((err) => {
          console.error(err);
          setInitialComparison(null);
          setIsLoading(false);
        });
  }, [pollName, uidA, uidB, selectorA.uid, selectorB.uid]);

  const onSubmitComparison = async (c: ComparisonRequest) => {
    if (initialComparison) {
      const { entity_a, entity_b, criteria_scores, duration_ms } = c;
      await UsersService.usersMeComparisonsUpdate({
        pollName,
        uidA: entity_a.uid,
        uidB: entity_b.uid,
        requestBody: { criteria_scores, duration_ms },
      });
    } else {
      await UsersService.usersMeComparisonsCreate({
        pollName,
        requestBody: c,
      });
      setInitialComparison(c);
    }

    if (afterSubmitCallback) {
      const suggestion = afterSubmitCallback(c.entity_a.uid, c.entity_b.uid);
      if (suggestion.uid) {
        if (suggestion.refreshLeft) {
          onChangeA({ uid: suggestion.uid, rating: null });
          setSelectorB((value) => ({ ...value, ratingIsExpired: true }));
        } else {
          onChangeB({ uid: suggestion.uid, rating: null });
          setSelectorA((value) => ({ ...value, ratingIsExpired: true }));
        }
      }
    } else {
      setSelectorA((value) => ({ ...value, ratingIsExpired: true }));
      setSelectorB((value) => ({ ...value, ratingIsExpired: true }));
    }

    showSuccessAlert(t('comparison.successfullySubmitted'));
  };

  // redirect the user if at least one legacy parameters has been used
  // existing UIDs always prevail
  if (legacyA != null || legacyB != null) {
    return (
      <Redirect
        to={{ pathname: location.pathname, search: newSearchParams.toString() }}
      />
    );
  }

  const entityName = getEntityName(t, pollName);

  return (
    <Grid
      container
      sx={{
        maxWidth: '880px',
        gap: '8px',
      }}
    >
      <Grid
        item
        xs
        component={Card}
        sx={{
          alignSelf: 'start',
        }}
      >
        <EntitySelector
          title={`${entityName} 1`}
          value={selectorA}
          onChange={onChangeA}
          otherUid={uidB}
        />
      </Grid>
      <Grid
        item
        xs
        component={Card}
        sx={{
          alignSelf: 'start',
        }}
      >
        <EntitySelector
          title={`${entityName} 2`}
          value={selectorB}
          onChange={onChangeB}
          otherUid={uidA}
        />
      </Grid>
      <Grid
        item
        xs={12}
        sx={{
          mt: 1,
          display: 'flex',
          alignItems: 'center',
          flexDirection: 'column',
          '&:empty': {
            display: 'none',
          },
        }}
        component={Card}
        elevation={2}
      >
        <ComparisonHelper />
      </Grid>
      <Grid
        item
        xs={12}
        sx={{
          marginTop: 2,
          display: 'flex',
          alignItems: 'center',
          flexDirection: 'column',
          py: 3,
        }}
        component={Card}
        elevation={2}
      >
        {selectorA.rating && selectorB.rating ? (
          isLoading ? (
            <CircularProgress />
          ) : (
            <ComparisonSliders
              submit={onSubmitComparison}
              initialComparison={initialComparison}
              uidA={uidA}
              uidB={uidB}
              isComparisonPublic={
                selectorA.rating.is_public && selectorB.rating.is_public
              }
            />
          )
        ) : (
          <Typography>{t('comparison.pleaseSelectTwoItems')}</Typography>
        )}
      </Grid>
    </Grid>
  );
};

export default Comparison;
