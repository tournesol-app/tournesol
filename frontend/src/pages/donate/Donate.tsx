import React from 'react';

import Typography from '@material-ui/core/Typography';

const DonatePage = () => {
  return (
    <div
      style={{
        marginTop: 24,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <div
        style={{
          maxWidth: '100%',
          width: 640,
          color: '#4A473E',
          padding: 24,
        }}
      >
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

        <form
          action="https://www.paypal.com/donate"
          method="post"
          target="_top"
          style={{
            marginTop: 24,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <input type="hidden" name="hosted_button_id" value="22T84YR7TZ762" />
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
  );
};

export default DonatePage;
