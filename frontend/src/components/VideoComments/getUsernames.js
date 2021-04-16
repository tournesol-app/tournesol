import { TournesolAPI } from '../../api';

function convert({ username }) {
  return { text: username, value: username, url: `/user/${username}` };
}

export default function getUsernames(searchQuery, setAllUsernames) {
  const api = new TournesolAPI.UserInformationApi();
  api.userInformationSearchUsernameList(searchQuery, { limit: 10000 },
    (err, data) => {
      if (!err) {
        const newData = data.results.map(convert);
        setAllUsernames(newData);
      }
    });
}
