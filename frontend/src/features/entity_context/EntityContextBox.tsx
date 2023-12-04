import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import linkifyStr from 'linkify-string';

import {
  Alert,
  AlertTitle,
  Box,
  Divider,
  Link,
  SxProps,
  Typography,
} from '@mui/material';

import { EntityContext, OriginEnum } from 'src/services/openapi';

interface EntityContextBoxProps {
  uid: string;
  contexts: Array<EntityContext>;
}

interface EntityContextListProps {
  uid: string;
  origin_?: OriginEnum;
  contexts: Array<EntityContext>;
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
        <Link
          to="/faq?scrollTo=are_recommendations_moderated_by_the_association"
          component={RouterLink}
          sx={{
            color: 'inherit',
            textDecorationColor: 'inherit',
          }}
        >
          {t('entityContextTextList.whyThisMessage')}
        </Link>
      </Box>
    </>
  );
};

const EntityContextList = ({
  uid,
  contexts,
  origin_,
}: EntityContextListProps) => {
  const { t } = useTranslation();

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
      sx={alertSx}
    >
      <AlertTitle>
        <strong>
          {origin_ === OriginEnum.ASSOCIATION &&
            t('contextsFromOrigin.theAssociationWouldLikeToGiveYouContext')}
        </strong>
      </AlertTitle>

      <EntityContextTextList
        uid={uid}
        origin_={origin_}
        contexts={entityHasWarnings ? warnings : infos}
      />
    </Alert>
  );
};

const EntityContextBox = ({ uid, contexts }: EntityContextBoxProps) => {
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
          />
        </Box>
      )}
    </>
  );
};

export default EntityContextBox;
