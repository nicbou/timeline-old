import ApiService from './api-service.js';

export default class extends ApiService {
  static objectToFormData(object, attachedFiles) {
    throw new Exception('objectToFormData is not implemented');
  }

  static async get(accessToken) {
    // Fetch objects from multiple endpoints. Return a list of objects of all types.
    const objectEndpointsByType = await this.getEndpoints(accessToken);
    const allObjects = [];
    for (const [objectType, objectsOfTypeUrl] of Object.entries(objectEndpointsByType)) {
      const objectsOfType = await this.fetchWithToken(objectsOfTypeUrl, {}, accessToken).then(response => response.json());
      objectsOfType.forEach(object => object.type = objectType);
      allObjects.push(...objectsOfType);
    }

    return allObjects;
  }

  static async getEndpoints(accessToken) {
    const objectEndpointsByType = await this.fetchWithToken(this.getApiBase() + '/', {}, accessToken).then(response => response.json());
    return objectEndpointsByType;
  }

  static async create(object, fileAttachments, accessToken) {
    return this.fetchWithToken(
      this.getApiBase() + `/${object.type}/`,
      {
        method: 'POST',
        body: this.objectToFormData(object, fileAttachments),
      },
      accessToken
    ).then(response => response.json()).then(createdObject => {
      createdObject.type = object.type;
      return createdObject;
    });
  }

  static async update(object, newFileAttachments, accessToken) {
    return this.fetchWithToken(
      object.url,
      {
        method: 'PUT',
        body: this.objectToFormData(object, newFileAttachments),
      },
      accessToken
    ).then(response => response.json()).then(updatedObject => {
      updatedObject.type = object.type;
      return updatedObject;
    });
  }

  static async delete(object, accessToken) {
    return this.fetchWithToken(
      object.url,
      { method: 'DELETE' },
      accessToken
    );
  }
}