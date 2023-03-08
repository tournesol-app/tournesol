import React from 'react';
import { Trans } from 'react-i18next';

const LargelyRecommendedDesc = () => (
  <Trans i18nKey="criteriaDescriptions.largely_recommended">
    <strong>This is the default quality criterion of Tournesol 🌻.</strong>
    <p>
      It aims to measure the extent to which a content should be recommended to
      a very wide audience, according to the contributor&apos;s judgment.
    </p>
    <p>
      The main motivation for making this the single default quality criterion
      is that it highlights the core of Tournesol&apos;s mission. Namely,
      Tournesol aims to identify contents worth promoting at scale.
    </p>
    <p>
      A secondary motivation is to make it as contributor-friendly as possible,
      especially for new contributors.
    </p>
    <p>
      A third motivation is to use this quality criterion to infer the
      importance assigned by the contributors the the other quality criteria. In
      particular, we plan to soon learn how to best combine the different
      optional quality criteria (and the default one) into a more reliable
      unique global Tournesol score per video.
    </p>
  </Trans>
);

export default LargelyRecommendedDesc;
