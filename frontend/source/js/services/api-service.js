import config from './../config.js';

export default class {
  static getApiBase() {
    return `https://${config.domain}/api`;
  }

  static fetchJsonWithToken(absoluteUrl, options, accessToken) {
    if(!accessToken){
      throw new Error("fetchJsonWithToken called without an access token");
    }
    options.headers = options.headers || {};
    options.headers.Authorization = `Bearer ${accessToken}`;
    return fetch(absoluteUrl, options)
      .then(response => response.ok ? response.json() : Promise.reject(response));
  }
}