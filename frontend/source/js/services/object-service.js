export default class {
  static objectToFormData(object, attachedFiles) {
  }

  static getApiBase() {
    return `https://${window.location.hostname}/api/`;
  }

  static async get() {
    // Fetch objects from multiple endpoints. Return a list of objects of all types.
    const objectEndpointsByType = await this.getEndpoints();
    const allObjects = [];
    for (const [objectType, objectsOfTypeUrl] of Object.entries(objectEndpointsByType)) {
      const objectsOfType = await fetch(objectsOfTypeUrl).then(response => response.json());
      objectsOfType.forEach(object => object.type = objectType);
      allObjects.push(...objectsOfType);
    }

    return allObjects;
  }

  static async getEndpoints() {
    const objectEndpointsByType = await fetch(new URL('', this.getApiBase())).then(response => response.json());
    return objectEndpointsByType;
  }

  static async create(object, fileAttachments) {
    return fetch(new URL(`${object.type}/`, this.getApiBase()), {
      method: 'POST',
      body: objectToFormData(object, fileAttachments),
    }).then(response => response.json()).then(createdObject => {
      createdObject.type = object.type;
      return createdObject;
    });
  }

  static async update(object, newFileAttachments) {
    return fetch(object.url, {
      method: 'PUT',
      body: objectToFormData(object, newFileAttachments),
    }).then(response => response.json()).then(updatedObject => {
      updatedObject.type = object.type;
      return updatedObject;
    });
  }

  static async delete(object) {
    return fetch(object.url, { method: 'DELETE' });
  }
}