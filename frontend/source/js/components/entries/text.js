export default Vue.component('text-entry', {
  props: ['entry'],
  computed: {
    fileName: function() {
      const pathParts = this.entry.extra_attributes.file.path.split('/');
      return pathParts[pathParts.length - 1];
    },
    richDescription: function() {
      if (this.entry.extra_attributes.file.mimetype === 'text/markdown'){
        return marked(this.entry.description);
      }
      return '<p>' + this.entry.description.replaceAll('\n', '</p><p>') + '</p>';
    },
  },
  template: `
    <div>
      <i class="icon fas fa-file-alt" :class="iconClass" :title="new Date(entry.date_on_timeline).toLocaleString()"></i>
      <div class="meta">{{ fileName }}</div>
      <div class="content" v-html="richDescription"></div>
    </div>
  `
});