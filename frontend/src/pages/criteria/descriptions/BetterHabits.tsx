import React from 'react';
import { Trans } from 'react-i18next';

const BetterHabitsDesc = () => (
  <Trans i18nKey="criteriaDescriptions.better_habits">
    <em>
      Does it make people adopt habits that benefit themselves and beyond?
    </em>
    <p>
      This criterion aims to highlight content that nudges viewers towards
      better habits, for themselves or for society. These habits may include
      healthier habits, in terms of food, sport activities or mental health, or
      more careful thinking when consuming informational contents. They may also
      include more altruistic habits, such as being kinder to others (including
      on the Internet), reducing our carbon footprint and being wary of our
      overconfidence. Evidently, contents that do not promote better habits
      should be given lower ratings, while contents that promote poor habits,
      purposely or not, should be given very low ratings.
    </p>
    <p>
      Contents that score high on &quot;encourages better habits&quot; should be
      successful at motivating viewers to grow and improve themselves.
    </p>
  </Trans>
);

export default BetterHabitsDesc;
