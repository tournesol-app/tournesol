import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';

import { Box, Chip } from '@mui/material';

import { EntityContext, OriginEnum } from 'src/services/openapi';

export const EntityContextChip = ({
  uid,
  entityContexts,
}: {
  uid: string;
  entityContexts: EntityContext[];
}) => {
  const history = useHistory();
  const { t } = useTranslation();

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    history.push(`/entities/${uid}#entity-context`);
  };

  const unsafeContext = entityContexts.find(
    (context) => context.unsafe && context.origin === OriginEnum.ASSOCIATION
  );

  if (!unsafeContext) {
    return <></>;
  }

  return (
    <Box pr={1} display="flex" justifyContent="flex-end">
      <Chip
        size="small"
        color="warning"
        variant="outlined"
        label={t('entityContextChip.context')}
        onClick={handleClick}
      />
    </Box>
  );
};

export default EntityContextChip;
