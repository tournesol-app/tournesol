import React from 'react';
import { Trans } from 'react-i18next';

const LaymanFriendlyDesc = () => (
  <Trans i18nKey="criteriaDescriptions.layman_friendly">
    <em>How understandable is it, without prior knowledge?</em>
    <p>
      This criterion aims to identify contents that would be suitable to those
      with very limited prior knowledge. When judging this feature, contributors
      are encouraged to reflect on the suitability of the content to their
      grandparents or to their 5-year-old nephew.
    </p>
    <p>
      Contents that score high on &quot;layman-friendly&quot; should be
      accessible to a very large audience.
    </p>
    <h3>Distinction with &quot;clear and pedagogical&quot;</h3>
    <p>
      An example of layman-friendly non-pedagogical video is a video discussing
      concepts in a very superficial way.
    </p>
    <p>
      An example of a very pedagogical video that may not be very
      layman-friendly is{' '}
      <a href="https://www.youtube.com/watch?v=X8jsijhllIA">
        this video by 3Blue1Brown
      </a>
      .
    </p>
  </Trans>
);

export default LaymanFriendlyDesc;
