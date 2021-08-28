const apiBase = `https://${window.location.hostname}/api/archive/`;

export default class {
  async static getArchives() {
    // Fetch archives from multiple endpoints. Return a list of archives of all types.
    const archiveEndpointsByType = await fetch(new URL('', apiBase)).then(response => response.json());

    const allArchives = [];
    for (const [archiveType, archivesOfTypeUrl] of Object.entries(archiveEndpointsByType)) {
      const archivesOfTypeResponse = await fetch(archivesOfTypeUrl);
      const archivesOfType = await archivesOfTypeResponse.json();
      archivesOfType.forEach(archive => archive.type = archiveType);
      allArchives.push(...archivesOfType);
    }

    return allArchives;
  }
}