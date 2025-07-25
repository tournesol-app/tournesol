import React from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import { Chip } from '@mui/material';

import { EntityContext, OriginEnum } from 'src/services/openapi';

export const EntityContextChip = ({
  uid,
  entityContexts,
}: {
  uid: string;
  entityContexts: EntityContext[];
}) => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    navigate(`/entities/${uid}#entity-context`);
  };

  const unsafeContext = entityContexts.find(
    (context) => context.unsafe && context.origin === OriginEnum.ASSOCIATION
  );

  if (unsafeContext == undefined) {
    return <></>;
  }

  return (
    <Chip
      size="small"
      color="warning"
      variant="outlined"
      label={t('entityContextChip.context')}
      onClick={handleClick}
      sx={{
        fontSize: '0.8125em',
      }}
    />
  );
};

export default EntityContextChip;
