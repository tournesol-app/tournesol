import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import linkifyStr from 'linkify-string';

import {
  Alert,
  AlertTitle,
  Box,
  Collapse,
  Divider,
  IconButton,
  SxProps,
  Typography,
} from '@mui/material';
import { KeyboardArrowDown, KeyboardArrowUp } from '@mui/icons-material';

import { InternalLink } from 'src/components';
import { EntityContext, OriginEnum } from 'src/services/openapi';
import {
  getCollapsedState,
  setCollapsedState,
} from 'src/utils/entityContexts/collapsed';

interface EntityContextBoxProps {
  uid: string;
  contexts: Array<EntityContext>;
  // If set, display the entity name before the contexts.
  entityName?: string;
  // If true the contexts can be collapsed.
  collapsible?: boolean;
  // Replace the default association disclaier.
  altAssociationDisclaimer?: React.ReactElement;
}

interface EntityContextListProps {
  uid: string;
  origin_?: OriginEnum;
  contexts: Array<EntityContext>;
  entityName?: string;
  collapsible?: boolean;
  diclaimer?: React.ReactElement;
}

interface EntityContextTextListProps {
  uid: string;
  origin_?: OriginEnum;
  contexts: Array<EntityContext>;
}

const EntityContextTextList = ({
  uid,
  origin_,
  contexts,
}: EntityContextTextListProps) => {
  const { t } = useTranslation();
  const linkifyOpts = { defaultProtocol: 'https', target: '_blank' };

  return (
    <>
      {contexts.map((context, idx) => {
        if (context.text) {
          const text = linkifyStr(context.text || '', linkifyOpts);
          return (
            <Box key={`context_${uid}_${origin_}_p${idx}`}>
              <Typography paragraph component="div">
                <Box
                  whiteSpace="pre-wrap"
                  dangerouslySetInnerHTML={{ __html: text }}
                />
              </Typography>
              {idx < contexts.length - 1 && <Divider sx={{ mb: 2 }} />}
            </Box>
          );
        }
      })}
      <Box display="flex" justifyContent="flex-end">
        <InternalLink to="/faq?scrollTo=are_recommendations_moderated_by_the_association">
          {t('entityContextTextList.whyThisMessage')}
        </InternalLink>
      </Box>
    </>
  );
};

const EntityContextList = ({
  uid,
  contexts,
  origin_,
  diclaimer,
  entityName,
  collapsible,
}: EntityContextListProps) => {
  const { t } = useTranslation();

  const [displayText, setDisplayText] = useState(
    collapsible ? !getCollapsedState(uid) : true
  );

  const toggleDisplayText = (previousState: boolean) => {
    setCollapsedState(uid, previousState);
    setDisplayText(!previousState);
  };

  const infos = contexts.filter((ctx) => !ctx.unsafe);
  const warnings = contexts.filter((ctx) => ctx.unsafe);

  const entityHasWarnings = warnings.length > 0;

  let alertSx: SxProps = {};

  if (entityHasWarnings) {
    alertSx = { border: '1px solid' };
  }

  return (
    <Alert
      id="entity-context"
      severity={entityHasWarnings ? 'warning' : 'info'}
      sx={{
        '.MuiAlert-message': { width: '100%' },
        ...alertSx,
      }}
    >
      <Box display="flex" justifyContent="space-between">
        <AlertTitle>
          {diclaimer ? (
            diclaimer
          ) : (
            <strong>
              {origin_ === OriginEnum.ASSOCIATION &&
                t('entityContext.theAssociationWouldLikeToGiveYouContext')}
            </strong>
          )}
        </AlertTitle>

        {collapsible && (
          <IconButton
            aria-label="Show context"
            onClick={() => {
              toggleDisplayText(displayText ? true : false);
            }}
          >
            {displayText ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
          </IconButton>
        )}
      </Box>

      <Collapse in={displayText}>
        {entityName && (
          <Typography paragraph variant="body2" fontStyle="italic">
            {t('entityContext.about')} « {entityName} »
          </Typography>
        )}
        <EntityContextTextList
          uid={uid}
          origin_={origin_}
          contexts={entityHasWarnings ? warnings : infos}
        />
      </Collapse>
    </Alert>
  );
};

const EntityContextBox = ({
  uid,
  contexts,
  entityName,
  altAssociationDisclaimer,
  collapsible = false,
}: EntityContextBoxProps) => {
  const associationContexts = contexts.filter(
    (ctx) => ctx.origin === OriginEnum.ASSOCIATION
  );

  return (
    <>
      {associationContexts.length > 0 && (
        <Box key={`contexts_${uid}_${OriginEnum.ASSOCIATION}`}>
          <EntityContextList
            uid={uid}
            origin_={OriginEnum.ASSOCIATION}
            contexts={associationContexts}
            diclaimer={altAssociationDisclaimer}
            entityName={entityName}
            collapsible={collapsible}
          />
        </Box>
      )}
    </>
  );
};

export default EntityContextBox;
