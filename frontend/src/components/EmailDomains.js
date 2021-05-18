import React from 'react';

import { TournesolAPI } from '../api';

export default () => {
  const [requested, setRequested] = React.useState(false);
  const [acceptedDomains, setAcceptedDomains] = React.useState([]);
  const [rejectedDomains, setRejectedDomains] = React.useState([]);
  const [pendingDomains, setPendingDomains] = React.useState([]);

  if (!requested) {
    setRequested(true);
    const api = new TournesolAPI.EmailDomainApi();
    api.emailDomainList({ limit: 100, status: 'ACK' }, (err, data) => {
      if (!err) setAcceptedDomains(data.results);
    });
    api.emailDomainList({ limit: 100, status: 'RJ' }, (err, data) => {
      if (!err) setRejectedDomains(data.results);
    });
    api.emailDomainList({ limit: 100, status: 'PD' }, (err, data) => {
      if (!err) setPendingDomains(data.results);
    });
  }

  const formatDomain = (domain) => (
    <a className="domain_link_class" href={`http://${domain.domain.substring(1)}`}>
      {domain.domain}
    </a>);
  const listDomains = (lst) => lst.length > 0 && lst.map((domain) => (
    <li>{formatDomain(domain)}</li>));

  return (
    <div id="domains">
      <h1>Tournesol domains certification</h1>

      <p>Accepted domains</p>
      <ul className="accepted_domains_class">
        {listDomains(acceptedDomains)}
      </ul>
    </div>
  );
};
