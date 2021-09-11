import { RequestStatus } from './../models/requests.js';
import ArchiveService from './../services/archive-service.js';

export default {
  namespaced: true,
  state: {
    archives: [],
    archivesRequestStatus: RequestStatus.NONE,
    archivesRequestPromise: null,
  },
  mutations: {
    SET_ARCHIVES(state, archives) {
      state.archives = archives;
    },
    ADD_ARCHIVE(state, archive) {
      state.archives.push(archive);
    },
    DELETE_ARCHIVE(state, archive) {
      state.archives = state.archives.filter(a => a !== archive);
    },
    UPDATE_ARCHIVE(state, archive) {
      Object.assign(state.archives.find(a => a.key === archive.key), archive);
    },
    SET_ARCHIVES_REQUEST_PROMISE(state, promise) {
      state.archivesRequestPromise = promise;
    },
    ARCHIVES_REQUEST_SUCCESS(state) {
      state.archivesRequestStatus = RequestStatus.SUCCESS;
    },
    ARCHIVES_REQUEST_PENDING(state) {
      state.archivesRequestStatus = RequestStatus.PENDING;
    },
    ARCHIVES_REQUEST_FAILURE(state) {
      state.archivesRequestStatus = RequestStatus.FAILURE;
    },
  },
  actions: {
    async getArchives(context, forceRefresh=false) {
      if (context.state.archivesRequestStatus === RequestStatus.NONE || forceRefresh) {
        context.commit('ARCHIVES_REQUEST_PENDING');
        const archivesRequestPromise = ArchiveService.getArchives()
          .then(archives => {
            context.commit('SET_ARCHIVES', archives);
            context.commit('ARCHIVES_REQUEST_SUCCESS');
            return context.state.archives;
          })
          .catch(err => {
            context.commit('SET_ARCHIVES', []);
            context.commit('ARCHIVES_REQUEST_FAILURE');
            return context.state.archives;
          });
        context.commit('SET_ARCHIVES_REQUEST_PROMISE', archivesRequestPromise);
        return archivesRequestPromise;
      }
      return context.state.archivesRequestPromise;
    },
    async updateArchive(context, {archive, newFiles}) {
      return ArchiveService.updateArchive(archive, newFiles)
        .then((updatedArchive) => {
          context.commit('UPDATE_ARCHIVE', updatedArchive);
          return context.state.archives;
        })
        .catch(err => {
          return context.state.archives;
        });
    },
    async deleteArchive(context, archive) {
      return ArchiveService.deleteArchive(archive)
        .then(() => {
          context.commit('DELETE_ARCHIVE', archive);
          return context.state.archives;
        })
        .catch(err => {
          return context.state.archives;
        });
    }
  }
};