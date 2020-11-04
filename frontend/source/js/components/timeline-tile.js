import Post from './post.js';

function getNestedProperty(obj, ...args) {
  return args.reduce((obj, level) => obj && obj[level], obj)
}

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
    previewType: function() {
      if(this.entry.schema.startsWith('file.video')) {
        return 'video';
      }
      else if(this.entry.schema.startsWith('file.image') || this.entry.schema.startsWith('file.document.pdf')) {
        return 'image';
      }
      else if(this.entry.schema.startsWith('social.')) {
        return 'post';
      }
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
    </div>
  `
});