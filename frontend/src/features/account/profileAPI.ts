import { AccountsService } from '../../services/openapi';
import { OpenAPI } from '../../services/openapi/core/OpenAPI';

const api_url = process.env.REACT_APP_API_URL;

export const changeUsername = (access_token: string, username: string) => {
  OpenAPI.TOKEN = access_token;
  OpenAPI.BASE = api_url ?? '';
  return AccountsService.accountsProfilePartialUpdate({
    username,
  });
};
