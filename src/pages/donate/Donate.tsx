import React from 'react';

const DonatePage = () => {
  return (
    <div>
      <div
        style={{
          marginLeft: 64,
          maxWidth: 'calc(100% - 8px)',
          width: 600,
          color: '#4A473E',
        }}
      >
        <p>
          Tournesol aims to identify top videos of public utility by eliciting
          contributors&#39; judgements on content quality.
        </p>
        <p>
          Because we are a small team of mostly volunteers, the development of
          Tournesol is slower than we would like it to be. If you can, please
          consider helping us, through coding or through donations. Check-out
          our{' '}
          <a href="https://github.com/tournesol-app/tournesol">
            open source code
          </a>
          , or join our <a href="https://discord.gg/TvsFB8RNBV">Discord</a>.{' '}
        </p>

        <form
          action="https://www.paypal.com/donate"
          method="post"
          target="_top"
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
