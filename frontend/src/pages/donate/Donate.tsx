import React from 'react';

import { makeStyles } from '@material-ui/core';
import Typography from '@material-ui/core/Typography';

import { ContentHeader } from 'src/components';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  content: {
    maxWidth: '100%',
    width: 640,
    padding: 24,
  },
  box: {
    padding: 8,
    marginTop: 8,
    background: '#FFFFFF',
    border: '1px solid #DCD8CB',
    boxShadow:
      '0px 0px 8px rgba(0, 0, 0, 0.02), 0px 2px 4px rgba(0, 0, 0, 0.05)',
    borderRadius: '4px',
  },
});

const DonatePage = () => {
  const classes = useStyles();
  return (
    <>
      <ContentHeader title="Donate" />
      <div className={classes.root}>
        <div className={classes.content}>
          <Typography paragraph>
            Because we are a small team of mostly volunteers, the development of
            Tournesol is slower than we would like it to be. If you can, please
            consider helping us, through coding or through donations. Check-out
            our{' '}
            <a href="https://github.com/tournesol-app/tournesol">
              open source code
            </a>
            , or join our <a href="https://discord.gg/TvsFB8RNBV">Discord</a>.{' '}
          </Typography>

          <Typography variant="h4" gutterBottom style={{ fontStyle: 'italic' }}>
            How to make a donation?
          </Typography>
          <div className={classes.box}>
            <Typography variant="h6">By direct transfer</Typography>
            <pre>Association Tournesol</pre>
            <pre>Lausanne, Switzerland</pre>
            <pre>IBAN: CH42 0900 0000 1569 4102 5</pre>
            <pre>BIC: POFICHBEXXX</pre>
          </div>

          <div className={classes.box}>
            <Typography variant="h6">By Paypal</Typography>

            <form
              action="https://www.paypal.com/donate"
              method="post"
              target="_top"
              style={{ marginTop: 8 }}
            >
              <input
                type="hidden"
                name="hosted_button_id"
                value="22T84YR7TZ762"
              />
              <input
                type="image"
                src="https://www.paypalobjects.com/en_US/CH/i/btn/btn_donateCC_LG.gif"
                name="submit"
                title="PayPal - The safer, easier way to pay online!"
                alt="Donate with PayPal button"
              />
              <img
                alt=""
                src="https://www.paypal.com/en_CH/i/scr/pixel.gif"
                width="1"
                height="1"
              />
            </form>
          </div>
        </div>
      </div>
    </>
  );
};

export default DonatePage;
