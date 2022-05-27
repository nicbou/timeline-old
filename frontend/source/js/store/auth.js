import { RequestStatus } from './../models/requests.js';
import { filters } from './../models/filters.js';
import AuthService from './../services/auth-service.js';

export default {
  namespaced: true,
  state: {
    accessToken: sessionStorage.getItem('accessToken'),
    codeVerifier: sessionStorage.getItem('codeVerifier'),
  },
  mutations: {
    setAccessToken: function (state, accessToken) {
      state.accessToken = accessToken;
      sessionStorage.setItem('accessToken', accessToken);
    },
    setCodeVerifier: function (state, codeVerifier) {
      state.codeVerifier = codeVerifier;
      sessionStorage.setItem('codeVerifier', codeVerifier);
    },
  },
  actions: {
    async getAuthorizationCodeUrl(context) {
      const codeVerifier = AuthService.generateRandomString()
      context.commit('setCodeVerifier', codeVerifier);
      return await AuthService.getAuthorizationCodeUrl(codeVerifier);
    },
    async getToken(context, authorizationCode) {
      const { access_token } = await AuthService.getToken(authorizationCode, context.state.codeVerifier);
      context.commit('setAccessToken', access_token);
      context.commit('setCodeVerifier', null);
    },
  }
};