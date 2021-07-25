import React from 'react';

import {
  TextField,
  Grid,
  Container,
  makeStyles,
  Button,
} from '@material-ui/core';
import { useAppSelector, useAppDispatch } from '../../app/hooks';
import { getComparisonsAsync, selectComparisons } from './comparisonsSlice';
import { selectLogin } from '../login/loginSlice';

const useStyles = makeStyles((theme: any) => ({
  content: {
    marginTop: '64px',
    padding: theme.spacing(3),
  },
}));

const Comparisons = () => {
  const classes = useStyles();
  const comparisons = useAppSelector(selectComparisons);
  const dispatch = useAppDispatch();
  const token = useAppSelector(selectLogin);

  return (
    <div className="Comparisons">
      <Container className={classes.content} maxWidth="xs">
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Grid container spacing={2}>
              <Grid
                item
                xs={12}
                onClick={() =>
                  dispatch(getComparisonsAsync(token.access_token))
                }
              >
                <Button color="secondary" fullWidth variant="contained">
                  Fetch Comparisons
                </Button>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  value={JSON.stringify(comparisons.value)}
                />
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Container>
    </div>
  );
};

export default Comparisons;
