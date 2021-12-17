const apiBase = `https://${window.location.hostname}/api/source/`;

export const sourceTypes = {
  filesystem: 'Filesystem',
  hackernews: 'Hacker News',
  reddit: 'Reddit',
  rss: 'RSS',
  rsync: 'Rsync',
  trakt: 'Trakt',
  twitter: 'Twitter',
};

function sourceToFormData(source, files) {
  const formData = new FormData();
  formData.append('key', source.key);
  formData.append('description', source.description);
  for (var i = 0; i < files.length; i++) {
    formData.append('source_files', files[i], files[i].name);
  }
  return formData;
}

export default class {
  static async getSources() {
    // Fetch sources from multiple endpoints. Return a list of sources of all types.
    const sourceEndpointsByType = await this.getSourceEndpoints();
    const allSources = [];
    for (const [sourceType, sourcesOfTypeUrl] of Object.entries(sourceEndpointsByType)) {
      const sourcesOfTypeResponse = await fetch(sourcesOfTypeUrl);
      const sourcesOfType = await sourcesOfTypeResponse.json();
      sourcesOfType.forEach(source => source.type = sourceType);
      allSources.push(...sourcesOfType);
    }

    return allSources;
  }

  static async getSourceEndpoints() {
    const sourceEndpointsByType = await fetch(new URL('', apiBase)).then(response => response.json());
    delete sourceEndpointsByType.sourcefile;
    return sourceEndpointsByType;
  }

  static async createSource(source, files) {
    return fetch(new URL(`${source.type}/`, apiBase), {
      method: 'POST',
      body: sourceToFormData(source, files),
    }).then(response => response.json()).then(createdSource => {
      createdSource.type = source.type;
      return createdSource;
    });
  }

  static async updateSource(source, newFiles) {
    return fetch(source.url, {
      method: 'PUT',
      body: sourceToFormData(source, newFiles),
    }).then(response => response.json()).then(updatedSource => {
      updatedSource.type = source.type;
      return updatedSource;
    });
  }

  static async deleteSource(source) {
    return fetch(source.url, { method: 'DELETE' });
  }

  static async deleteSourceFile(fileId) {
    return fetch(new URL(`sourcefile/${fileId}/`, apiBase), { method: 'DELETE' });
  }
}