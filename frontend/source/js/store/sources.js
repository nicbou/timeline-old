import { RequestStatus } from './../models/requests.js';
import SourceService from './../services/source-service.js';

export default {
  namespaced: true,
  state: {
    sources: [],
    sourcesRequestStatus: RequestStatus.NONE,
    sourcesRequestPromise: null,
  },
  mutations: {
    SET_SOURCES(state, sources) {
      state.sources = sources;
    },
    ADD_SOURCE(state, source) {
      state.sources.push(source);
    },
    DELETE_SOURCE(state, source) {
      state.sources = state.sources.filter(a => a !== source);
    },
    UPDATE_SOURCE(state, source) {
      Object.assign(state.sources.find(a => a.key === source.key), source);
    },
    SET_SOURCES_REQUEST_PROMISE(state, promise) {
      state.sourcesRequestPromise = promise;
    },
    SOURCES_REQUEST_SUCCESS(state) {
      state.sourcesRequestStatus = RequestStatus.SUCCESS;
    },
    SOURCES_REQUEST_PENDING(state) {
      state.sourcesRequestStatus = RequestStatus.PENDING;
    },
    SOURCES_REQUEST_FAILURE(state) {
      state.sourcesRequestStatus = RequestStatus.FAILURE;
    },
  },
  actions: {
    async getSources(context, forceRefresh=false) {
      if (context.state.sourcesRequestStatus === RequestStatus.NONE || forceRefresh) {
        context.commit('SOURCES_REQUEST_PENDING');
        const sourcesRequestPromise = SourceService.getSources()
          .then(sources => {
            context.commit('SET_SOURCES', sources);
            context.commit('SOURCES_REQUEST_SUCCESS');
            return context.state.sources;
          })
          .catch(err => {
            context.commit('SET_SOURCES', []);
            context.commit('SOURCES_REQUEST_FAILURE');
            return context.state.sources;
          });
        context.commit('SET_SOURCES_REQUEST_PROMISE', sourcesRequestPromise);
        return sourcesRequestPromise;
      }
      return context.state.sourcesRequestPromise;
    },
    async createSource(context, {source, files}) {
      return SourceService.createSource(source, files)
        .then((updatedSource) => {
          context.commit('ADD_SOURCE', updatedSource);
          return context.state.sources;
        })
        .catch(err => {
          return context.state.sources;
        });
    },
    async updateSource(context, {source, newFiles}) {
      return SourceService.updateSource(source, newFiles)
        .then((updatedSource) => {
          context.commit('UPDATE_SOURCE', updatedSource);
          return context.state.sources;
        })
        .catch(err => {
          return context.state.sources;
        });
    },
    async deleteSource(context, source) {
      return SourceService.deleteSource(source)
        .then(() => {
          context.commit('DELETE_SOURCE', source);
          return context.state.sources;
        })
        .catch(err => {
          return context.state.sources;
        });
    }
  }
};