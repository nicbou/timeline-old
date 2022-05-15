import ImagePreview from './previews/image.js';
import VideoPreview from './previews/video.js';
import { hasGeolocation } from './../utils/entries.js';

export default Vue.component('preview', {
  props: ['entry'],
  computed: {
    mimetype: function(){
      if (this.entry.extra_attributes && this.entry.extra_attributes.file) {
        return this.entry.extra_attributes.file.mimetype;
      }
      return undefined;
    },
    imageSrcSet: function() {
        return `${this.entry.extra_attributes.previews.preview} 1x, ${this.entry.extra_attributes.previews.preview2x} 2x`;
    },
    previewType: function() {
      if (this.mimetype.startsWith('image/') || this.mimetype === 'application/pdf') {
        return 'image-preview';
      }
      else if(this.mimetype.startsWith('video/')) {
        return 'video-preview';
      }
    },
  },
  methods: {
    hasGeolocation,
    close: function(event) {
      this.$emit('close');
    }
  },
  template: `
    <div class="preview modal content-with-sidebar">
      <div class="content">
        <button class="button close" @click="close" title="Close"><i class="fas fa-times"></i></button>
        <component :is="previewType" :entry="entry"></component>
      </div>
      <div class="sidebar">
        <dl>
          <div class="attribute" v-show="entry.title">
            <dt>Title</dt>
            <dd>{{ entry.title }}</dd>
          </div>
          <div class="attribute" v-show="entry.description">
            <dt>Description</dt>
            <dd>{{ entry.description }}</dd>
          </div>
          <div class="attribute">
            <dt>Source</dt>
            <dd>{{ entry.source }}</dd>
          </div>
          <div class="attribute">
            <dt>Type</dt>
            <dd>{{ entry.extra_attributes.file.mimetype }}</dd>
          </div>
          <div class="attribute">
            <dt>Path</dt>
            <dd>{{ entry.extra_attributes.file.path }}</dd>
          </div>
          <div class="attribute" v-if="hasGeolocation(entry)">
            <dt>Location</dt>
            <dd>
              <entry-map class="map" :entries="[entry]"></entry-map>
              <small>
                <i class="fas fa-map-marker-alt"></i>
                {{ entry.extra_attributes.location.latitude }}, {{ entry.extra_attributes.location.longitude }}
              </small>
            </dd>
          </div>
          <div class="attribute">
            <dt>Actions</dt>
            <dl>
              <div class="input-group vertical">
                <a v-if="entry.extra_attributes.file.path" class="button" title="Save this file to your device" :href="entry.extra_attributes.file.path" target="_blank">
                  <i class="fas fa-download"></i>
                  Show original
                </a>
                <a v-if="entry.extra_attributes.file.path" class="button" title="Save this file to your device" :href="entry.extra_attributes.file.path" download>
                  <i class="fas fa-download"></i>
                  Download
                </a>
              </div>
            </dl>
          </div>
        </dl>
      </div>
    </div>
  `
});