import React from 'react';
import { Trans } from 'react-i18next';

import { ExternalLink } from 'src/components';

const PedagogyDesc = () => (
  <Trans i18nKey="criteriaDescriptions.pedagogy">
    <em>
      How efficiently does the content guide viewers in their understanding?
    </em>
    <p>
      This criterion aims to measure the clarity of the explanations of a
      content. More importantly, this{' '}
      <ExternalLink href="https://tournesol.app/entities/yt:GEmuEWjHr5c">
        Veritasium video
      </ExternalLink>{' '}
      argues that what really matters is what is going on in the viewer&apos;s
      head as they watch the video. A pedagogical content should thus accompany
      the viewers adequately along every challenging step of an argument or of
      the analysis of some data.
    </p>
    <p>
      Contents that score high on &quot;clear and pedagogical&quot; should help
      viewers understand all the elements that lead to a conclusion.
    </p>
  </Trans>
);

export default PedagogyDesc;
