import React, { useState } from 'react';

import { useHistory } from 'react-router-dom';
import { TextField, Typography, Button } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

import { UsersService } from 'src/services/openapi';
import { useLoginState } from 'src/hooks';

const useStyles = makeStyles((theme) => ({
  buttonDanger: {
    backgroundColor: theme.palette.error.main,
    color: theme.palette.error.contrastText,
    '&:hover': {
      backgroundColor: theme.palette.error.dark,
    },
  },
  inputDanger: { width: '100%', margin: '8px 0px 8px 0px' },
}));

const DELETE_ACCOUNT_KEYWORD = 'delete account';

const DeleteAccountForm = () => {
  const classes = useStyles();
  const [keyword, setKeyword] = useState('');
  const { logout } = useLoginState();

  const history = useHistory();

  const deleteAccount = async () => {
    await UsersService.usersMeDestroy();
    logout();
    history.push('/');
  };

  return (
    <>
      <Typography>
        Please type the words <b>{DELETE_ACCOUNT_KEYWORD}</b> in the text box
        below to enable deleting your account.
      </Typography>
      <TextField
        size="small"
        variant="outlined"
        color="secondary"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        className={classes.inputDanger}
      />
      <Button
        disabled={keyword !== DELETE_ACCOUNT_KEYWORD}
        className={classes.buttonDanger}
        onClick={deleteAccount}
        fullWidth
        variant="contained"
      >
        Delete your account
      </Button>
    </>
  );
};

export default DeleteAccountForm;
