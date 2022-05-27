import ApiService from './api-service.js';
import config from './../config.js';

export function generateRandomString() {
  const array = new Uint32Array(28);
  window.crypto.getRandomValues(array);
  return Array.from(array, dec => ('0' + dec.toString(16)).substr(-2)).join('');
}

function base64UrlEncode(string) {
  return btoa(String.fromCharCode.apply(null, new Uint8Array(string)))
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

export default class AuthService extends ApiService {
  static async getAuthorizationCodeUrl(codeVerifier) {
    const codeChallenge = await AuthService.pkceChallengeFromVerifier(codeVerifier);

    const authorizationCodeUrl = new URL(AuthService.getApiBase() + '/oauth/authorize/');
    authorizationCodeUrl.search = new URLSearchParams({
      approval_prompt: 'auto',
      response_type: 'code',
      redirect_uri: `https://${window.location.hostname}/oauth-redirect`,
      client_id: config.clientId,
      code_challenge: codeChallenge,
      code_challenge_method: 'S256',
    });

    return authorizationCodeUrl;
  }

  static async getToken(authorizationCode, codeVerifier) {
    const tokenUrl = AuthService.getApiBase() + '/oauth/token/';
    const bodyParams = new URLSearchParams({
      grant_type: 'authorization_code',
      code: authorizationCode,
      client_id: config.clientId,
      code_verifier: codeVerifier,
    });

    return fetch(tokenUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: bodyParams.toString(),
    }).then(response => response.json());
  }

  static async pkceChallengeFromVerifier(codeVerifier) {
    const encoder = new TextEncoder();
    const sha256Verifier = await window.crypto.subtle.digest('SHA-256', encoder.encode(codeVerifier));
    const encodedVerifier = btoa(String.fromCharCode.apply(null, new Uint8Array(sha256Verifier)))
      .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    return encodedVerifier;
  }
}