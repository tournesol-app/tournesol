import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Button,
  IconButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  MenuList,
  Typography,
} from '@mui/material';
import { Delete, MoreVert } from '@mui/icons-material';

import DialogBox from 'src/components/DialogBox';
import { useCurrentPoll, useNotifications } from 'src/hooks';
import { UsersService } from 'src/services/openapi';

interface ComparisonActionBarProps {
  uidA: string | null;
  uidB: string | null;
  afterDeletion: () => void;
}

const ComparisonActionBar = ({
  uidA,
  uidB,
  afterDeletion,
}: ComparisonActionBarProps) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const { displayErrorsFrom, showSuccessAlert } = useNotifications();

  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const menuOpen = Boolean(menuAnchorEl);
  const [confirmDeletetionDialog, setConfirmDeletetionDialog] = useState(false);

  const openMenu = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const closeMenu = () => {
    setMenuAnchorEl(null);
  };

  const openConfirmDeletionDialog = () => {
    setConfirmDeletetionDialog(true);
  };

  const closeConfirmDeletionDialog = () => {
    setConfirmDeletetionDialog(false);
  };

  const deleteComparison = async () => {
    if (!uidA || !uidB) {
      return;
    }

    await UsersService.usersMeComparisonsDestroy({
      pollName: pollName,
      uidA: uidA,
      uidB: uidB,
    });
  };

  const onDeletionConfirmed = async () => {
    try {
      await deleteComparison();
      showSuccessAlert(t('comparisonActionBar.comparisonDeleted'));
      afterDeletion();
    } catch (error) {
      displayErrorsFrom(
        error,
        t('comparisonActionBar.errorOccurredCannotDeleteComparison'),
        [
          {
            status: 404,
            variant: 'warning',
            msg: t('comparisonActionBar.youHaventComparedTheseItemsYet'),
          },
        ]
      );
    } finally {
      closeConfirmDeletionDialog();
      closeMenu();
    }
  };

  return (
    <Box>
      <IconButton
        aria-label="more"
        id="comparison-actions"
        aria-controls={menuOpen ? 'comparison-footer-menu' : undefined}
        aria-expanded={menuOpen ? 'true' : undefined}
        aria-haspopup="true"
        onClick={openMenu}
      >
        <MoreVert />
      </IconButton>
      <Menu
        id="comparison-footer-menu"
        anchorEl={menuAnchorEl}
        open={menuOpen}
        onClose={closeMenu}
        MenuListProps={{
          'aria-labelledby': 'comparison-actions',
        }}
      >
        <MenuList dense sx={{ py: 0 }}>
          <MenuItem
            onClick={openConfirmDeletionDialog}
            disabled={!uidA || !uidB}
          >
            <ListItemIcon>
              <Delete />
            </ListItemIcon>
            <ListItemText>
              {t('comparisonActionBar.deleteComparison')}
            </ListItemText>
          </MenuItem>
        </MenuList>
      </Menu>
      <DialogBox
        open={confirmDeletetionDialog}
        onClose={closeConfirmDeletionDialog}
        mainActionColor="error"
        mainActionCallback={onDeletionConfirmed}
        title={t('comparisonActionBar.areYouSure')}
        content={
          <Typography paragraph>
            {t('comparisonActionBar.theScoresGivenToTheCriteriaWillBeDeleted')}
          </Typography>
        }
        additionalActionButton={
          <Button
            color="secondary"
            variant="outlined"
            onClick={() => {
              closeConfirmDeletionDialog();
              closeMenu();
            }}
          >
            {t('comparisonActionBar.back')}
          </Button>
        }
      />
    </Box>
  );
};

export default ComparisonActionBar;
