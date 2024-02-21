import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Location } from 'history';

import { CircularProgress, Grid, Typography, Card } from '@mui/material';

import { useNotifications } from 'src/hooks';
import {
  UsersService,
  ComparisonRequest,
  ApiError,
} from 'src/services/openapi';
import ComparisonSliders from 'src/features/comparisons/ComparisonSliders';
import EntitySelector, {
  SelectorValue,
} from 'src/features/entity_selector/EntitySelector';
import { UID_YT_NAMESPACE } from 'src/utils/constants';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import ComparisonEntityContexts from './ComparisonEntityContexts';
import ComparisonHelper from './ComparisonHelper';

export const UID_PARAMS: { vidA: string; vidB: string } = {
  vidA: 'uidA',
  vidB: 'uidB',
};
const LEGACY_PARAMS: { vidA: string; vidB: string } = {
  vidA: 'videoA',
  vidB: 'videoB',
};

const getUidsFromLocation = (location: Location) => {
  const searchParams = new URLSearchParams(location.search);
  let uidA = searchParams.get(UID_PARAMS.vidA);
  if (uidA === null) {
    const legacyA = searchParams.get(LEGACY_PARAMS.vidA);
    if (legacyA) {
      uidA = UID_YT_NAMESPACE + legacyA;
    }
  }
  let uidB = searchParams.get(UID_PARAMS.vidB);
  if (uidB === null) {
    const legacyB = searchParams.get(LEGACY_PARAMS.vidB);
    if (legacyB) {
      uidB = UID_YT_NAMESPACE + legacyB;
    }
  }
  return {
    uidA,
    uidB,
  };
};

interface Props {
  afterSubmitCallback?: (
    uidA: string,
    uidB: string
  ) => { uid: string; refreshLeft: boolean };
  autoFillSelectorA?: boolean;
  autoFillSelectorB?: boolean;
}

/**
 * The comparison UI.
 *
 * Containing two entity selectors and the criteria sliders. Note that it
 * currently uses the `useLocation` hook to update the URL parameters when
 * a entity uid is changed. Adding this component into a page will also add
 * these uids in the URL parameters.
 */
const Comparison = ({
  afterSubmitCallback,
  autoFillSelectorA = false,
  autoFillSelectorB = false,
}: Props) => {
  const { t, i18n } = useTranslation();
  const currentLang = i18n.resolvedLanguage;

  const history = useHistory();
  const location = useLocation();
  const { showSuccessAlert, displayErrorsFrom } = useNotifications();
  const { name: pollName } = useCurrentPoll();

  const [isLoading, setIsLoading] = useState(true);

  const [initialComparison, setInitialComparison] =
    useState<ComparisonRequest | null>(null);

  const { uidA, uidB } = getUidsFromLocation(location);

  const [selectorA, setSelectorA] = useState<SelectorValue>({
    uid: uidA,
    rating: null,
  });
  const [selectorB, setSelectorB] = useState<SelectorValue>({
    uid: uidB,
    rating: null,
  });

  const onChange = useCallback(
    (vidKey: 'vidA' | 'vidB') => (newValue: SelectorValue) => {
      // `window.location` is used here, to avoid memoizing the location
      // defined in component state, which could be obsolete and cause a
      // race condition when the 2 selectors are updated concurrently.
      const searchParams = new URLSearchParams(window.location.search);
      const uid = newValue.uid;

      const uidKey = UID_PARAMS[vidKey];
      if ((searchParams.get(uidKey) || '') !== uid) {
        searchParams.set(uidKey, uid || '');
        searchParams.delete(LEGACY_PARAMS[vidKey]);
        history.replace({ search: searchParams.toString() });
      }
      if (vidKey === 'vidA') {
        setSelectorA(newValue);
      } else if (vidKey === 'vidB') {
        setSelectorB(newValue);
      }
    },
    [history]
  );

  const onChangeA = useMemo(() => onChange('vidA'), [onChange]);
  const onChangeB = useMemo(() => onChange('vidB'), [onChange]);

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
        .catch(() => {
          setInitialComparison(null);
          setIsLoading(false);
        });
  }, [pollName, uidA, uidB, selectorA.uid, selectorB.uid]);

  /**
   * When the UI language changes, refresh the ratings to retrieve the
   * corresponding localized entity contexts.
   */
  useEffect(() => {
    if (isLoading) {
      return;
    }

    if (selectorA.uid) {
      setSelectorA((value) => ({ ...value, ratingIsExpired: true }));
    }

    if (selectorB.uid) {
      setSelectorB((value) => ({ ...value, ratingIsExpired: true }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentLang]);

  const onSubmitComparison = async (c: ComparisonRequest) => {
    try {
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
    } catch (e) {
      displayErrorsFrom(e as ApiError);
      throw e;
    }

    if (afterSubmitCallback) {
      const suggestion = afterSubmitCallback(c.entity_a.uid, c.entity_b.uid);

      // Do not update the selectors when receiving this message.
      if (suggestion.uid === '__UNMOUNTING_PARENT__') {
        return;
      }

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
        display="flex"
        flexDirection="column"
        alignSelf="stretch"
      >
        <EntitySelector
          title="A"
          alignment="left"
          value={selectorA}
          onChange={onChangeA}
          otherUid={uidB}
          autoFill={autoFillSelectorA}
        />
      </Grid>
      <Grid
        item
        xs
        component={Card}
        display="flex"
        flexDirection="column"
        alignSelf="stretch"
      >
        <EntitySelector
          title="B"
          alignment="right"
          value={selectorB}
          onChange={onChangeB}
          otherUid={uidA}
          autoFill={autoFillSelectorB}
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
      <Grid item xs={12}>
        <ComparisonEntityContexts selectorA={selectorA} selectorB={selectorB} />
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
              uidA={uidA || ''}
              uidB={uidB || ''}
              isComparisonPublic={
                selectorA.rating.individual_rating.is_public &&
                selectorB.rating.individual_rating.is_public
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
