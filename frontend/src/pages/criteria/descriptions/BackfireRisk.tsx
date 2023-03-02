import React from 'react';
import { Trans } from 'react-i18next';

const BackfireRiskDesc = () => (
  <Trans i18nKey="criteriaDescriptions.backfire_risk">
    <em>
      Is it adapted to viewers with opposing beliefs? Does it prevent
      misconceptions or undesirable reactions?
    </em>
    <p>
      This criterion aims to measure the probability that a user may
      misunderstand or negatively react to the information presented. This may
      be particularly likely to occur for contents presented with a strong
      &quot;us versus them&quot; atmosphere on controversial topics
      <sup>
        (<a href="https://www.pnas.org/content/115/37/9216">BailABBC+-18</a>)
      </sup>
      . Note, however, that this{' '}
      <a href="https://tournesol.app/entities/yt:eVtCO84MDj8">
        Veritasium video
      </a>{' '}
      (based on his{' '}
      <a href="http://www.physics.usyd.edu.au/super/theses/PhD(Muller).pdf">
        PhD thesis
      </a>
      ) shows that backfiring also occurs for clean presentation of a
      counter-intuitive scientific concept, if the content does not pinpoint the
      risks of misunderstandings.
    </p>
    <p>
      Contents that score high on &quot;resilience to backfiring risks&quot;
      should be safe to recommend to all sorts of viewers, with limited risks of
      misunderstandings.
    </p>
  </Trans>
);

export default BackfireRiskDesc;
