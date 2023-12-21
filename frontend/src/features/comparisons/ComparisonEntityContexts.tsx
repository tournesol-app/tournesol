import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Grid, useTheme } from '@mui/material';

import EntityContextBox from 'src/features/entity_context/EntityContextBox';
import { SelectorValue } from 'src/features/entity_selector/EntitySelector';
import { useCurrentPoll } from 'src/hooks';
import { getEntityName } from 'src/utils/constants';

interface EntityContextBoxProps {
  selectorA: SelectorValue;
  selectorB: SelectorValue;
}

const ComparisonEntityContextsItem = ({
  selector,
  altAssociationDisclaimer,
}: {
  selector: SelectorValue;
  altAssociationDisclaimer?: React.ReactElement;
}) => {
  return (
    <>
      {selector.rating && selector.uid && selector.rating.entity_contexts && (
        <EntityContextBox
          uid={selector.uid}
          contexts={selector.rating.entity_contexts}
          entityName={selector.rating?.entity?.metadata?.name}
          altAssociationDisclaimer={altAssociationDisclaimer}
          collapsible={true}
        />
      )}
    </>
  );
};

const ComparisonEntityContexts = ({
  selectorA,
  selectorB,
}: EntityContextBoxProps) => {
  const theme = useTheme();

  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const entityName = getEntityName(t, pollName);

  return (
    <Grid
      container
      spacing={1}
      sx={{
        'span.primary': {
          color: theme.palette.secondary.main,
          fontWeight: 'bold',
          textTransform: 'capitalize',
        },
      }}
    >
      {selectorA.uid === selectorB.uid ? (
        <Grid item xs={12}>
          <ComparisonEntityContextsItem selector={selectorA} />
        </Grid>
      ) : (
        <>
          <Grid item xs={12} sm={12} md={6}>
            <ComparisonEntityContextsItem
              selector={selectorA}
              altAssociationDisclaimer={
                <strong>
                  <Trans
                    t={t}
                    i18nKey="entityContext.entityAtheAssociationWouldLikeToGiveYouContext"
                  >
                    <span className="primary">{{ entityName }} A</span> - The
                    Tournesol association would like to give you some context.
                  </Trans>
                </strong>
              }
            />
          </Grid>
          <Grid item xs={12} sm={12} md={6}>
            <ComparisonEntityContextsItem
              selector={selectorB}
              altAssociationDisclaimer={
                <strong>
                  <Trans
                    t={t}
                    i18nKey="entityContext.entityBtheAssociationWouldLikeToGiveYouContext"
                  >
                    <span className="primary">{{ entityName }} B</span> - The
                    Tournesol association would like to give you some context.
                  </Trans>
                </strong>
              }
            />
          </Grid>
        </>
      )}
    </Grid>
  );
};

export default ComparisonEntityContexts;
