import ImagePreview from './previews/image.js';
import VideoPreview from './previews/video.js';

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
    close: function(event) {
      this.$emit('close');
    }
  },
  template: `
    <div class="preview">
      <button class="button close" @click="close" title="Close"><i class="fas fa-times"></i></button>
      <component :is="previewType" :entry="entry"></component>
    </div>
  `
});