import config from './../config.js';

export default class {
  static getApiBase() {
    return `https://${config.domain}/api`;
  }

  static fetchWithToken(absoluteUrl, options, accessToken) {
    if(!accessToken){
      throw new Error("fetchWithToken called without an access token");
    }
    options.headers = options.headers || {};
    options.headers.Authorization = `Bearer ${accessToken}`;
    return fetch(absoluteUrl, options);
  }
}