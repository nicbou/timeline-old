import Post from './post.js';

export default Vue.component('tile', {
  props: ['entry'],
  computed: {
    tileStyle: function() {
      if(this.entry.extra_attributes.width && this.entry.extra_attributes.height) {
        return {
          width: `${this.entry.extra_attributes.width / this.entry.extra_attributes.height * 200}px`,
        }
      }
    },
    isVideo: function() {
      return this.entry.schema.startsWith('file.video');
    },
    previewType: function() {
      if(this.isVideo) {
        return 'video';
      }
      else if(this.entry.schema.startsWith('file.image') || this.entry.schema.startsWith('file.document.pdf')) {
        return 'image';
      }
      else if(this.entry.schema.startsWith('social.')) {
        return 'post';
      }
    },
    hasGeolocation: function() {
      return !!this.entry.extra_attributes.location;
    },
    imageSrcSet: function() {
      return `${this.entry.extra_attributes.previews.thumbnail} 1x, ${this.entry.extra_attributes.previews.thumbnail2x} 2x`;
    }
  },
  methods: {
    videoHoverStart: function() {
      this.$refs.videoElement.play()
    },
    videoHoverEnd: function() {
      this.$refs.videoElement.pause()
      this.$refs.videoElement.currentTime = 0;
    },
  },
  template: `
    <div class="tile" v-if="previewType" :style="tileStyle" :class="previewType">
      <img
        @click="$emit('click', entry)"
        v-if="previewType === 'image'"
        loading="lazy"
        :alt="entry.title"
        :src="entry.extra_attributes.previews.thumbnail"
        :srcset="imageSrcSet"
        />
      <video
        @click="$emit('click', entry)"
        :alt="entry.title"
        :src="entry.extra_attributes.previews.thumbnail"
        @mouseleave="videoHoverEnd"
        @mouseover="videoHoverStart"
        loop
        ref="videoElement"
        v-if="previewType === 'video'"/>
      <post :entry="entry" v-if="previewType === 'post'"></post>
      <div class="tile-icons">
        <i v-if="hasGeolocation" class="fas fa-map-marker-alt"></i>
        <i v-if="isVideo" class="fas fa-play-circle"></i>
      </div>
    </div>
  `
});