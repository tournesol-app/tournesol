import { AccountsService } from '../../services/openapi';
import { OpenAPI } from '../../services/openapi/core/OpenAPI';

const api_url = process.env.REACT_APP_API_URL;

export const changePassword = (
  access_token: string,
  old_password: string,
  password: string,
  password_confirm: string
) => {
  OpenAPI.TOKEN = access_token;
  OpenAPI.BASE = api_url ?? '';
  return AccountsService.accountsChangePasswordCreate({
    old_password,
    password,
    password_confirm,
  });
};
