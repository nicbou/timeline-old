import ImagePreview from './previews/image.js';
import VideoPreview from './previews/video.js';

export default Vue.component('preview', {
  props: ['entry'],
  computed: {
    mimetype: function(){
      if (this.entry.extra_attributes) {
        return this.entry.extra_attributes.mimetype;
      }
      return undefined;
    },
    imageSrcSet: function() {
        return `${this.entry.extra_attributes.previews.preview} 1x, ${this.entry.extra_attributes.previews.preview2x} 2x`;
    },
    previewType: function() {
      const s = this.entry.schema;
      if (s.startsWith('file.image') || s.startsWith('file.document.pdf')) {
        return 'image-preview';
      }
      else if(s.startsWith('file.video')) {
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