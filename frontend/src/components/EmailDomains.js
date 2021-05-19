import React from 'react';

import { TournesolAPI } from '../api';

export default () => {
  const [requested, setRequested] = React.useState(false);
  const [acceptedDomains, setAcceptedDomains] = React.useState([]);

  if (!requested) {
    setRequested(true);
    const api = new TournesolAPI.EmailDomainApi();
    api.emailDomainList({ limit: 100, status: 'ACK' }, (err, data) => {
      if (!err) setAcceptedDomains(data.results);
    });
  }

  return (
    <div id="domains">
      <h1>Tournesol domains certification</h1>

      <p>Accepted domains</p>
      <ul className="accepted_domains_class">
        {acceptedDomains && acceptedDomains.map((domain) => (
          <li>
            <a className="domain_link_class" href={`http://${domain.domain.substring(1)}`}>
              {domain.domain}
            </a>
          </li>))}
      </ul>
    </div>
  );
};
