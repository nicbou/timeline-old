import ApiService from './api-service.js';

export default class ApiObjectService extends ApiService {
  static objectToFormData(object, attachedFiles) {
    throw new Exception('objectToFormData is not implemented');
  }

  static async get(accessToken) {
    // Fetch objects from multiple endpoints. Return a list of objects of all types.
    const objectEndpointsByType = await this.getEndpoints(accessToken);
    const allObjects = [];
    for (const [objectType, objectsOfTypeUrl] of Object.entries(objectEndpointsByType)) {
      const objectsOfType = await this.fetchJsonWithToken(objectsOfTypeUrl, {}, accessToken);
      objectsOfType.forEach(object => object.type = objectType);
      allObjects.push(...objectsOfType);
    }

    return allObjects;
  }

  static getEndpoints(accessToken) {
    return this.fetchJsonWithToken(this.getApiBase() + '/', {}, accessToken);
  }

  static create(object, fileAttachments, accessToken) {
    return this.fetchJsonWithToken(
      this.getApiBase() + `/${object.type}/`,
      {
        method: 'POST',
        body: this.objectToFormData(object, fileAttachments),
      },
      accessToken
    ).then(createdObject => {
      createdObject.type = object.type;
      return createdObject;
    });
  }

  static update(object, newFileAttachments, accessToken) {
    return this.fetchJsonWithToken(
      object.url,
      {
        method: 'PUT',
        body: this.objectToFormData(object, newFileAttachments),
      },
      accessToken
    ).then(updatedObject => {
      updatedObject.type = object.type;
      return updatedObject;
    });
  }

  static delete(object, accessToken) {
    return this.fetchJsonWithToken(
      object.url,
      { method: 'DELETE' },
      accessToken
    );
  }
}