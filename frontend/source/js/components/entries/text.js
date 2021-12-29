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
    <article class="post text">
      <header>
        <span class="post-icon">
          <i class="fas fa-file-alt"></i>
        </span>
        <span class="post-title">
          {{ fileName }}
        </span>
      </header>
      <main v-html="richDescription"></main>
    </article>
  `
});